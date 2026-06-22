#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水循环系统 — 基于连续统框架的统一扩散

v4.1 重构：拆分核心逻辑到子模块

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

版本: v4.1
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

from environment.hydrology.systems.evaporation_calculator import EvaporationCalculator
from environment.hydrology.systems.infiltration_calculator import InfiltrationCalculator
from environment.hydrology.systems.runoff_calculator import RunoffCalculator
from environment.hydrology.systems.groundwater_exchanger import GroundwaterExchanger
from environment.hydrology.systems.river_flow_calculator import RiverFlowCalculator

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
    RIVER_FLOW_RATE = 0.1          # 河流流速 (格/h)

    def __init__(self):
        super().__init__()
        self._evaporation = EvaporationCalculator(self.EVAPORATION_RATE)
        self._infiltration = InfiltrationCalculator(self.INFILTRATION_RATE)
        self._runoff = RunoffCalculator(self.RUNOFF_THRESHOLD)
        self._groundwater = GroundwaterExchanger(self.GROUNDWATER_DISCHARGE)
        self._river_flow = RiverFlowCalculator(self.RIVER_FLOW_RATE)

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行水循环更新"""
        # 获取环境组件
        env = world.get_environment()
        if env is None:
            return

        # 获取降雨数据
        rainfall = getattr(env, 'rainfall', 0.0)
        temperature = getattr(env, 'temperature', 20.0)

        # 处理所有水体
        for entity, (water, space) in world.get_components(WaterBodyComponent, SpaceComponent):
            # 降雨补充
            if rainfall > 0:
                water.volume += rainfall * dt * 0.1  # 10% 降雨进入水体
                water.volume = min(water.volume, water.max_volume)

            # 蒸发
            self._evaporation.calculate(water, temperature, dt)

        # 处理所有土壤
        for entity, (soil, space) in world.get_components(SoilComponent, SpaceComponent):
            # 降雨补充
            if rainfall > 0:
                soil.moisture += rainfall * dt * 0.5  # 50% 降雨进入土壤
                soil.moisture = min(soil.moisture, soil.max_moisture)

            # 渗透
            self._infiltration.calculate(soil, world, entity, dt)

            # 径流
            self._runoff.calculate(soil, world, entity, dt)

        # 地下水交换
        self._groundwater.exchange(world, dt)

        # 河流流动
        self._river_flow.calculate(world, dt)

        # 更新环境湿度
        if hasattr(env, 'humidity'):
            total_evaporation = self._calculate_total_evaporation(world)
            env.humidity += total_evaporation * 0.1
            env.humidity = min(1.0, max(0.0, env.humidity))

    def _calculate_total_evaporation(self, world: World) -> float:
        """计算总蒸发量"""
        total = 0.0
        for entity, (water,) in world.get_components(WaterBodyComponent):
            total += getattr(water, 'evaporated_this_tick', 0.0)
        return total
