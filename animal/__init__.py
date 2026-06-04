#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动物系统模块 — 动物实体的创建、行为与生态交互

职责：
    - AnimalFactory: 按物种预设创建动物实体（含基因组、生命周期、空间坐标）
    - SPECIES_PRESETS: 物种模板（basic/fast/tank 等属性配置）
    - GrazingSystem: 食草动物的植物觅食行为
    - PredationSystem: 食肉动物的捕食行为
    - AnimalReproductionSystem: 动物繁衍（成熟期+能量阈值）

与 biology/ 的关系：
    - 动物是独立的生物实体，复用 biology/ 的 GenomeComponent、EnergyComponent、
      LifeCycleComponent、MorphologyComponent、ImmuneComponent、HealthStatusComponent
    - 通过 biology/systems/ 统一调度生长、衰老、繁殖、死亡

与 plant/ 的关系：
    - GrazingSystem 读取 PlantComponent 和 ResourceComponent，消耗植物产量
    - 植物过度啃食可能导致死亡（ResourceComponent.amount <= 0）

与 ecology/ 的关系：
    - 动物死亡后由 DeathSystem 转化为 CorpseComponent
    - DecomposerSystem 分解尸体为土壤养分
"""

from .animal_factory import AnimalFactory
from .presets import SPECIES_PRESETS
from .systems.grazing_system import GrazingSystem
from .systems.predation_system import PredationSystem
from .systems.animal_reproduction_system import AnimalReproductionSystem

__all__ = [
    "AnimalFactory",
    "SPECIES_PRESETS",
    "GrazingSystem",
    "PredationSystem",
    "AnimalReproductionSystem",
]
