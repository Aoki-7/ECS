#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
human/rules/human_rules.py — 人类特定规则

职责：
    定义仅适用于人类的文明演进规则，如技能提升、财富积累等。
    这些规则由 TransformationSystem 调用，但配置在人类领域内，
    避免通用规则引擎（rules/）依赖特定领域组件。
"""

from core.entity import Entity
from core.world import World

from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.social.social_component import SocialComponent


def skill_improvement_condition(
    memory: MemoryComponent,
    skill: SkillComponent
) -> bool:
    """技能是否可以提升（5次练习后提升）"""
    if memory is None or skill is None:
        return False

    experiences = getattr(memory, "experiences", [])
    relevant_experiences = [
        exp for exp in experiences
        if (
            exp.get("type") == "skill_practice"
            and exp.get("skill_type") in skill.skills
        )
    ]
    return len(relevant_experiences) >= 5


def skill_improvement_transform(entity: Entity, world: World):
    """技能提升转换"""
    skill = world.get_component(entity, SkillComponent)
    memory = world.get_component(entity, MemoryComponent)

    if skill is None or memory is None:
        return

    experiences = getattr(memory, "experiences", [])
    skill_counts = {}

    for exp in experiences:
        if exp.get("type") != "skill_practice":
            continue
        skill_type = exp.get("skill_type")
        if skill_type is None:
            continue
        skill_counts[skill_type] = skill_counts.get(skill_type, 0) + 1

    if not skill_counts:
        return

    best_skill = max(skill_counts, key=skill_counts.get)
    if best_skill not in skill.skills:
        return

    current_level = float(skill.skills.get(best_skill, 0.0))
    current_level += 0.1
    current_level = min(current_level, 10.0)
    skill.skills[best_skill] = current_level


def wealth_accumulation_condition(economy: EconomyComponent) -> bool:
    """财富是否达到积累阈值"""
    if economy is None:
        return False
    return economy.wealth >= 100.0


def wealth_accumulation_transform(entity: Entity, world: World):
    """财富积累效应（社会地位提升 + 财富消耗）"""
    economy = world.get_component(entity, EconomyComponent)
    if economy is None or economy.wealth < 100.0:
        return

    social_comp = world.get_component(entity, SocialComponent)
    if social_comp is not None:
        relations = getattr(social_comp, "relations", {})
        for eid in list(relations.keys()):
            if hasattr(social_comp, "update_relation"):
                social_comp.update_relation(eid, 1)
        if hasattr(social_comp, "social_status"):
            social_comp.social_status += 1

    # 保留 70% 财富
    economy.wealth *= 0.7