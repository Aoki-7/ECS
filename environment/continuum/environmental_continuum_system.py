"""
环境连续统系统 — 相邻单元格物质-能量交换

【核心概念】
    每个环境单元格不是孤立的。相邻单元格通过扩散、平流、重力水流
    互相影响，使 10×10 网格表现为一个有弹性的连续体。
    即使局部受到扰动（人为破坏/火灾/污染），邻近区域的物质-能量
    会自然流入，体现环境的自适应性和恢复性。

【物理模型 — 5 大机制】
    1. 🌡 热扩散 (Thermal Diffusion)
    2. 💧 湿度扩散 (Humidity Diffusion)
    3. 🌊 重力水流 (Gravity Water Flow)
    4. 🌬 风驱平流 (Wind-driven Advection)
    5. 🌿 生态自恢复 (Ecological Self-Recovery)

v3.8 变更：
- 5 大机制拆分为独立处理器类
- 便于单元测试和物理模型替换
"""

from typing import Dict, Optional, Tuple

from core.world import World
from core.system import System
from core.entity import Entity

from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent

from .continuum_config import *
from .continuum_processors import (
    ThermalDiffusionProcessor,
    HumidityDiffusionProcessor,
    GravityWaterFlowProcessor,
    WindAdvectionProcessor,
    SelfRecoveryProcessor,
)


class EnvironmentalContinuumSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    环境连续统系统

    在管线中应运行在 EnvironmentSyncSystem 之后，
    作为所有环境更新的"空间平滑"步骤。
    """

    def __init__(
        self,
        neighborhood: str = "moore",
        boundary: str = "reflective",
        prevailing_wind_deg: float = 270.0,
    ):
        super().__init__()
        self.neighborhood = neighborhood
        self.boundary = boundary
        self.prevailing_wind_direction = prevailing_wind_deg
        self._neighbor_offsets = (
            NEIGHBOR_OFFSETS_MOORE if neighborhood == "moore" else NEIGHBOR_OFFSETS_VON_NEUMANN
        )

        # 初始化处理器
        self._processors = [
            ThermalDiffusionProcessor(self._neighbor_offsets),
            HumidityDiffusionProcessor(self._neighbor_offsets),
            GravityWaterFlowProcessor(),
            WindAdvectionProcessor(self._neighbor_offsets, prevailing_wind_deg),
            SelfRecoveryProcessor(),
        ]

    # ========================
    # 主更新入口
    # ========================

    def update(self, world: World, delta_hours: float) -> None:
        """主更新：对网格执行所有物理过程"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 顺序执行 5 大物理过程
        for processor in self._processors:
            processor.process(world, grid, delta_hours, bounds)

    # ========================
    # 网格构建
    # ========================

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引：{(x, y): Entity}"""
        grid: Dict[Tuple[int, int], Entity] = {}
        for entity, (space, env) in world.get_components(SpaceComponent, EnvironmentComponent):
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
