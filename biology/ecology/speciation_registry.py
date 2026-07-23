#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物种形成注册器

职责：
    - 注册新物种到工厂预设表
    - 生成新物种ID
    - 构建基因预设字典
"""

import logging
from typing import List, Optional

from core.world import World
from biology.components.genome_component import GenomeComponent

logger = logging.getLogger(__name__)


class SpeciationRegistry:
    """物种形成注册器"""

    def register_new_species(
        self,
        parent_species: str,
        centroid: List[float],
        all_entity_ids: List[int],
        world: World,
        counter: int = 0,
    ) -> Optional[str]:
        """
        注册新物种到工厂预设表

        返回新物种的标识名，失败返回 None
        """
        # 生成扁平命名的新物种名（避免嵌套如 herbivore_v1_v1）
        # 从 parent_species 中提取基础名（去掉已有的 _sN 后缀）
        base_name = parent_species
        if "_s" in base_name:
            # 找到最后一个 _s 后面的数字，去掉它
            idx = base_name.rfind("_s")
            if idx > 0 and base_name[idx + 2:].isdigit():
                base_name = base_name[:idx]
        new_species_id = f"{base_name}_s{counter + 1}"

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
        from biology.organisms.animal.animal_factory import AnimalFactory
        if parent_species in AnimalFactory.SPECIES_PRESETS:
            AnimalFactory.SPECIES_PRESETS[new_species_id] = preset
            logger.info(f"[Speciation] 已注册新动物物种 '{new_species_id}' 到 AnimalFactory")

        # 注册到植物工厂（如果原始物种是植物）
        from biology.organisms.plant.plant_factory import PlantFactory
        if parent_species in PlantFactory.SPECIES_PRESETS:
            PlantFactory.SPECIES_PRESETS[new_species_id] = preset
            logger.info(f"[Speciation] 已注册新植物物种 '{new_species_id}' 到 PlantFactory")

        return new_species_id

    def _get_expression_targets(self, world: World, entity_ids: List[int]) -> List[str]:
        """从实体中提取所有 expression_target 列表"""
        all_targets = set()
        for eid in entity_ids:
            entity = world.query_entity(eid)
            if entity is None:
                continue
            genome = world.get_component(entity, GenomeComponent)
            if genome is None or not genome.genes:
                continue
            for gene in genome.genes:
                all_targets.add(gene.expression_target)
        return sorted(all_targets)