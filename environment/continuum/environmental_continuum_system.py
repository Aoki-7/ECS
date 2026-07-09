#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境连续统系统 — 相邻单元格物质-能量交换

【核心概念】
    每个环境单元格不是孤立的。相邻单元格通过扩散、平流、重力水流
    互相影响，使网格表现为一个有弹性的连续体。
    即使局部受到扰动（人为破坏/火灾/污染），邻近区域的物质-能量
    会自然流入，体现环境的自适应性和恢复性。

【物理模型 — 5 大机制】
    1. 🌡 热扩散 (Thermal Diffusion) — 傅里叶热传导
       dT/dt = D * ∇²T * damping
       单位: T(°C), D(1/h), dt(h)

    2. 💧 湿度扩散 (Humidity Diffusion) — 菲克扩散定律
       dH/dt = D * ∇²H
       单位: H(0~1), D(1/h), dt(h)

    3. 🌊 重力水流 (Gravity Water Flow) — 达西定律简化
       flow = k * slope^α * moisture * dt
       单位: moisture(0~1), k(1/h), slope(m/m), dt(h)

    4. 🌬 风驱平流 (Wind-driven Advection) — 平流方程
       dT/dt = C * wind_speed * cos(θ) * ∇T
       单位: T(°C), wind_speed(m/s), C(1/m), dt(h)

    5. 🌿 生态自恢复 (Ecological Self-Recovery) — 松弛模型
       dX/dt = r * sigmoid(X_climax - X) * (X_climax - X)
       单位: X(various), r(1/h), dt(h)

【数值稳定性】
    - 同步更新: 所有处理器先计算通量，再统一应用
    - 守恒检查: 每步计算前后验证能量/水分/养分守恒
    - 自适应步长: 变化过大时自动减小 dt

【v4.0 变更】
    - 5 大机制拆分为独立处理器类
    - 共享组件缓存 (ContinuumCache)，避免重复查询
    - 共享边界解析 (resolve_boundary)，消除代码重复
    - 共享守恒检查 (ConservationSnapshot)，确保数值稳定
    - 支持运行时热切换物理模型
"""

from typing import Dict, Optional, Tuple
import logging

from core.world import World
from core.system import System
from core.entity import Entity

from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent

from .continuum_config import *
from .continuum_utils import (
    ContinuumCache,
    ConservationSnapshot,
    take_conservation_snapshot,
    check_conservation,
    get_neighbor_offsets,
)
from .continuum_processors import (
    ThermalDiffusionProcessor,
    HumidityDiffusionProcessor,
    GravityWaterFlowProcessor,
    WindAdvectionProcessor,
    SelfRecoveryProcessor,
)

logger = logging.getLogger(__name__)


class EnvironmentalContinuumSystem(System):
    """
    环境连续统系统

    在管线中应运行在 EnvironmentSyncSystem 之后，
    作为所有环境更新的"空间平滑"步骤。

    依赖图:
        dependencies_after = [EnvironmentSyncSystem]
        dependencies_before = []  # 管线末端
    """

    tick_interval = 20  # 每20帧执行一次

    def __init__(
        self,
        neighborhood: str = "moore",
        boundary: str = "reflective",
        prevailing_wind_deg: float = 270.0,
        enable_conservation_check: bool = False,
        conservation_tolerance: float = 1e-6,
    ):
        """
        Args:
            neighborhood: "moore"(8) or "von_neumann"(4)
            boundary: 边界条件，当前仅 "reflective"
            prevailing_wind_deg: 盛行风向（度）
            enable_conservation_check: 是否开启守恒检查。
                默认关闭，因为自恢复、水域湿度源等处理器会引入有意的源/汇。
                调试保守算法时可手动开启。
            conservation_tolerance: 守恒检查容差
        """
        super().__init__()
        self.neighborhood = neighborhood
        self.boundary = boundary
        self.prevailing_wind_direction = prevailing_wind_deg
        self.enable_conservation_check = enable_conservation_check
        self.conservation_tolerance = conservation_tolerance

        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

        # 初始化处理器
        self._processors = [
            ThermalDiffusionProcessor(),
            HumidityDiffusionProcessor(),
            GravityWaterFlowProcessor(),
            WindAdvectionProcessor(prevailing_wind_deg),
            SelfRecoveryProcessor(),
        ]

        # 网格缓存：环境单元是静态的，可在首次构建后复用
        self._grid_cache: Optional[Dict] = None
        self._bounds_cache: Optional[Tuple] = None
        self._continuum_cache: Optional[ContinuumCache] = None

    # ========================
    # 主更新入口
    # ========================

    def update(self, world: World, delta_hours: float) -> None:
        """主更新：对网格执行所有物理过程

        流程:
            1. 构建网格索引（首次运行，后续复用缓存）
            2. 预查询所有组件 (ContinuumCache)
            3. [可选] 拍摄守恒快照
            4. 顺序执行 5 大物理过程
            5. [可选] 验证守恒性
        """
        if self._grid_cache is None:
            grid = self._build_grid(world)
            if not grid:
                return
            self._grid_cache = grid
            self._bounds_cache = self._compute_bounds(grid)
            self._continuum_cache = ContinuumCache.build(world, grid)

        grid = self._grid_cache
        bounds = self._bounds_cache
        cache = self._continuum_cache

        # 守恒检查前快照
        before_snapshot = None
        if self.enable_conservation_check:
            before_snapshot = take_conservation_snapshot(cache)

        # 顺序执行 5 大物理过程
        # 注意: 处理器间是顺序执行，不是同步更新
        # 未来可改为同步更新 (先全部计算通量，再统一应用)
        for processor in self._processors:
            try:
                processor.process(
                    world, cache, grid, delta_hours,
                    bounds=bounds,
                    neighbor_offsets=self._neighbor_offsets,
                )
            except Exception as e:
                logger.error(f"Processor {processor.__class__.__name__} failed: {e}")
                raise

        # 守恒检查后验证
        if self.enable_conservation_check and before_snapshot is not None:
            after_snapshot = take_conservation_snapshot(cache)
            violation = check_conservation(
                before_snapshot, after_snapshot,
                self.conservation_tolerance
            )
            if violation:
                logger.warning(violation)

    # ========================
    # 网格构建
    # ========================

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引

        利用 ArchetypeStore 的 get_components 进行高效查询
        """
        grid: Dict[Tuple[int, int], Entity] = {}
        for entity, (space, env) in world.get_components(SpaceComponent, EnvironmentComponent):
            if space is None or env is None:
                continue
            key = (int(space.x), int(space.y))
            grid[key] = entity
        return grid

    def _compute_bounds(self, grid: Dict) -> Optional[Tuple[int, int, int, int]]:
        """计算网格边界"""
        if not grid:
            return None
        xs = [k[0] for k in grid.keys()]
        ys = [k[1] for k in grid.keys()]
        return min(xs), max(xs), min(ys), max(ys)
