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

        vectors = [v for _, v in id_vectors]
        centroid = self._compute_centroid(vectors)
        outliers = self._find_outlier_cluster(id_vectors, centroid)
        if not outliers:
            return None

        outlier_centroid = self._compute_centroid([v for _, v in outliers])
        distance = self._euclidean_distance(centroid, outlier_centroid)

        if distance < self.SPECIATION_DISTANCE_THRESHOLD:
            return None

        new_species_id = self._register_new_species(species_id, outlier_centroid, entities, world)
        if new_species_id:
            logger.info(
                f"[Speciation] 新物种形成: '{species_id}' → '{new_species_id}' "
                f"(距离={distance:.2f}, 群体={len(outliers)} 个体)"
            )
            self._migrate_entities_to_species(world, outliers, new_species_id)
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

    # -------------------------------------------------
    # 聚类分析
    # -------------------------------------------------

    def _compute_centroid(self, vectors: List[List[float]]) -> List[float]:
        """计算一组向量的中心点（各维度平均值）"""
        if not vectors:
            return []
        dim = len(vectors[0])
        centroid = []
        for i in range(dim):
            values = [v[i] for v in vectors]
            centroid.append(sum(values) / len(values))
        return centroid

    def _euclidean_distance(self, a: List[float], b: List[float]) -> float:
        """计算两个向量的欧氏距离"""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _find_outlier_cluster(
        self,
        vectors: List[Tuple[int, List[float]]],
        centroid: List[float],
    ) -> List[Tuple[int, List[float]]]:
        """
        寻找离群子集（简化 K-Means，K=2）

        策略：
            1. 取距离中心最远的个体作为种子 A
            2. 取距离种子 A 最远的个体作为种子 B
            3. 将所有个体按最近邻分配到 A 或 B 聚类
            4. 若两聚类中心距离 > 阈值，且小聚类 >= MIN_GROUP_SIZE，
               返回小聚类作为离群子集
        """
        if len(vectors) < self.MIN_GROUP_SIZE * 2:
            return []

        # 找距离中心最远的个体作为种子 A
        seed_a = max(vectors, key=lambda x: self._euclidean_distance(x[1], centroid))

        # 找距离种子 A 最远的个体作为种子 B
        seed_b = max(vectors, key=lambda x: self._euclidean_distance(x[1], seed_a[1]))

        # 分配个体到两个聚类
        cluster_a = []
        cluster_b = []

        for item in vectors:
            eid, vector = item
            dist_a = self._euclidean_distance(vector, seed_a[1])
            dist_b = self._euclidean_distance(vector, seed_b[1])
            if dist_a <= dist_b:
                cluster_a.append(item)
            else:
                cluster_b.append(item)

        # 确保 cluster_b 是较小的那个
        if len(cluster_a) < len(cluster_b):
            cluster_a, cluster_b = cluster_b, cluster_a

        # 小聚类必须满足最小群体大小
        if len(cluster_b) < self.MIN_GROUP_SIZE:
            return []

        # 计算两聚类中心距离
        centroid_a = self._compute_centroid([v for _, v in cluster_a])
        centroid_b = self._compute_centroid([v for _, v in cluster_b])
        inter_distance = self._euclidean_distance(centroid_a, centroid_b)

        if inter_distance < self.SPECIATION_DISTANCE_THRESHOLD:
            return []

        return cluster_b

    # -------------------------------------------------
    # 新物种注册
    # -------------------------------------------------

    def _register_new_species(
        self,
        parent_species: str,
        centroid: List[float],
        all_entity_ids: List[int],
        world: World,
    ) -> str | None:
        """
        注册新物种到工厂预设表

        返回新物种的标识名，失败返回 None
        """
        # 生成扁平命名的新物种名（避免嵌套如 herbivore_v1_v1）
        self._global_species_counter += 1
        # 从 parent_species 中提取基础名（去掉已有的 _sN 后缀）
        base_name = parent_species
        if "_s" in base_name:
            # 找到最后一个 _s 后面的数字，去掉它
            idx = base_name.rfind("_s")
            if idx > 0 and base_name[idx + 2:].isdigit():
                base_name = base_name[:idx]
        new_species_id = f"{base_name}_s{self._global_species_counter}"

        # 从任意一个原物种实体提取 expression_target 列表和基因模板
        # 用 centroid 的各维度值作为新物种的基因预设
        targets = self._get_expression_targets(world, all_entity_ids)
        if not targets:
            return None

        # 构建新物种的基因预设字典
        preset = {}
        for i, target in enumerate(targets):
            preset[target] = centroid[i]

        # 注册到动物工厂（如果原始物种是动物）
        from animal.animal_factory import AnimalFactory
        if parent_species in AnimalFactory.SPECIES_PRESETS:
            AnimalFactory.SPECIES_PRESETS[new_species_id] = preset
            logger.debug(f"[Speciation] 已注册动物新物种 '{new_species_id}' 到 AnimalFactory")
            return new_species_id

        # 注册到植物工厂（如果原始物种是植物）
        from plant.plant_factory import PlantFactory
        if parent_species in PlantFactory.SPECIES_PRESETS:
            # 植物需要同时更新 SPECIES_PRESETS 和 SPECIES_LIFECYCLE
            PlantFactory.SPECIES_PRESETS[new_species_id] = preset
            # 继承原始物种的寿命预设
            parent_lifecycle = PlantFactory.SPECIES_LIFECYCLE.get(
                parent_species, PlantFactory.SPECIES_LIFECYCLE.get("basic")
            )
            PlantFactory.SPECIES_LIFECYCLE[new_species_id] = parent_lifecycle
            logger.debug(f"[Speciation] 已注册植物新物种 '{new_species_id}' 到 PlantFactory")
            return new_species_id

        # 如果原始物种不在任何工厂中（可能是之前已经形成的新物种），
        # 尝试在两个工厂中都注册
        if parent_species not in AnimalFactory.SPECIES_PRESETS and \
           parent_species not in PlantFactory.SPECIES_PRESETS:
            # 从原始物种名推断类型（简单启发式）
            # 检查 entities 中是否有 AnimalComponent
            sample_entity = world.query_entity(all_entity_ids[0])
            if sample_entity and world.get_component(sample_entity, AnimalComponent):
                AnimalFactory.SPECIES_PRESETS[new_species_id] = preset
            elif sample_entity and world.get_component(sample_entity, PlantComponent):
                PlantFactory.SPECIES_PRESETS[new_species_id] = preset
                PlantFactory.SPECIES_LIFECYCLE[new_species_id] = \
                    PlantFactory.SPECIES_LIFECYCLE.get("basic")
            return new_species_id

        return None

    def _get_expression_targets(
        self, world: World, entity_ids: List[int]
    ) -> List[str]:
        """从实体组中提取统一的 expression_target 列表"""
        targets = set()
        for eid in entity_ids:
            entity = world.query_entity(eid)
            if entity is None:
                continue
            genome = world.get_component(entity, GenomeComponent)
            if genome:
                for gene in genome.genes:
                    targets.add(gene.expression_target)
        return sorted(targets)

    def _migrate_entities_to_species(
        self,
        world: World,
        outlier_vectors: List[Tuple[int, List[float]]],
        new_species_id: str,
    ) -> None:
        """将离群个体的物种标识更新为新物种"""
        for eid, _ in outlier_vectors:
            entity = world.query_entity(eid)
            if entity is None:
                continue
            tracker = world.get_component(entity, SpeciationTrackerComponent)
            if tracker is not None:
                tracker.species_id = new_species_id
                tracker.generation = 0  # 新物种从第 0 代开始计数

            # 同步更新 AnimalComponent / PlantComponent 中的 species 字段
            animal = world.get_component(entity, AnimalComponent)
            if animal is not None:
                animal.species = new_species_id

            plant = world.get_component(entity, PlantComponent)
            if plant is not None:
                # PlantComponent 没有 species 字段，暂不处理
                pass
