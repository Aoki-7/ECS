#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火灾蔓延系统 — 相邻单元格热传递与燃烧传播

v4.0 新增 — Phase 2

物理模型:
    1. 热源: 燃烧实体释放热量 (温度升高)
    2. 热传递: 使用连续统热扩散模型 (已存在)
    3. 点燃条件: 邻居温度 > 燃点 + 可燃物 + 湿度抑制
    4. 蔓延: 风加速蔓延 (顺风方向权重增加)
    5. 熄灭: 燃料耗尽 / 降雨 / 湿度高

参数:
    IGNITION_TEMP = 300°C (燃点)
    BURNING_HEAT = 500°C (燃烧温度)
    SPREAD_RATE = 0.1 /h (基础蔓延速率)
    WIND_BOOST = 2.0 (风加速倍数)
    HUMIDITY_INHIBITION = 0.5 (湿度抑制系数)

与其他模块的关系:
    - continuum/: 使用热扩散模型 (ThermalDiffusionProcessor)
    - environment/: 读取温度/湿度/降雨，写入温度
    - plant/: 读取植被覆盖 (燃料来源)
    - biology/: 实体死亡 (火灾致死)

版本: v4.0
"""

import logging
import math
from typing import Dict, Tuple, Optional

from core.system import System
from core.world import World
from core.entity import Entity

from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from space.space_component import SpaceComponent

from environment.continuum.continuum_utils import (
    resolve_boundary,
    clamp,
    get_neighbor_offsets,
)

logger = logging.getLogger(__name__)


class FireSpreadSystem(System):
    """
    火灾蔓延系统

    使用连续统框架:
    1. 燃烧实体作为热源 (温度升高)
    2. 热扩散自动传播热量 (已有 ThermalDiffusionProcessor)
    3. 本系统检查点燃条件和蔓延逻辑

    在管线中应运行在 ThermalDiffusionProcessor 之后。
    """

    tick_interval = 5  # 每5帧执行一次

    # 火灾参数
    IGNITION_TEMP = 300.0      # 燃点 (°C)
    BURNING_TEMP = 500.0       # 燃烧温度 (°C)
    SPREAD_RATE = 0.1          # 基础蔓延速率 (1/h)
    WIND_BOOST = 2.0         # 风加速倍数
    HUMIDITY_INHIBITION = 0.5  # 湿度抑制系数
    FUEL_CONSUMPTION = 0.01    # 燃料消耗速率 (1/h)

    def __init__(self, neighborhood: str = "moore"):
        super().__init__()
        self._neighbor_offsets = get_neighbor_offsets(neighborhood)

    def update(self, world: World, dt: float) -> None:
        """更新火灾蔓延"""
        grid = self._build_grid(world)
        if not grid:
            return

        bounds = self._compute_bounds(grid)

        # 1. 处理燃烧中的火源
        self._process_burning(world, grid, dt, bounds)

        # 2. 检查点燃条件
        self._check_ignition(world, grid, dt, bounds)

        # 3. 处理熄灭
        self._process_extinguishing(world, grid, dt)

    def _process_burning(self, world: World, grid: Dict, dt: float,
                         bounds: Optional[Tuple]) -> None:
        """处理燃烧中的火源"""
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 检查是否正在燃烧 (温度 > 燃点)
            if env.air_temperature < self.IGNITION_TEMP:
                continue

            # 燃烧释放热量
            env.air_temperature = min(self.BURNING_TEMP, env.air_temperature + 50.0 * dt)

            # 消耗燃料 (植被)
            if terrain is not None and terrain.vegetation_cover > 0:
                terrain.vegetation_cover = max(0.0, terrain.vegetation_cover - self.FUEL_CONSUMPTION * dt)

            # 产生烟雾 (可扩展)
            logger.debug(f"Fire burning at {key}: temp={env.air_temperature:.1f}°C")

    def _check_ignition(self, world: World, grid: Dict, dt: float,
                        bounds: Optional[Tuple]) -> None:
        """检查点燃条件"""
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 已经在燃烧
            if env.air_temperature >= self.IGNITION_TEMP:
                continue

            # 检查邻居火源
            for dx, dy in self._neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = world.get_component(grid[nk], EnvironmentComponent)
                if n_env is None:
                    continue

                # 邻居温度足够高
                if n_env.air_temperature < self.IGNITION_TEMP:
                    continue

                # 计算点燃概率
                ignition_prob = self._compute_ignition_probability(env, terrain, n_env)

                if ignition_prob > 0.5:  # 阈值
                    env.air_temperature = self.IGNITION_TEMP
                    logger.info(f"Fire ignited at {key} from neighbor {nk}")
                    break

    def _compute_ignition_probability(self, env: EnvironmentComponent,
                                      terrain: Optional[TerrainComponent],
                                      neighbor_env: EnvironmentComponent) -> float:
        """计算点燃概率

        因素:
            - 邻居温度 (越高越容易点燃)
            - 湿度 (越高越不容易点燃)
            - 植被覆盖 (燃料越多越容易点燃)
            - 风速 (加速蔓延)
        """
        # 基础概率 (基于温度差)
        temp_factor = (neighbor_env.air_temperature - self.IGNITION_TEMP) / self.IGNITION_TEMP
        temp_factor = clamp(temp_factor, 0.0, 1.0)

        # 湿度抑制
        humidity_factor = 1.0 - self.HUMIDITY_INHIBITION * env.air_humidity
        humidity_factor = clamp(humidity_factor, 0.0, 1.0)

        # 燃料因素
        fuel_factor = terrain.vegetation_cover if terrain else 0.0

        # 风加速
        wind_factor = 1.0 + self.WIND_BOOST * env.wind_speed

        return temp_factor * humidity_factor * fuel_factor * wind_factor

    def _process_extinguishing(self, world: World, grid: Dict, dt: float) -> None:
        """处理熄灭"""
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 不在燃烧
            if env.air_temperature < self.IGNITION_TEMP:
                continue

            # 降雨熄灭
            if env.rainfall > 5.0:  # 大雨
                env.air_temperature = max(env.air_temperature - 100.0 * dt, 20.0)
                logger.info(f"Fire extinguished by rain at {key}")
                continue

            # 燃料耗尽
            if terrain is not None and terrain.vegetation_cover < 0.01:
                env.air_temperature = max(env.air_temperature - 50.0 * dt, 20.0)
                logger.info(f"Fire extinguished by fuel depletion at {key}")
                continue

            # 湿度高
            if env.air_humidity > 0.9:
                env.air_temperature = max(env.air_temperature - 30.0 * dt, 20.0)

    def _build_grid(self, world: World) -> Dict[Tuple[int, int], Entity]:
        """构建网格索引"""
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
