#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
SystemPriority — 系统优先级常量

集中管理所有 ECS System 的 priority 值，避免魔法值分散在 80+ 个文件中。

规则：
    - 数字越小，执行越早
    - 同优先级内，按注册顺序执行
    - 预留 5 的倍数以容纳中间插入
"""


class SystemPriority:
    """系统优先级枚举"""

    # 基础设施层（0–9）
    SPACE = 0       # SpaceSystem 由 World 内部维护，通常不显示设置
    TIME = 5
    EVENT_LOG = 5

    # 环境层（20–29）
    ENVIRONMENT = 20
    ATMOSPHERE = 20
    WEATHER_EFFECT = 25
    PATHFINDING = 28
    COMBAT_AI = 29

    # 碰撞检测层（15）— 在移动后、行为前检测碰撞
    COLLISION = 15

    # 人类核心层（30–43）
    HUMAN_COGNITIVE = 30
    CONFLICT_DETECTION = 31
    CONFLICT_RESOLUTION = 32
    REPUTATION = 35
    ECONOMY = 35
    HUMAN_OBSERVATION = 45
    TERRITORY = 39
    LEADERSHIP = 40
    LOYALTY = 41
    RECRUIT = 42
    TRIBE = 43

    # 生理与生物层（40–50）
    PHYSIOLOGY = 40
    HEALTH = 40
    HUMAN_DEATH_TRIGGER = 40
    DISEASE_SPREAD = 41
    GRAZING = 42
    HEALTHCARE = 42
    MEMORY_DECAY = 43
    ANIMAL_NEEDS = 44
    ANIMAL_SOCIAL = 44
    ANIMAL_MEMORY = 44
    ANIMAL_PERCEPTION = 44
    ANIMAL_LEARNING = 44
    ANIMAL_TERRITORY = 45
    ANIMAL_MIGRATION = 46
    PLANT_GROWTH = 48
    PREDATION = 49

    # 生物学生命周期层（50）
    BIOLOGY = 50
    GENE_EXPRESSION = 50
    COMPETITION = 50
    GROWTH = 50
    MORPHOLOGY = 50
    NUTRIENT = 50
    LIFE_CYCLE = 50
    SENESCENCE = 50
    DAMAGE_REPAIR = 50
    MUTATION = 50
    REPRODUCTION = 50
    SEED_DISPERSAL = 50
    IMMUNE = 50
    CREATURE_DEATH_TRIGGER = 50
    DEATH_EXECUTION = 50
    DEATH_EVENT = 50
    CORPSE = 50
    DEATH_ARCHIVE = 55

    # 规则与文明层（60–70）
    RULES = 60
    TRANSFORMATION = 60
    CIVILIZATION = 70