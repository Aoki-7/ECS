#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动物系统 — 动物实体创建、行为、生态交互（食草/捕食/社交/迁徙）

目录结构:
    animal/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── animal_factory.py        # AnimalFactory: 按物种预设创建动物实体
    ├── presets.py               # SPECIES_PRESETS: 物种模板 (basic/fast/tank/predator)
    ├── components/              # 动物组件包
    │   ├── animal_component.py      # AnimalComponent: 基础动物属性 (物种/行为模式)
    │   ├── animal_needs_component.py  # AnimalNeedsComponent: 生理需求 (饥饿/口渴/睡眠/恐惧/繁殖)
    │   ├── animal_social_component.py # AnimalSocialComponent: 社交状态 (群体/配偶/亲子关系)
    │   ├── animal_memory_component.py # AnimalMemoryComponent: 环境记忆 (食物/水源/威胁位置)
    │   ├── animal_territory_component.py # AnimalTerritoryComponent: 领地边界与入侵记录
    │   ├── animal_reproduction_component.py # AnimalReproductionComponent: 繁殖状态 (求偶/怀孕/哺乳期)
    │   ├── animal_perception_component.py  # AnimalPerceptionComponent: 感知范围与优先级
    │   └── animal_learning_component.py    # AnimalLearningComponent: 学习记忆 (正/负强化)
    ├── systems/               # 动物系统包
    │   ├── grazing_system.py        # GrazingSystem: 食草动物觅食 (读取 Plant/Resource)
    │   ├── predation_system.py      # PredationSystem: 食肉动物捕食 (追踪/伏击/追击)
    │   ├── animal_reproduction_system.py # AnimalReproductionSystem: 动物繁衍 (成熟期+能量阈值)
    │   ├── animal_needs_system.py   # AnimalNeedsSystem: 生理需求驱动 (饥饿→觅食/口渴→寻水)
    │   ├── animal_social_system.py  # AnimalSocialSystem: 社交行为 (群体聚集/配偶选择/亲子保护)
    │   ├── animal_memory_system.py  # AnimalMemorySystem: 记忆更新 (发现/消耗/遗忘)
    │   ├── animal_territory_system.py # AnimalTerritorySystem: 领地巡逻与入侵防御
    │   ├── animal_migration_system.py # AnimalMigrationSystem: 季节性迁徙 (路径规划/资源追踪)
    │   ├── animal_perception_system.py  # AnimalPerceptionSystem: 环境感知 (视野/嗅觉/听觉)
    │   └── animal_learning_system.py    # AnimalLearningSystem: 行为学习 (关联形成/习惯化)
    └── tests/                 # 动物测试包 (25 测试)

核心职责:
    1. 动物实体创建:
       - AnimalFactory.create_animal(): 按物种预设创建完整动物实体 (含基因组/生命周期/空间坐标)
       - SPECIES_PRESETS: 9 种预设 (basic/fast/tank/predator/herbivore/social/solitary/migratory/territorial)
       - 每种预设包含 20+ 基因参数，无外观硬编码

    2. 动物行为系统:
       - 食草: GrazingSystem → 读取 PlantComponent + ResourceComponent，消耗植物产量
       - 捕食: PredationSystem → 追踪/伏击/追击猎物，能量收益 vs 消耗权衡
       - 社交: AnimalSocialSystem → 群体聚集、配偶选择、亲子保护、等级制度
       - 记忆: AnimalMemorySystem → 食物/水源/威胁位置记忆，随时间遗忘
       - 领地: AnimalTerritorySystem → 边界巡逻、入侵检测、驱逐行为
       - 迁徙: AnimalMigrationSystem → 季节性路径规划，资源追踪
       - 感知: AnimalPerceptionSystem → 视野/嗅觉/听觉多模态感知
       - 学习: AnimalLearningSystem → 正/负强化关联，习惯化与敏感化

    3. 生理需求驱动:
       - AnimalNeedsSystem → 饥饿/口渴/睡眠/恐惧/繁殖需求
       - 需求优先级动态排序 (紧急度 = 当前值 / 阈值)
       - 需求驱动行为选择 (饥饿→觅食/口渴→寻水/恐惧→逃跑)

与其他模块的关系:
    - core/: 依赖 ECS 框架
    - biology/: 复用 Genome/Energy/LifeCycle/Morphology/Immune/Health 组件
    - biology/systems/: 统一调度生长/衰老/繁殖/死亡
    - plant/: GrazingSystem 读取 PlantComponent，消耗植物产量 (过度啃食导致植物死亡)
    - environment/: 环境因素影响动物 (温度→能量消耗/天气→迁徙触发/地形→移动成本)
    - space/: 使用 SpatialIndex 进行位置查询和路径规划
    - decomposer/: 动物死亡后转化为 CorpseComponent，由 DecomposerSystem 分解
    - ecology/: 种群动态、食物链、物种竞争

设计原则:
    - 基因驱动: 所有动物属性由基因表达，行为倾向由基因预设
    - 能量守恒: 所有行为消耗能量，能量来源于食物 (植物/猎物)
    - 感知有限: 动物只能感知有限范围内的环境，信息不完整
    - 学习适应: 动物可通过经验学习，但学习有遗忘曲线

版本: v4.0
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