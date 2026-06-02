#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物系统模块 — 植物实体的创建与管理

职责：
    - PlantFactory: 按物种预设创建植物实体
    - SPECIES_PRESETS: 9 种植物物种模板（属性配置）
    - SPECIES_LIFECYCLE: 物种生命周期模板（种子→幼苗→成熟→衰老）
    - 植物完全依赖 biology/ 的生命周期系统实现生长、繁殖、死亡

与 biology/ 的关系：
    - 植物是最基础的生物实体，直接体现 biology/ 的基因→表现型→生长管线
    - 通过光合作用将 environment/light_field/ 的能量转化为生物量
    - 通过 biology/systems/ReproductionSystem 产生种子/果实

与 resource/ 的关系：
    - 成熟植物可被人类砍伐转化为木材（resource/wood/）
    - 果实可作为食物（resource/food/）
    - 植物本身也是动物的觅食目标
"""

from .plant_factory import PlantFactory
from .presets import SPECIES_PRESETS, SPECIES_LIFECYCLE

__all__ = ["PlantFactory", "SPECIES_PRESETS", "SPECIES_LIFECYCLE"]
