#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水循环系统 — 基于连续统框架的统一扩散

v4.0 重构：使用 continuum_utils 的通用扩散内核，
替代原有的独立距离扫描实现。

物理模型:
    降雨: 直接补充土壤和水体
    蒸发: 水体 → 大气湿度
    渗透: 土壤 → 地下水 (达西定律简化)
    径流: 土壤饱和 → 重力水流 (使用 continuum 重力水流模型)
    地下水交换: 地下水 ↔ 水体 (扩散模型)
    河流流动: 上游 → 下游 (连通图)

参数:
    蒸发率 = 0.001 /h
    渗透率 = 0.01 /h
    径流阈值 = 0.9 (土壤饱和度)
    地下水排泄 = 0.005 /h

与其他模块的关系:
    - continuum/: 使用通用扩散内核 (compute_diffusion_flux, resolve_boundary)
    - environment/: 读取降雨/温度，写入湿度
    - soil/: 读取/写入土壤湿度
    - hydrology/: 读取/写入水体/地下水

版本: v4.0
"""

import logging
import math
from typing import Dict, Tuple, Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.hydrology.components.water_body_component import WaterBodyComponent
from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent

from environment.terrain.components.terrain_component import TerrainComponent
from environment.continuum.continuum_utils import (
    resolve_boundary,
    compute_diffusion_flux,
    clamp,
    get_neighbor_offsets,
)
from environment.continuum.continuum_config import (
    WATER_FLOW_BASE_RATE,
    WATER_FLOW_SLOPE_EXPONENT,
)

logger = logging.getLogger(__name__)


class WaterCycleSystem(System):
    """
    水循环系统

    使用连续统框架处理:
    1. 降雨补充 (直接)
    2. 蒸发 (水体 → 大气)
    3. 渗透 (土壤 → 地下水)
    4. 径流 (重力水流，使用 continuum 模型)
    5. 地下水交换 (扩散模型)
    6. 河流流动 (连通图)

    在管线中应运行在 EnvironmentalContinuumSystem 之后。
    """

    tick_interval = 5  # 每5帧执行一次

    # 水循环参数
    EVAPORATION_RATE = 0.001       # 基础蒸发速率 (1/h)
    INFILTRATION_RATE = 0.01       # 渗透速率 (1/h)
    RUNOFF_THRESHOLD = 0.9         # 土壤饱和度径流阈值
    GROUNDWATER_DISCHARGE = 0.005  # 地下水排泄速率 (1/h)
    MAX_MOISTURE_CHANGE = 0.05     # 最大单步水分变化

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新水循环"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 1. 处理降雨
        self._process_rainfall(world, grid, dt)

        # 2. 处理蒸发
        self._process_evaporation(world, grid, dt)

        # 3. 处理渗透和径流
        self._process_infiltration_and_runoff(world, grid, dt, bounds)

        # 4. 处理地下水交换
        self._process_groundwater_exchange(world, grid, dt, bounds)

        # 5. 处理河流流动
        self._process_river_flow(world, grid, dt)

    def _process_rainfall(self, world: World, grid: Dict, dt: float) -> None:
        """降雨补充土壤和水体"""
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            soil = world.get_component(eid, SoilComponent)
            if env is None or soil is None:
                continue

            rainfall = env.rainfall * dt
            if rainfall <= 0:
                continue

            # 70% 降雨进入土壤
            soil_infiltration = rainfall * 0.7
            soil.moisture = min(1.0, soil.moisture + soil_infiltration * 0.01)

            # 30% 形成地表水（添加到最近水体）
            surface_water = rainfall * 0.3
            space = world.get_component(eid, SpaceComponent)
            if space is not None:
                self._add_to_nearest_water_body(world, grid, space, surface_water)

    def _process_evaporation(self, world: World, grid: Dict, dt: float) -> None:
        """水体蒸发"""
        for key, eid in grid.items():
            water = world.get_component(eid, WaterBodyComponent)
            if water is None:
                continue

            # 蒸发量与温度、表面积相关
            evap = water.evaporation * dt
            water.volume = max(0.0, water.volume - evap)

            # 更新环境湿度
            env = world.get_component(eid, EnvironmentComponent)
            if env is not None:
                env.air_humidity = min(1.0, env.air_humidity + evap * 0.0001)

    def _process_infiltration_and_runoff(self, world: World, grid: Dict, dt: float,
                                        bounds: Optional[Tuple]) -> None:
        """土壤渗透和径流 — 使用重力水流模型

        物理模型:
            渗透: 土壤水 → 地下水 (达西定律简化)
            径流: 使用 continuum 重力水流模型 (海拔梯度驱动)
        """
        # 预取海拔
        elevs = {}
        for key, eid in grid.items():
            terrain = world.get_component(eid, TerrainComponent)
            elevs[key] = terrain.elevation if terrain else 0.0

        # 计算径流 (重力水流)
        runoff = {key: 0.0 for key in grid.keys()}

        for key, eid in grid.items():
            soil = world.get_component(eid, SoilComponent)
            env = world.get_component(eid, EnvironmentComponent)
            if soil is None or env is None:
                continue

            # 渗透：土壤水向地下水补给
            groundwater = world.get_component(eid, GroundwaterComponent)
            if groundwater is not None and soil.moisture > groundwater.porosity:
                excess = (soil.moisture - groundwater.porosity) * self.INFILTRATION_RATE * dt
                soil.moisture -= excess * 0.01
                groundwater.water_table += excess * 0.1

            # 径流：使用 continuum 重力水流模型
            if soil.moisture > self.RUNOFF_THRESHOLD:
                cur_elev = elevs[key]
                available = soil.moisture - self.RUNOFF_THRESHOLD

                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0),
                               (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    nk = (key[0] + dx, key[1] + dy)
                    if nk not in grid:
                        continue

                    # 只流向下坡
                    elev_diff = cur_elev - elevs[nk]
                    if elev_diff <= 0:
                        continue

                    dist = math.sqrt(dx*dx + dy*dy)
                    slope = elev_diff / max(dist, 0.1)

                    flow = (
                        WATER_FLOW_BASE_RATE
                        * (slope ** WATER_FLOW_SLOPE_EXPONENT)
                        * available
                        * dt
                    )
                    flow = min(flow, available * 0.5)

                    runoff[key] -= flow
                    runoff[nk] += flow

        # 应用径流
        for key, delta in runoff.items():
            if abs(delta) < 1e-10:
                continue
            soil = world.get_component(grid[key], SoilComponent)
            if soil is None:
                continue
            soil.moisture += delta
            soil.moisture = clamp(soil.moisture, 0.0, 1.0)

    def _process_groundwater_exchange(self, world: World, grid: Dict, dt: float,
                                     bounds: Optional[Tuple]) -> None:
        """地下水与水体交换 — 使用扩散模型"""
        n_nei = len(self._neighbor_offsets)
        net_fluxes = {key: 0.0 for key in grid.keys()}

        for key, eid in grid.items():
            groundwater = world.get_component(eid, GroundwaterComponent)
            if groundwater is None:
                continue

            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_groundwater = world.get_component(grid[nk], GroundwaterComponent)
                if n_groundwater is None:
                    continue

                flux = compute_diffusion_flux(
                    groundwater.water_table, n_groundwater.water_table,
                    self.GROUNDWATER_DISCHARGE, dt, self.MAX_MOISTURE_CHANGE
                )

                net_fluxes[key] += flux
                net_fluxes[nk] -= flux

        # 应用净通量
        for key, net_flux in net_fluxes.items():
            groundwater = world.get_component(grid[key], GroundwaterComponent)
            if groundwater is None:
                continue
            groundwater.water_table += net_flux / n_nei

    def _process_river_flow(self, world: World, grid: Dict, dt: float) -> None:
        """河流流动（上游向下游）"""
        for key, eid in grid.items():
            water = world.get_component(eid, WaterBodyComponent)
            if water is None or water.body_type != "river":
                continue

            # 计算流出量
            if water.flow_rate > 0 and water.connected_to:
                outflow = water.flow_rate * dt
                water.volume = max(0.0, water.volume - outflow)

                # 分配到下游水体
                for downstream_id in water.connected_to:
                    downstream = world.query_entity(downstream_id)
                    if downstream is not None:
                        ds_water = world.get_component(downstream, WaterBodyComponent)
                        if ds_water is not None:
                            ds_water.volume = min(ds_water.max_volume, ds_water.volume + outflow / len(water.connected_to))

    def _add_to_nearest_water_body(self, world: World, grid: Dict, space: SpaceComponent, amount: float) -> None:
        """将水量添加到最近的水体"""
        nearest = None
        nearest_dist = float('inf')

        for key, eid in grid.items():
            water = world.get_component(eid, WaterBodyComponent)
            wb_space = world.get_component(eid, SpaceComponent)
            if water is None or wb_space is None:
                continue
            dist = ((space.x - wb_space.x) ** 2 + (space.y - wb_space.y) ** 2) ** 0.5
            if dist < nearest_dist and dist < 50:  # 50单位范围内
                nearest_dist = dist
                nearest = water

        if nearest is not None:
            nearest.volume = min(nearest.max_volume, nearest.volume + amount)

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引 — 包含所有有 SpaceComponent 的实体"""
        grid = {}
        for entity, (space,) in world.get_components(SpaceComponent):
            if space is None:
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
