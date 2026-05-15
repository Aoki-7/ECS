#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:rules_config.py
@说明:自定义规则配置 - 文明演进规则
@时间:2026/03/26 13:36:46
@作者:Sherry
@版本:2.0
'''

from core.entity import Entity
from core.world import World
from typing import Dict, Any

from resource.food.components.food_component import FoodComponent
from resource.wood.components.wood_component import WoodComponent
from resource.stone.components.stone_component import StoneComponent
from resource.metal.components.metal_component import MetalComponent
from resource.water.components.water_component import WaterComponent
from garbage.components.garbage_component import GarbageComponent

from human.components.economic.economy_component import EconomyComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.memory_component import MemoryComponent


# ===== 基础资源转换规则 =====

def spoiled_food_condition(food: FoodComponent) -> bool:
    """食物是否变质"""
    return food.is_spoiled()


def spoiled_food_transform(entity: Entity, world: World):
    """变质食物转换规则"""
    food: FoodComponent = world.get_component(entity=entity, component_type=FoodComponent)

    # 移除食物
    world.remove_component(entity=entity, component_type=food)

    # 转换为垃圾
    world.add_component(GarbageComponent(
        toxicity=food.poison + food.contamination
    ))


# ===== 文明演进规则 =====

def resource_depletion_condition(resource) -> bool:
    """资源是否耗尽"""
    return resource.amount <= 0


def resource_depletion_transform(entity: Entity, world: World):
    """资源耗尽处理"""
    resource = world.get_component(entity, type(world.get_component(entity, ResourceComponent)))
    if resource and resource.regenerable:
        resource.state = ResourceState.REGENERATING
    else:
        resource.state = ResourceState.DEPLETED


def skill_improvement_condition(memory: MemoryComponent, skill: SkillComponent) -> bool:
    """技能是否可以提升"""
    # 检查记忆中是否有足够的相关经验
    relevant_experiences = [exp for exp in memory.experiences
                          if exp.get('type') == 'skill_practice' and exp.get('skill_type') in skill.skills]
    return len(relevant_experiences) >= 5  # 5次练习后提升


def skill_improvement_transform(entity: Entity, world: World):
    """技能提升"""
    skill = world.get_component(entity, SkillComponent)
    memory = world.get_component(entity, MemoryComponent)

    # 找到最常练习的技能
    skill_counts = {}
    for exp in memory.experiences:
        if exp.get('type') == 'skill_practice':
            skill_type = exp.get('skill_type')
            skill_counts[skill_type] = skill_counts.get(skill_type, 0) + 1

    if skill_counts:
        best_skill = max(skill_counts, key=skill_counts.get)
        if best_skill in skill.skills:
            skill.skills[best_skill] += 0.1  # 提升0.1级
            skill.skills[best_skill] = min(skill.skills[best_skill], 10.0)  # 最高10级


def wealth_accumulation_condition(economy: EconomyComponent) -> bool:
    """财富是否达到积累阈值"""
    return economy.wealth >= 100.0  # 财富达到100时触发


def wealth_accumulation_transform(entity: Entity, world: World):
    """财富积累效应"""
    economy = world.get_component(entity, EconomyComponent)

    # 财富积累可以解锁新能力或社会地位
    if economy.wealth >= 100.0:
        # 增加社会地位
        social_comp = world.get_component(entity, SocialComponent)
        if social_comp:
            social_comp.social_status += 1

        # 重置财富阈值（但保留部分财富）
        economy.wealth = economy.wealth * 0.7  # 保留70%


    