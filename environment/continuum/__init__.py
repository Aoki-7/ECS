#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续统子模块 — 相邻单元格间物理扩散与平流

目录结构:
    environment/continuum/
    ├── __init__.py                    # 本文件：包导出
    ├── continuum_config.py            # 所有扩散系数、恢复率、地形映射
    ├── continuum_utils.py             # 共享工具 (边界解析、缓存、守恒检查、扩散内核)
    ├── continuum_processors.py        # 5 大物理处理器 (热扩散/湿度扩散/重力水流/风驱平流/自恢复)
    ├── environmental_continuum_system.py  # 系统入口 (网格构建、处理器调度、守恒验证)
    ├── systems/                       # 扩展系统包
    │   ├── __init__.py                  # 系统包导出
    │   ├── fire_spread_system.py        # 火灾蔓延系统 (Phase 2)
    │   ├── erosion_sediment_system.py   # 土壤侵蚀/沉积系统 (Phase 2)
    │   ├── gas_diffusion_system.py      # CO₂/O₂ 扩散系统 (Phase 2)
    │   ├── groundwater_flow_system.py   # 地下水流动系统 (Phase 2)
    │   ├── bio_environment_coupling_system.py # 生物-环境耦合系统 (Phase 3)
    │   └── adaptive_timestep_system.py  # 自适应时间步长系统 (Phase 4)
    └── tests/
        └── test_continuum_processors.py   # 处理器测试 (16 测试)

核心职责:
    基础物理过程 (5 大机制):
    1. 热扩散 (Thermal Diffusion): 傅里叶热传导，温度梯度 → 热通量
    2. 湿度扩散 (Humidity Diffusion): 菲克扩散定律，湿度梯度 → 水汽通量
    3. 重力水流 (Gravity Water Flow): 达西定律简化，海拔梯度 → 水流
    4. 风驱平流 (Wind Advection): 平流方程，风向 → 温度/湿度传递
    5. 生态自恢复 (Self-Recovery): 松弛模型，向顶极状态恢复

    扩展物理过程 (Phase 2-4):
    6. 火灾蔓延 (Fire Spread): 热传递 + 燃烧传播 (Phase 2)
    7. 土壤侵蚀/沉积 (Erosion/Sediment): 水流携带土壤颗粒 (Phase 2)
    8. CO₂/O₂ 扩散 (Gas Diffusion): 气体浓度梯度交换 (Phase 2)
    9. 地下水流动 (Groundwater Flow): 水头梯度驱动 (Phase 2)
    10. 生物-环境耦合 (Bio-Environment Coupling): 生物活动影响环境 (Phase 3)
    11. 自适应时间步长 (Adaptive Timestep): 数值稳定性控制 (Phase 4)

数值稳定性:
    - 共享组件缓存 (ContinuumCache): 单次遍历，避免重复查询
    - 共享边界解析 (resolve_boundary): 消除代码重复
    - 守恒检查 (ConservationSnapshot): 每步验证能量/水分/养分守恒
    - 限制变化量 (limit_change): 防止数值震荡
    - 自适应步长 (AdaptiveTimestepSystem): 变化过大时自动减小 dt

统一扩散框架:
    - PollutionDiffusionSystem: 使用 compute_diffusion_flux 通用内核
    - OceanCurrentSystem: 使用 resolve_boundary + 指数衰减模型
    - WaterCycleSystem: 使用重力水流模型 + 扩散内核

与其他模块的关系:
    - environment/: 环境管线第 5 层 (空间平滑)
    - environment/systems/: 在 EnvironmentSyncSystem 之后执行
    - core/: 依赖 ECS 框架和 ArchetypeStore 缓存
    - space/: 使用 SpaceComponent 构建网格索引
    - plant/: 植被影响热扩散/火灾燃料/侵蚀
    - animal/: 动物活动影响土壤紧实度
    - human/: 建筑影响风场/农业影响养分

设计原则:
    - 物理正确: 每个机制有明确的数学公式和物理单位
    - 数值稳定: 守恒检查、变化量限制、自适应步长
    - 可扩展: 新增处理器只需继承基类，无需复制样板代码
    - 可配置: 所有参数集中配置，支持运行时热切换
    - 统一框架: 所有扩散过程使用相同的内核和边界处理

版本: v4.0
"""

from .continuum_utils import (
    ContinuumCache,
    ConservationSnapshot,
    resolve_boundary,
    compute_diffusion_flux,
    apply_diffusion_fluxes,
    sigmoid_factor,
    clamp,
    take_conservation_snapshot,
    check_conservation,
    get_neighbor_offsets,
)
from .continuum_processors import (
    ContinuumProcessor,
    ThermalDiffusionProcessor,
    HumidityDiffusionProcessor,
    GravityWaterFlowProcessor,
    WindAdvectionProcessor,
    SelfRecoveryProcessor,
)
from .environmental_continuum_system import EnvironmentalContinuumSystem
from .systems import (
    FireSpreadSystem,
    ErosionSedimentSystem,
    GasDiffusionSystem,
    GroundwaterFlowSystem,
    BioEnvironmentCouplingSystem,
    AdaptiveTimestepSystem,
)

__all__ = [
    # 工具
    "ContinuumCache",
    "ConservationSnapshot",
    "resolve_boundary",
    "compute_diffusion_flux",
    "apply_diffusion_fluxes",
    "sigmoid_factor",
    "clamp",
    "take_conservation_snapshot",
    "check_conservation",
    "get_neighbor_offsets",
    # 处理器
    "ContinuumProcessor",
    "ThermalDiffusionProcessor",
    "HumidityDiffusionProcessor",
    "GravityWaterFlowProcessor",
    "WindAdvectionProcessor",
    "SelfRecoveryProcessor",
    # 基础系统
    "EnvironmentalContinuumSystem",
    # 扩展系统
    "FireSpreadSystem",
    "ErosionSedimentSystem",
    "GasDiffusionSystem",
    "GroundwaterFlowSystem",
    "BioEnvironmentCouplingSystem",
    "AdaptiveTimestepSystem",
]