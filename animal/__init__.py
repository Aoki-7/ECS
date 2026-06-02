#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动物系统模块 — 动物实体的创建与管理

职责：
    - AnimalFactory: 按物种预设创建动物实体
    - SPECIES_PRESETS: 物种模板（basic/fast/tank 等属性配置）
    - 动物复用 biology/ 的生命周期、基因、健康组件
    - 动物行为通过 human/ 的行为流水线简化版实现

与 biology/ 的关系：
    - 动物是人类系统之外的另一类生物实体
    - 复用 biology/ 的 GenomeComponent、EnergyComponent、LifeCycleComponent
    - 通过 biology/systems/ 统一调度生长、衰老、繁殖、死亡

与 human/ 的关系：
    - 动物可作为人类的食物来源（通过 rules/ 转化为肉类资源）
    - 某些动物可能对人类构成威胁（ CombatSystem 交互）
"""

from .animal_factory import AnimalFactory
from .presets import SPECIES_PRESETS

__all__ = ["AnimalFactory", "SPECIES_PRESETS"]