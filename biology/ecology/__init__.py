"""
生态子模块 — 种群动态、物种形成、食物链

依赖:
    - biology/
    - core/
    - animal/
    - plant/

版本: v4.0
"""
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
生态学模块 — 生态系统层面的种群、营养级、物质循环与物种形成

本模块提供生态系统级的模拟能力，连接个体生物与宏观生态过程：
    - 组件 (components): 食物链位置、种群参数、物种形成追踪
    - 系统 (systems):
        - EcologyBalanceSystem   : 生态平衡监控（生物多样性、能量金字塔）
        - PopulationDynamicsSystem : 基于 Lotka-Volterra 的种群动态调节
        - TrophicLevelSystem     : 营养级能量传递（Lindeman 定律）
        - SpeciationSystem       : 遗传分化检测与新物种自动注册

使用示例：
    from biology.ecology import (
        FoodChainComponent, PopulationComponent, SpeciationTrackerComponent,
        EcologyBalanceSystem, PopulationDynamicsSystem,
        TrophicLevelSystem, SpeciationSystem,
    )
"""

# ── 组件 ──
from biology.ecology.components.food_chain_component import FoodChainComponent
from biology.ecology.components.population_component import PopulationComponent
from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent

# ── 系统 ──
from biology.ecology.ecology_balance_system import EcologyBalanceSystem
from biology.ecology.population_dynamics_system import PopulationDynamicsSystem
from biology.ecology.trophic_level_system import TrophicLevelSystem
from biology.ecology.speciation_system import SpeciationSystem

__all__ = [
    # 组件
    "FoodChainComponent",
    "PopulationComponent",
    "SpeciationTrackerComponent",
    # 系统
    "EcologyBalanceSystem",
    "PopulationDynamicsSystem",
    "TrophicLevelSystem",
    "SpeciationSystem",
]

