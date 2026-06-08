#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆注册系统

在实体创建后自动注册到统一记忆层。

职责：
    1. 监听实体创建事件（通过 World 的组件添加钩子）
    2. 提取实体的感官描述（从组件推断）
    3. 注册到 MemoryLayer

与 World 的关系：
    - World.create_entity() 创建实体
    - 组件添加后，本系统提取描述并注册概念
"""

import logging

from core.system import System
from core.world import World

from memory_layer import MemoryLayer, SensoryDescription

logger = logging.getLogger(__name__)


class MemoryRegistrationSystem(System):
    """
    记忆注册系统

    在实体创建并挂载组件后，自动提取感官描述并注册到记忆层。
    
    优先级：最高（在大多数系统之前执行）
    """
    priority = -100  # 最高优先级，确保最先执行
    tick_interval = 1

    def __init__(self):
        super().__init__()
        self._memory_layer = MemoryLayer.get_instance()
        self._registered_entities = set()  # 已注册的实体ID

    def update(self, world: World, dt: float = 1.0) -> None:
        """扫描新实体并注册到记忆层"""
        for entity_id, entity in world.entities.items():
            if entity_id in self._registered_entities:
                continue

            # 尝试提取实体类型和感官描述
            entity_type, description = self._extract_entity_info(world, entity)
            if entity_type and description:
                self._memory_layer.register_entity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    description=description,
                )
                self._registered_entities.add(entity_id)
                logger.debug(f"[MemoryRegistration] 实体 {entity_id}({entity_type}) 已注册到记忆层")

    def _extract_entity_info(self, world: World, entity) -> tuple[str | None, SensoryDescription | None]:
        """
        从实体组件提取类型和感官描述。
        
        支持：
        - AnimalComponent → animal
        - PlantComponent → plant
        - CategoryComponent → 从 category 推断
        """
        # 尝试 AnimalComponent
        try:
            from animal.components.animal_component import AnimalComponent
            animal_comp = world.get_component(entity, AnimalComponent)
            if animal_comp:
                return self._extract_animal_info(animal_comp)
        except ImportError:
            pass

        # 尝试 PlantComponent
        try:
            from plant.components.plant_component import PlantComponent
            plant_comp = world.get_component(entity, PlantComponent)
            if plant_comp:
                return self._extract_plant_info(plant_comp)
        except ImportError:
            pass

        # 尝试 CategoryComponent
        try:
            from core.category_component import CategoryComponent
            cat_comp = world.get_component(entity, CategoryComponent)
            if cat_comp:
                return self._extract_category_info(cat_comp)
        except ImportError:
            pass

        # 默认：无法识别类型
        return None, None

    def _extract_animal_info(self, animal_comp) -> tuple[str, SensoryDescription]:
        """从 AnimalComponent 提取信息"""
        entity_type = f"animal_{animal_comp.species}"
        
        # 根据物种推断感官描述
        description = SensoryDescription()
        
        # 食性影响描述
        if animal_comp.diet == "carnivore":
            description.texture = "危险"
        elif animal_comp.diet == "herbivore":
            description.texture = "温和"
        
        return entity_type, description

    def _extract_plant_info(self, plant_comp) -> tuple[str, SensoryDescription]:
        """从 PlantComponent 提取信息"""
        entity_type = "plant"
        
        description = SensoryDescription()
        # 植物默认描述
        description.texture = "有机"
        
        return entity_type, description

    def _extract_category_info(self, cat_comp) -> tuple[str | None, SensoryDescription | None]:
        """从 CategoryComponent 提取信息"""
        category_name = getattr(cat_comp.category, 'name', str(cat_comp.category))
        entity_type = category_name.lower()
        
        description = SensoryDescription()
        
        return entity_type, description
