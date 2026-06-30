#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物种形成系统（Speciation System）

核心职责：
    1. 定期扫描生态系统中的所有生物实体
    2. 按 species_id 分组，计算各群体的平均基因型
    3. 检测群体内遗传分化程度，当某子群与原型的遗传距离超过阈值时，
       将其识别为新物种并自动注册预设模板
    4. 新物种获得独立的 species_id，后续繁殖将独立演化

物种形成模型（简化 Allopatric + Peripatric）：
    - 突变在每一代随机积累（由 GenomeComponent.mutate 完成）
    - SpeciationSystem 定期"采样"种群基因型分布
    - 当检测到明显的双峰/多峰分布时，将离群子集提升为新物种
    - 新物种注册到工厂预设表，使工厂可以继续基于该新物种创建实体

阈值参数：
    SPECIATION_DISTANCE_THRESHOLD : 遗传距离超过此值即视为新物种
    MIN_GROUP_SIZE                : 最小群体大小，避免单一个体形成新物种
    MAX_SPECIES_PER_SCAN          : 每次扫描最多识别的新物种数（防止爆发）
"""

import logging
import math
import random
from collections import defaultdict
from typing import Dict, List, Tuple

from core.system import System
from core.world import World

from biology.components.genome_component import GenomeComponent
from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent
from animal.components.animal_component import AnimalComponent
from plant.components.plant_component import PlantComponent

from biology.ecology.speciation_analyzer import SpeciationAnalyzer
from biology.ecology.speciation_registry import SpeciationRegistry
from biology.ecology.speciation_migrator import SpeciationMigrator
from core.sqrt_cache import cached_sqrt

logger = logging.getLogger(__name__)


class SpeciationSystem(System):
    tick_interval = 80
    """
    物种形成系统

    运行周期：每 80 步扫描一次（给种群足够时间积累变异）
    """

    # 物种形成遗传距离阈值（基因 strength 欧氏距离）
    SPECIATION_DISTANCE_THRESHOLD = 2.0

    # 最小群体大小（避免单一个体或极小群体形成新物种）
    MIN_GROUP_SIZE = 5

    # 每次扫描最多识别的新物种数
    MAX_SPECIES_PER_SCAN = 3

    # 全局物种序号计数器（用于扁平命名新物种）
    _global_species_counter: int = 0

    # 物种分裂冷却：物种标识 -> 上次分裂时的 tick_count
    _species_cooldown: Dict[str, int] = {}

    def __init__(self):
        super().__init__()
        self._analyzer = SpeciationAnalyzer(
            threshold=self.SPECIATION_DISTANCE_THRESHOLD,
            min_group_size=self.MIN_GROUP_SIZE,
        )
        self._registry = SpeciationRegistry()
        self._migrator = SpeciationMigrator()

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行物种形成扫描"""
        species_groups = self._group_by_species(world)
        if not species_groups:
            return

        current_tick = getattr(world, 'tick_count', 0)
        new_species_count = 0
        processed_species = set()

        for species_id, entities in species_groups.items():
            if species_id in processed_species:
                continue
            if not self._can_speciate(species_id, entities, current_tick):
                continue

            new_species = self._try_speciate(world, species_id, entities, current_tick)
            if new_species:
                new_species_count += 1
                processed_species.add(species_id)
                if new_species_count >= self.MAX_SPECIES_PER_SCAN:
                    break

        if new_species_count > 0:
            logger.info(f"[Speciation] 本次扫描共形成 {new_species_count} 个新物种")

    def _can_speciate(self, species_id: str, entities: List[int], current_tick: int) -> bool:
        """检查物种是否满足分化条件"""
        last_split = self._species_cooldown.get(species_id, 0)
        if current_tick - last_split < self.tick_interval * 2:
            return False
        if len(entities) < self.MIN_GROUP_SIZE * 2:
            return False
        return True

    def _try_speciate(self, world: World, species_id: str, entities: List[int], current_tick: int) -> str | None:
        """尝试让物种分化，返回新物种ID或None"""
        id_vectors = self._extract_gene_vectors(world, entities)
        if not id_vectors:
            return None

        outliers = self._analyzer.find_outlier_cluster(id_vectors)
        if not outliers:
            return None

        outlier_centroid = self._analyzer.compute_centroid([v for _, v in outliers])
        centroid = self._analyzer.compute_centroid([v for _, v in id_vectors])
        distance = self._analyzer.euclidean_distance(centroid, outlier_centroid)

        if distance < self.SPECIATION_DISTANCE_THRESHOLD:
            return None

        new_species_id = self._registry.register_new_species(
            species_id, outlier_centroid, entities, world,
            counter=self._global_species_counter,
        )
        if new_species_id:
            self._global_species_counter += 1
            logger.info(
                f"[Speciation] 新物种形成: '{species_id}' -> '{new_species_id}' "
                f"(距离={distance:.2f}, 群体={len(outliers)} 个体)"
            )
            self._migrator.migrate_entities_to_species(world, outliers, new_species_id)
            self._species_cooldown[species_id] = current_tick
            self._species_cooldown[new_species_id] = current_tick

        return new_species_id

    # -------------------------------------------------
    # 数据收集
    # -------------------------------------------------

    def _group_by_species(self, world: World) -> Dict[str, List[int]]:
        """按 species_id 将实体分组"""
        groups = defaultdict(list)
        for entity, (tracker,) in world.get_components(SpeciationTrackerComponent):
            if not world.has_entity(entity):
                continue
            groups[tracker.species_id].append(entity.id)
        return dict(groups)

    def _extract_gene_vectors(
        self, world: World, entity_ids: List[int]
    ) -> List[Tuple[int, List[float]]]:
        """
        将一组实体的基因组提取为统一维度的向量

        返回: [(entity_id, [strength1, strength2, ...]), ...]
        """
        # 先收集所有实体中出现的 expression_target，保证维度一致
        all_targets = set()
        genomes = {}

        for eid in entity_ids:
            entity = world.query_entity(eid)
            if entity is None:
                continue
            genome = world.get_component(entity, GenomeComponent)
            if genome is None or not genome.genes:
                continue
            genomes[eid] = genome
            for gene in genome.genes:
                all_targets.add(gene.expression_target)

        if not all_targets:
            return []

        sorted_targets = sorted(all_targets)

        vectors = []
        for eid, genome in genomes.items():
            # 建立 target -> 平均 strength 的映射
            target_values = defaultdict(list)
            for gene in genome.genes:
                target_values[gene.expression_target].append(gene.strength)

            vector = []
            for target in sorted_targets:
                values = target_values.get(target, [0.0])
                vector.append(sum(values) / len(values))

            vectors.append((eid, vector))

        return vectors
