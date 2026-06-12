"""
动物系统 — 动物实体创建、行为、生态交互（食草/捕食/社交/迁徙）

职责：
    - 动物实体工厂与物种预设
    - 食草/捕食/社交/迁徙等行为系统
    - 与 plant/、environment/ 生态交互

依赖：
    - core/
    - biology/
    - space/
    - environment/
    - resource/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动物系统模块 — 动物实体的创建、行为与生态交互（重构版）

职责：
    - AnimalFactory: 按物种预设创建动物实体（含基因组、生命周期、空间坐标）
    - SPECIES_PRESETS: 物种模板（basic/fast/tank/predator 等属性配置）
    - GrazingSystem: 食草动物的植物觅食行为
    - PredationSystem: 食肉动物的捕食行为（已拆分方法）
    - AnimalReproductionSystem: 动物繁衍（成熟期+能量阈值）
    - AnimalNeedsSystem: 动物生理需求驱动（饥饿/口渴/睡眠/恐惧/繁殖）
    - AnimalSocialSystem: 动物社交行为（群体/配偶/亲子关系）
    - AnimalMemorySystem: 动物环境记忆（食物/水源/威胁位置）
    - AnimalTerritorySystem: 动物领地行为（边界巡逻/入侵防御）
    - AnimalMigrationSystem: 动物季节性迁徙

与 biology/ 的关系：
    - 动物是独立的生物实体，复用 biology/ 的 GenomeComponent、EnergyComponent、
      LifeCycleComponent、MorphologyComponent、ImmuneComponent、HealthStatusComponent
    - 通过 biology/systems/ 统一调度生长、衰老、繁殖、死亡

与 plant/ 的关系：
    - GrazingSystem 读取 PlantComponent 和 ResourceComponent，消耗植物产量
    - 植物过度啃食可能导致死亡（ResourceComponent.amount <= 0）

与 ecology/ 的关系：
    - 动物死亡后由 DeathSystem 转化为 CorpseComponent
    - decomposer.DecomposerSystem 分解尸体为土壤养分
"""

from .animal_factory import AnimalFactory
from .presets import SPECIES_PRESETS

# 组件
from .components.animal_component import AnimalComponent
from .components.animal_needs_component import AnimalNeedsComponent
from .components.animal_social_component import AnimalSocialComponent
from .components.animal_memory_component import AnimalMemoryComponent
from .components.animal_territory_component import AnimalTerritoryComponent
from .components.animal_reproduction_component import AnimalReproductionComponent
from .components.animal_perception_component import AnimalPerceptionComponent
from .components.animal_learning_component import AnimalLearningComponent

# 系统
from .systems.grazing_system import GrazingSystem
from .systems.predation_system import PredationSystem
from .systems.animal_reproduction_system import AnimalReproductionSystem
from .systems.animal_needs_system import AnimalNeedsSystem
from .systems.animal_social_system import AnimalSocialSystem
from .systems.animal_memory_system import AnimalMemorySystem
from .systems.animal_territory_system import AnimalTerritorySystem
from .systems.animal_migration_system import AnimalMigrationSystem
from .systems.animal_perception_system import AnimalPerceptionSystem
from .systems.animal_learning_system import AnimalLearningSystem

__all__ = [
    # 工厂与预设
    "AnimalFactory",
    "SPECIES_PRESETS",
    # 组件
    "AnimalComponent",
    "AnimalNeedsComponent",
    "AnimalSocialComponent",
    "AnimalMemoryComponent",
    "AnimalTerritoryComponent",
    "AnimalReproductionComponent",
    "AnimalPerceptionComponent",
    "AnimalLearningComponent",
    # 系统
    "GrazingSystem",
    "PredationSystem",
    "AnimalReproductionSystem",
    "AnimalNeedsSystem",
    "AnimalSocialSystem",
    "AnimalMemorySystem",
    "AnimalTerritorySystem",
    "AnimalMigrationSystem",
    "AnimalPerceptionSystem",
    "AnimalLearningSystem",
]

