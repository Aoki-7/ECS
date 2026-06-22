#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产出物创建器

职责：
    - 创建制作产出物实体
    - 添加到世界或库存
"""

import logging
from typing import Dict

from core.world import World
from human.components.economic.inventory.inventory_component import InventoryComponent

logger = logging.getLogger(__name__)


class ProductCreator:
    """产出物创建器"""

    def create_product(self, world: World, entity, result: Dict) -> None:
        """
        创建产出物

        Args:
            world: World实例
            entity: 制作实体
            result: 制作结果字典
        """
        if not result.get("success") or not result.get("output"):
            return

        output_type = result["output"]
        quality = result.get("quality", 0.5)
        props = result.get("properties", {})

        # 创建产出物实体
        product = world.create_entity()

        # 添加基础组件
        from identity.name_component import NameComponent
        world.add_component(product, NameComponent(name=output_type))

        from space.space_component import SpaceComponent
        space = world.get_component(entity, SpaceComponent)
        if space:
            world.add_component(product, SpaceComponent(x=space.x, y=space.y))

        # 添加质量组件
        from resource.components.resource_component import ResourceComponent
        world.add_component(product, ResourceComponent(
            resource_type=output_type,
            amount=1.0,
            quality=quality,
        ))

        # 添加属性组件（如果有）
        if props:
            from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent
            # 这里可以添加更多属性

        # 将产出物添加到制作者的库存
        inventory = world.get_component(entity, InventoryComponent)
        if inventory:
            inventory.items[output_type] = inventory.items.get(output_type, 0) + 1

        logger.debug(
            f"[ProductCreator] 创建产出物 {output_type} (质量:{quality:.2f}) "
            f"for E{entity.id}"
        )
