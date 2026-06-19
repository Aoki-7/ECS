#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物模拟层 — 基因、表型、生命周期、生长、衰老、死亡

目录结构:
    biology/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── components/              # 生物组件包
    │   ├── genome_component.py      # GenomeComponent: 基因组 (基因列表 + 表达状态)
    │   ├── phenotype_component.py   # PhenotypeComponent: 表型 (基因表达后的数值性状)
    │   ├── immune_component.py      # ImmuneComponent: 免疫系统 (抗体/抗原/感染状态)
    │   ├── health_status_component.py # HealthStatusComponent: 健康状态 (疾病/伤口/中毒)
    │   └── nutrient_component.py    # NutrientComponent: 营养状态 (水分/养分/储备)
    ├── systems/               # 生物系统包
    │   ├── gene_expression_system.py # GeneExpressionSystem: 基因 → 表型表达
    │   ├── growth_system.py         # GrowthSystem: 生长逻辑 (基因驱动形态变化)
    │   ├── aging_system.py          # AgingSystem: 衰老机制 (代谢率下降/修复能力降低)
    │   ├── death_system.py          # DeathSystem: 死亡触发 (健康/寿命/能量阈值)
    │   ├── reproduction_system.py   # ReproductionSystem: 繁殖机制 (基因重组/突变)
    │   ├── mutation_system.py       # MutationSystem: 基因突变 (随机/环境诱导)
    │   ├── life_cycle_system.py     # LifeCycleSystem: 生命周期推进 (阶段转换)
    │   └── morphology_system.py     # MorphologySystem: 形态更新 (体型/结构变化)
    ├── lifecycle/             # 生命周期子模块
    │   ├── components/            # 生命周期组件 (Energy/Morphology/LifeCycle)
    │   ├── systems/               # 生命周期系统 (Growth/Aging/Death)
    │   ├── aging/                 # 衰老子模块
    │   ├── birth/                 # 出生子模块
    │   ├── corpse/                # 尸体子模块
    │   ├── death/                 # 死亡子模块
    │   └── growth/                # 生长子模块
    ├── genetics/              # 遗传子模块
    │   └── gene.py                  # Gene: 基因原子定义 (名称/值/显隐性/突变率)
    ├── traits/                # 特征子模块
    │   └── trait.py                 # Trait: 基因表达后的数值性状
    ├── ecology/               # 生态子模块
    │   ├── components/              # 生态组件
    │   └── ...                      # 种群动态、物种形成、食物链
    └── tests/                 # 生物测试包

核心职责:
    1. 提供生物实体所需的基础组件:
       - GenomeComponent: 存储基因列表，支持表达/突变/重组
       - PhenotypeComponent: 存储基因表达后的数值性状 (身高/体重/颜色等)
       - EnergyComponent: 能量状态 (当前/最大/消耗率)
       - MorphologyComponent: 形态参数 (体型/结构/器官发育)
       - LifeCycleComponent: 生命周期阶段 (胚胎/幼年/成年/老年)
       - ImmuneComponent: 免疫系统状态
       - HealthStatusComponent: 健康状态 (疾病/伤口/中毒)
       - NutrientComponent: 营养状态 (水分/养分/储备)

    2. 实现生物核心过程:
       - 基因表达: Genome → Phenotype (GeneExpressionSystem)
       - 生长: 基因驱动形态变化 (GrowthSystem)
       - 衰老: 代谢率下降、修复能力降低 (AgingSystem)
       - 死亡: 健康/寿命/能量阈值检查 (DeathSystem)
       - 繁殖: 基因重组 + 突变 (ReproductionSystem)
       - 突变: 随机突变 + 环境诱导突变 (MutationSystem)

    3. 为上层模块提供生物学基础:
       - animal/: 复用 Genome/Energy/LifeCycle/Morphology/Immune/Health
       - plant/: 复用 Genome/Energy/LifeCycle，叠加光合/根系/冠层组件
       - human/: 复用全部基础组件，叠加认知/社交/文明组件

与其他模块的关系:
    - core/: 依赖 ECS 框架 (Entity/Component/System/World)
    - identity/: 实体分类系统 (生物属于 EntityCategory.LIFE)
    - animal/: 动物在 biology 基础上叠加行为系统 (觅食/捕食/社交/迁徙)
    - plant/: 植物在 biology 基础上叠加光合/根系/种子传播系统
    - human/: 人类在 biology 基础上叠加认知/社交/文明系统
    - decomposer/: 分解者处理死亡后的尸体 (CorpseComponent)
    - environment/: 环境因素影响生物 (温度/光照/土壤 → 生长/健康/能量)

设计原则:
    - 基因驱动: 所有生物属性由基因表达，无硬编码数值
    - 生命周期: 统一的出生→成长→衰老→死亡管线
    - 能量守恒: 所有生物活动消耗能量，能量来源于环境
    - 信息损失: 基因突变和环境压力导致性状变异

版本: v4.0
"""

from biology.lifecycle.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent

from biology.components.immune_component import ImmuneComponent
from biology.components.health_status_component import HealthStatusComponent
from biology.components.nutrient_component import NutrientComponent

from biology.genetics.gene import Gene
from biology.traits.trait import Trait

__all__ = [
    # 组件
    "EnergyComponent",
    "GenomeComponent",
    "PhenotypeComponent",
    "MorphologyComponent",
    "LifeCycleComponent",
    "ImmuneComponent",
    "HealthStatusComponent",
    "NutrientComponent",
    # 遗传
    "Gene",
    # 特征
    "Trait",
]
