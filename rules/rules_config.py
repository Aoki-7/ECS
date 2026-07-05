#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@文件:rules_config.py
@说明:通用规则配置 —— 仅包含资源转换相关规则

设计原则：
    本文件只定义不依赖任何特定领域（如 human）的通用规则。
    人类特定的文明演进规则（技能提升、财富积累）已迁移至：
        human/rules/human_rules.py
"""

from typing import Dict, Any

from core.entity import Entity
from core.world import World

from resource.food.components.food_component import FoodComponent
from resource.food.systems.food_clean_up_system import FoodCleanupSystem
from resource.components.resource_component import ResourceComponent, ResourceState
from resource.wood.components.wood_component import WoodComponent
from resource.stone.components.stone_component import StoneComponent
from resource.metal.components.metal_component import MetalComponent
from resource.water.components.water_component import WaterComponent
from garbage.components.garbage_component import GarbageComponent


# =========================================================
# 基础资源转换规则
# =========================================================

def spoiled_food_condition(food: FoodComponent) -> bool:
    """食物是否变质"""
    if food is None:
        return False
    return FoodCleanupSystem.is_spoiled(food)


def spoiled_food_transform(entity: Entity, world: World):
    """变质食物转换规则：食物 → 垃圾"""
    food = world.get_component(entity, FoodComponent)
    if food is None:
        return

    world.remove_component(entity=entity, component_type=FoodComponent)

    toxicity = (
        getattr(food, "poison", 0.0)
        + getattr(food, "contamination", 0.0)
    )
    garbage = GarbageComponent(toxicity=toxicity)
    world.add_component(entity, garbage)


# =========================================================
# 资源耗尽规则
# =========================================================

def resource_depletion_condition(resource: ResourceComponent) -> bool:
    """资源是否耗尽"""
    if resource is None:
        return False
    return resource.amount <= 0


def resource_depletion_transform(entity: Entity, world: World):
    """资源耗尽处理"""
    resource = world.get_component(entity, ResourceComponent)
    if resource is None:
        return

    if getattr(resource, "regenerable", False):
        resource.state = ResourceState.REGENERATING
    else:
        resource.state = ResourceState.DEPLETED
