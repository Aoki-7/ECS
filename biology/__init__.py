#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/__init__.py
@说明:生物模拟层

本模块提供生物实体所需的组件、系统与遗传机制，包括：
    - 组件 (components): 能量、基因组、表型、形态、生命周期、生长
    - 系统 (systems): 基因表达、生长、衰老、死亡、繁殖、突变、生命周期推进、形态更新
    - 遗传 (genetics): 基因原子定义
    - 特征 (traits): 基因表达后的数值性状

使用示例：
    from biology import GenomeComponent, GeneExpressionSystem
"""

from biology.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.morphology_component import MorphologyComponent
from biology.components.life_cycle_component import LifeCycleComponent

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
    "CompetitionComponent",
    # 遗传
    "Gene",
    # 特征
    "Trait",
]
