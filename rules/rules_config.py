#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@文件:rules_config.py
@说明:自定义规则配置 - 文明演进规则
@时间:2026/03/26 13:36:46
@作者:Sherry
@版本:3.0
"""

from typing import Dict, Any

from core.entity import Entity
from core.world import World

from resource.food.components.food_component import (
    FoodComponent,
)

from resource.components.resource_component import (
    ResourceComponent,
    ResourceState,
)

from resource.wood.components.wood_component import (
    WoodComponent,
)

from resource.stone.components.stone_component import (
    StoneComponent,
)

from resource.metal.components.metal_component import (
    MetalComponent,
)

from resource.water.components.water_component import (
    WaterComponent,
)

from garbage.components.garbage_component import (
    GarbageComponent,
)

from human.components.economic.economy_component import (
    EconomyComponent,
)

from human.components.abilities.skill_component import (
    SkillComponent,
)

from human.components.cognitive.memory_component import (
    MemoryComponent,
)

from human.components.social.social_component import (
    SocialComponent,
)


# =========================================================
# 基础资源转换规则
# =========================================================

def spoiled_food_condition(
    food: FoodComponent
) -> bool:
    """
    食物是否变质
    """

    if food is None:
        return False

    return food.is_spoiled()


def spoiled_food_transform(
    entity: Entity,
    world: World
):
    """
    变质食物转换规则
    """

    food = world.get_component(
        entity,
        FoodComponent
    )

    if food is None:
        return

    # =====================================================
    # 移除食物组件
    # =====================================================

    world.remove_component(
        entity=entity,
        component_type=FoodComponent
    )

    # =====================================================
    # 转换为垃圾
    # =====================================================

    toxicity = (
        getattr(food, "poison", 0.0)
        + getattr(food, "contamination", 0.0)
    )

    garbage = GarbageComponent(
        toxicity=toxicity
    )

    world.add_component(
        entity,
        garbage
    )


# =========================================================
# 文明演进规则
# =========================================================

def resource_depletion_condition(
    resource: ResourceComponent
) -> bool:
    """
    资源是否耗尽
    """

    if resource is None:
        return False

    return resource.amount <= 0


def resource_depletion_transform(
    entity: Entity,
    world: World
):
    """
    资源耗尽处理
    """

    resource: ResourceComponent = world.get_component(
        entity,
        ResourceComponent
    )

    if resource is None:
        return

    # 可再生资源
    if getattr(resource, "regenerable", False):
        resource.state = ResourceState.REGENERATING

    # 不可再生资源
    else:
        resource.state = ResourceState.DEPLETED


def skill_improvement_condition(
    memory: MemoryComponent,
    skill: SkillComponent
) -> bool:
    """
    技能是否可以提升
    """

    if memory is None or skill is None:
        return False

    experiences = getattr(
        memory,
        "experiences",
        []
    )

    relevant_experiences = [
        exp
        for exp in experiences
        if (
            exp.get("type") == "skill_practice"
            and exp.get("skill_type") in skill.skills
        )
    ]

    # 5次练习后提升
    return len(relevant_experiences) >= 5


def skill_improvement_transform(
    entity: Entity,
    world: World
):
    """
    技能提升
    """

    skill: SkillComponent = world.get_component(
        entity,
        SkillComponent
    )

    memory = world.get_component(
        entity,
        MemoryComponent
    )

    if skill is None or memory is None:
        return

    experiences = getattr(
        memory,
        "experiences",
        []
    )

    skill_counts = {}

    # =====================================================
    # 统计技能练习次数
    # =====================================================

    for exp in experiences:

        if exp.get("type") != "skill_practice":
            continue

        skill_type = exp.get("skill_type")

        if skill_type is None:
            continue

        skill_counts[skill_type] = (
            skill_counts.get(skill_type, 0)
            + 1
        )

    if not skill_counts:
        return

    # =====================================================
    # 找到练习最多的技能
    # =====================================================

    best_skill = max(
        skill_counts,
        key=skill_counts.get
    )

    if best_skill not in skill.skills:
        return

    # =====================================================
    # 技能成长
    # =====================================================

    current_level = float(
        skill.skills.get(best_skill, 0.0)
    )

    current_level += 0.1

    # 最大等级 10
    current_level = min(
        current_level,
        10.0
    )

    skill.skills[best_skill] = current_level


def wealth_accumulation_condition(
    economy: EconomyComponent
) -> bool:
    """
    财富是否达到积累阈值
    """

    if economy is None:
        return False

    return economy.wealth >= 100.0


def wealth_accumulation_transform(
    entity: Entity,
    world: World
):
    """
    财富积累效应
    """

    economy: EconomyComponent = world.get_component(
        entity,
        EconomyComponent
    )

    if economy is None:
        return

    if economy.wealth < 100.0:
        return

    # =====================================================
    # 社会影响
    # =====================================================

    social_comp: SocialComponent = world.get_component(
        entity,
        SocialComponent
    )

    if social_comp is not None:

        # relations 兼容保护
        relations = getattr(
            social_comp,
            "relations",
            {}
        )

        # 对已有关系增加好感
        for eid in list(relations.keys()):

            if hasattr(
                social_comp,
                "update_relation"
            ):
                social_comp.update_relation(
                    eid,
                    1
                )

        # social_status 兼容保护
        if hasattr(
            social_comp,
            "social_status"
        ):
            social_comp.social_status += 1

    # =====================================================
    # 财富消耗
    # =====================================================

    # 保留 70% 财富
    economy.wealth *= 0.7