#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境连续统处理器模块

将 EnvironmentalContinuumSystem 的 5 大物理机制拆分为独立处理器，
便于单元测试、性能调优和物理模型替换。
"""

import math
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

from core.world import World
from core.entity import Entity

from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import is_water_terrain

from .continuum_config import *


class ContinuumProcessor(ABC):
    """连续统处理器基类"""

    @abstractmethod
    def process(self, world: World, grid: Dict[Tuple[int, int], Entity],
                dt: float, bounds: Optional[Tuple] = None) -> None:
        """
        执行物理处理

        Args:
            world: ECS 世界
            grid: 网格索引 {(x,y): Entity}
            dt: 时间步长
            bounds: 边界范围 (min_x, max_x, min_y, max_y)
        """
        pass


class ThermalDiffusionProcessor(ContinuumProcessor):
    """热扩散处理器 — 傅里叶热传导"""

    def __init__(self, neighbor_offsets):
        self._neighbor_offsets = neighbor_offsets

    def process(self, world: World, grid: Dict, dt: float, bounds: Optional[Tuple] = None) -> None:
        fluxes = {}
        n_nei = len(self._neighbor_offsets)

        # 预计算所有实体的环境组件和地形组件
        env_cache = {}
        terrain_cache = {}
        for key, eid in grid.items():
            env_cache[key] = world.get_component(eid, EnvironmentComponent)
            terrain_cache[key] = world.get_component(eid, TerrainComponent)

        for (x, y), eid in grid.items():
            env = env_cache.get((x, y))
            terrain = terrain_cache.get((x, y))
            if env is None:
                continue

            # 植被阻尼 & 水域缓冲
            veg = terrain.vegetation_cover if terrain else 0.0
            is_water = terrain and is_water_terrain(terrain.terrain_type)
            veg_damp = 1.0 - VEGETATION_THERMAL_DAMPING * veg
            water_buf = WATER_THERMAL_BUFFER if is_water else 1.0

            net_temp = 0.0
            net_soil = 0.0

            for dx, dy in self._neighbor_offsets:
                nk = self._resolve_boundary((x + dx, y + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = env_cache.get(nk)
                n_terrain = terrain_cache.get(nk)
                if n_env is None:
                    continue

                n_veg = n_terrain.vegetation_cover if n_terrain else 0.0
                n_water = n_terrain and is_water_terrain(n_terrain.terrain_type)
                n_veg_damp = 1.0 - VEGETATION_THERMAL_DAMPING * n_veg
                n_water_buf = WATER_THERMAL_BUFFER if n_water else 1.0

                # 平均阻尼
                avg_damp = (veg_damp + n_veg_damp) / 2.0
                avg_buf = (water_buf + n_water_buf) / 2.0
                eff_temp = TEMP_DIFFUSION_COEFF * avg_damp * avg_buf

                # 大气温度
                dT = n_env.air_temperature - env.air_temperature
                flux = eff_temp * dT * dt
                flux = max(-MAX_TEMP_CHANGE_PER_STEP,
                           min(MAX_TEMP_CHANGE_PER_STEP, flux))
                net_temp += flux

                # 土壤温度
                eff_soil = SOIL_TEMP_DIFFUSION_COEFF * avg_damp
                dTs = n_env.soil_temperature - env.soil_temperature
                sflux = eff_soil * dTs * dt
                sflux = max(-MAX_TEMP_CHANGE_PER_STEP,
                            min(MAX_TEMP_CHANGE_PER_STEP, sflux))
                net_soil += sflux

            fluxes[(x, y)] = (net_temp, net_soil)

        # 应用通量
        for (x, y), (net_t, net_s) in fluxes.items():
            env = env_cache.get((x, y))
            if env is None:
                continue
            env.air_temperature += net_t / n_nei
            env.soil_temperature += net_s / n_nei
            env.air_temperature = max(-30.0, min(50.0, env.air_temperature))
            env.soil_temperature = max(-20.0, min(60.0, env.soil_temperature))

    def _resolve_boundary(self, coord, grid, bounds):
        """简化边界处理（仅 reflective）"""
        x, y = coord
        if bounds is not None:
            min_x, max_x, min_y, max_y = bounds
        else:
            xs = [k[0] for k in grid.keys()]
            ys = [k[1] for k in grid.keys()]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

        if x < min_x or x > max_x or y < min_y or y > max_y:
            return None
        return (x, y)


class HumidityDiffusionProcessor(ContinuumProcessor):
    """湿度扩散处理器"""

    def __init__(self, neighbor_offsets):
        self._neighbor_offsets = neighbor_offsets

    def process(self, world: World, grid: Dict, dt: float, bounds: Optional[Tuple] = None) -> None:
        fluxes = {}
        n_nei = len(self._neighbor_offsets)

        env_cache = {}
        terrain_cache = {}
        for key, eid in grid.items():
            env_cache[key] = world.get_component(eid, EnvironmentComponent)
            terrain_cache[key] = world.get_component(eid, TerrainComponent)

        for (x, y), eid in grid.items():
            env = env_cache.get((x, y))
            terrain = terrain_cache.get((x, y))
            if env is None:
                continue

            is_water = terrain and is_water_terrain(terrain.terrain_type)

            net_humid = 0.0
            net_moist = 0.0

            for dx, dy in self._neighbor_offsets:
                nk = self._resolve_boundary((x + dx, y + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = env_cache.get(nk)
                if n_env is None:
                    continue

                # 空气湿度扩散
                dh = n_env.air_humidity - env.air_humidity
                net_humid += HUMIDITY_DIFFUSION_COEFF * dh * dt

                # 土壤湿度扩散
                dm = n_env.soil_moisture - env.soil_moisture
                m_flux = SOIL_MOISTURE_DIFFUSION_COEFF * dm * dt
                m_flux = max(-MAX_MOISTURE_CHANGE_PER_STEP,
                             min(MAX_MOISTURE_CHANGE_PER_STEP, m_flux))
                net_moist += m_flux

                # 水域额外释放水汽
                if is_water and n_env.air_humidity < 0.95:
                    net_humid += 0.02 * (1.0 - n_env.air_humidity) * dt

            fluxes[(x, y)] = (net_humid, net_moist)

        for (x, y), (net_h, net_m) in fluxes.items():
            env = env_cache.get((x, y))
            if env is None:
                continue
            env.air_humidity += net_h / n_nei
            env.soil_moisture += net_m / n_nei
            env.air_humidity = max(0.01, min(1.0, env.air_humidity))
            env.soil_moisture = max(0.0, min(1.0, env.soil_moisture))

    def _resolve_boundary(self, coord, grid, bounds):
        x, y = coord
        if bounds is not None:
            min_x, max_x, min_y, max_y = bounds
        else:
            xs = [k[0] for k in grid.keys()]
            ys = [k[1] for k in grid.keys()]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

        if x < min_x or x > max_x or y < min_y or y > max_y:
            return None
        return (x, y)


class GravityWaterFlowProcessor(ContinuumProcessor):
    """重力水流处理器"""

    def process(self, world: World, grid: Dict, dt: float, bounds: Optional[Tuple] = None) -> None:
        # 预取海拔
        elevs = {}
        waters = {}
        for key, eid in grid.items():
            terrain = world.get_component(eid, TerrainComponent)
            elevs[key] = terrain.elevation if terrain else 0.0
            waters[key] = (terrain is not None
                           and is_water_terrain(terrain.terrain_type))

        # 计算净水分损失/增益
        losses = {key: 0.0 for key in grid}

        for (x, y), eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue

            cur_elev = elevs[(x, y)]
            is_water = waters[(x, y)]
            available = 0.5 if is_water else env.soil_moisture

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nk = (x + dx, y + dy)
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
                flow = min(flow, env.soil_moisture * 0.5)

                losses[(x, y)] -= flow
                losses[nk] += flow

        # 应用
        for key, delta in losses.items():
            if abs(delta) < 1e-10:
                continue
            eid = grid[key]
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            env.soil_moisture += delta
            env.soil_moisture = max(0.0, min(1.0, env.soil_moisture))


class WindAdvectionProcessor(ContinuumProcessor):
    """风驱平流处理器"""

    def __init__(self, neighbor_offsets, prevailing_wind_deg: float = 270.0):
        self._neighbor_offsets = neighbor_offsets
        self.prevailing_wind_direction = prevailing_wind_deg

    def process(self, world: World, grid: Dict, dt: float, bounds: Optional[Tuple] = None) -> None:
        wind_rad = math.radians(self.prevailing_wind_direction)
        wind_vx = -math.sin(wind_rad)
        wind_vy = -math.cos(wind_rad)

        fluxes = {}

        for (x, y), eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            net_t = 0.0
            net_h = 0.0

            for dx, dy in self._neighbor_offsets:
                nk = (x + dx, y + dy)
                if nk not in grid:
                    continue

                n_env = world.get_component(grid[nk], EnvironmentComponent)
                if n_env is None:
                    continue

                dist = math.sqrt(dx * dx + dy * dy)
                to_vx = -dx / dist
                to_vy = -dy / dist

                match = to_vx * wind_vx + to_vy * wind_vy
                if match <= 0:
                    continue

                strength = WIND_ADVECTION_COEFF * env.wind_speed * match * dt
                strength = min(strength, 0.3)

                net_t += strength * (n_env.air_temperature - env.air_temperature)
                net_h += strength * (n_env.air_humidity - env.air_humidity)

            fluxes[(x, y)] = (net_t, net_h)

        n_nei = len(self._neighbor_offsets)
        for (x, y), (net_t, net_h) in fluxes.items():
            eid = grid[(x, y)]
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            env.air_temperature += net_t / n_nei
            env.air_humidity += net_h / n_nei
            env.air_temperature = max(-30.0, min(50.0, env.air_temperature))
            env.air_humidity = max(0.01, min(1.0, env.air_humidity))


class SelfRecoveryProcessor(ContinuumProcessor):
    """生态自恢复处理器"""

    def process(self, world: World, grid: Dict, dt: float, bounds: Optional[Tuple] = None) -> None:
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 顶极状态
            if terrain and terrain.terrain_type:
                climax = TERRAIN_CLIMAX_STATE.get(
                    terrain.terrain_type, DEFAULT_CLIMAX
                )
            else:
                climax = DEFAULT_CLIMAX

            c_t, c_h, c_m, c_n, c_p, c_k = climax

            # 气温
            d = c_t - env.air_temperature
            env.air_temperature += RECOVERY_RATE_TEMPERATURE * self._sig(d) * d * dt

            # 空气湿度
            d = c_h - env.air_humidity
            env.air_humidity += RECOVERY_RATE_HUMIDITY * self._sig(d) * d * dt
            env.air_humidity = max(0.01, min(1.0, env.air_humidity))

            # 土壤湿度
            d = c_m - env.soil_moisture
            env.soil_moisture += RECOVERY_RATE_MOISTURE * self._sig(d) * d * dt
            env.soil_moisture = max(0.0, min(1.0, env.soil_moisture))

            # 氮
            d = c_n - env.nitrogen
            env.nitrogen += RECOVERY_RATE_NITROGEN * self._sig(d) * d * dt
            env.nitrogen = max(0.0, min(200.0, env.nitrogen))

            # 磷
            d = c_p - env.phosphorus
            env.phosphorus += RECOVERY_RATE_PHOSPHORUS * self._sig(d) * d * dt
            env.phosphorus = max(0.0, min(100.0, env.phosphorus))

            # 钾
            d = c_k - env.potassium
            env.potassium += RECOVERY_RATE_POTASSIUM * self._sig(d) * d * dt
            env.potassium = max(0.0, min(200.0, env.potassium))

    @staticmethod
    def _sig(dev: float) -> float:
        """Sigmoid 形状函数"""
        if dev == 0:
            return 0.0
        x = RECOVERY_SIGMOID_K * abs(dev)
        s = 2.0 / (1.0 + math.exp(-x)) - 1.0
        return s if dev > 0 else -s
