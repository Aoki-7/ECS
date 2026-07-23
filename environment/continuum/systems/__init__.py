#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续统系统包 — 扩展物理过程

v4.0 新增系统:
    - FireSpreadSystem: 火灾蔓延 (热传递 + 燃烧传播)
    - ErosionSedimentSystem: 土壤侵蚀/沉积 (水流携带)
    - GasDiffusionSystem: CO₂/O₂ 扩散 (气体浓度梯度)
    - GroundwaterFlowSystem: 地下水流动 (水头梯度)

依赖:
    - environment.continuum/: 基础连续统框架
    - environment.continuum.continuum_utils: 共享工具

版本: v4.0
"""

from .fire_spread_system import FireSpreadSystem
from .erosion_sediment_system import ErosionSedimentSystem
from .gas_diffusion_system import GasDiffusionSystem
from .groundwater_flow_system import GroundwaterFlowSystem
from .bio_environment_coupling_system import BioEnvironmentCouplingSystem
from .adaptive_timestep_system import AdaptiveTimestepSystem

__all__ = [
    "FireSpreadSystem",
    "ErosionSedimentSystem",
    "GasDiffusionSystem",
    "GroundwaterFlowSystem",
    "BioEnvironmentCouplingSystem",
    "AdaptiveTimestepSystem",
]