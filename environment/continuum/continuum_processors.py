#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境连续统处理器模块

将 EnvironmentalContinuumSystem 的 5 大物理机制拆分为独立处理器，
使用共享工具 (continuum_utils) 避免代码重复。

数学模型:

1. 热扩散 (Thermal Diffusion)
   物理: 傅里叶热传导定律
   公式: dT/dt = D * ∇²T
   离散: ΔT = D * (T_neighbor - T_self) * dt / n_neighbors
   单位: T (°C), D (1/h), dt (h)

2. 湿度扩散 (Humidity Diffusion)
   物理: 菲克扩散定律
   公式: dH/dt = D * ∇²H
   离散: ΔH = D * (H_neighbor - H_self) * dt / n_neighbors
   单位: H (0~1), D (1/h), dt (h)

3. 重力水流 (Gravity Water Flow)
   物理: 达西定律简化
   公式: flow = k * slope^α * moisture * dt
   离散: ΔM = flow (下坡流出) / n_downhill
   单位: M (0~1), k (1/h), slope (m/m), dt (h)

4. 风驱平流 (Wind Advection)
   物理: 平流方程
   公式: dT/dt = -v · ∇T
   离散: ΔT = C * wind_speed * cos(θ) * (T_neighbor - T_self) * dt / n_neighbors
   单位: T (°C), v (m/s), C (1/m), dt (h)

5. 生态自恢复 (Ecological Self-Recovery)
   物理: 松弛模型 (向顶极状态恢复)
   公式: dX/dt = r * sigmoid(X_climax - X) * (X_climax - X)
   离散: ΔX = r * sigmoid(d) * d * dt
   单位: X (various), r (1/h), dt (h)
"""

import math
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

from core.sqrt_cache import cached_sqrt, cached_distance
from core.world import World
from core.entity import Entity

from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import is_water_terrain

from .continuum_config import *
from .continuum_utils import (
    ContinuumCache,
    resolve_boundary,
    compute_diffusion_flux,
    apply_diffusion_fluxes,
    sigmoid_factor,
    clamp,
)


class ContinuumProcessor(ABC):
    """连续统处理器基类

    所有处理器共享:
    - 组件缓存 (通过 ContinuumCache)
    - 边界解析 (通过 resolve_boundary)
    - 守恒检查 (通过 ConservationSnapshot)
    """

    @abstractmethod
    def process(self, world: World, cache: ContinuumCache, grid: Dict[Tuple[int, int], Entity],
                dt: float, bounds: Optional[Tuple] = None,
                neighbor_offsets: Optional[list] = None) -> None:
        """
        执行物理处理

        Args:
            world: ECS 世界
            cache: 组件缓存 (预查询)
            grid: 网格索引 {(x,y): Entity}
            dt: 时间步长 (hours)
            bounds: 边界范围 (min_x, max_x, min_y, max_y)
            neighbor_offsets: 邻居偏移列表
        """
        pass


class ThermalDiffusionProcessor(ContinuumProcessor):
    """热扩散处理器 — 傅里叶热传导

    物理模型:
        大气温度: dT_air/dt = D_air * ∇²T_air * vegetation_damping * water_buffer
        土壤温度: dT_soil/dt = D_soil * ∇²T_soil * vegetation_damping

    参数:
        D_air = 0.15 /h (空气扩散系数)
        D_soil = 0.03 /h (土壤扩散系数)
        vegetation_damping = 1 - 0.5 * cover (植被阻尼)
        water_buffer = 0.3 (水域热缓冲)

    单位:
        T: °C
        D: 1/h
        dt: h
    """

    def process(self, world: World, cache: ContinuumCache, grid: Dict, dt: float,
                bounds: Optional[Tuple] = None,
                neighbor_offsets: Optional[list] = None) -> None:
        if neighbor_offsets is None:
            neighbor_offsets = NEIGHBOR_OFFSETS_MOORE

        n_nei = len(neighbor_offsets)
        fluxes_temp = {}
        fluxes_soil = {}

        for key in cache.grid_keys:
            env = cache.get_env(key)
            terrain = cache.get_terrain(key)
            if env is None:
                continue

            # 植被阻尼 & 水域缓冲
            veg = terrain.vegetation_cover if terrain else 0.0
            is_water = terrain and is_water_terrain(terrain.terrain_type)
            veg_damp = 1.0 - VEGETATION_THERMAL_DAMPING * veg
            water_buf = WATER_THERMAL_BUFFER if is_water else 1.0

            net_temp = 0.0
            net_soil = 0.0

            for dx, dy in neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = cache.get_env(nk)
                n_terrain = cache.get_terrain(nk)
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
                eff_soil = SOIL_TEMP_DIFFUSION_COEFF * avg_damp

                # 大气温度扩散
                net_temp += compute_diffusion_flux(
                    env.air_temperature, n_env.air_temperature,
                    eff_temp, dt, MAX_TEMP_CHANGE_PER_STEP
                )

                # 土壤温度扩散
                net_soil += compute_diffusion_flux(
                    env.soil_temperature, n_env.soil_temperature,
                    eff_soil, dt, MAX_TEMP_CHANGE_PER_STEP
                )

            fluxes_temp[key] = net_temp
            fluxes_soil[key] = net_soil

        # 应用通量
        apply_diffusion_fluxes(
            fluxes_temp, cache,
            lambda e: e.air_temperature,
            lambda e, v: setattr(e, 'air_temperature', v),
            n_nei, -30.0, 50.0
        )
        apply_diffusion_fluxes(
            fluxes_soil, cache,
            lambda e: e.soil_temperature,
            lambda e, v: setattr(e, 'soil_temperature', v),
            n_nei, -20.0, 60.0
        )


class HumidityDiffusionProcessor(ContinuumProcessor):
    """湿度扩散处理器 — 菲克扩散定律

    物理模型:
        空气湿度: dH_air/dt = D_humid * ∇²H_air
        土壤水分: dM_soil/dt = D_moist * ∇²M_soil (坡度修正)

    参数:
        D_humid = 0.12 /h (空气湿度扩散系数)
        D_moist = 0.08 /h (土壤水分扩散系数)

    单位:
        H: 0~1 (相对湿度)
        M: 0~1 (土壤水分)
        D: 1/h
        dt: h
    """

    def process(self, world: World, cache: ContinuumCache, grid: Dict, dt: float,
                bounds: Optional[Tuple] = None,
                neighbor_offsets: Optional[list] = None) -> None:
        if neighbor_offsets is None:
            neighbor_offsets = NEIGHBOR_OFFSETS_MOORE

        n_nei = len(neighbor_offsets)
        fluxes_humid = {}
        fluxes_moist = {}

        for key in cache.grid_keys:
            env = cache.get_env(key)
            terrain = cache.get_terrain(key)
            if env is None:
                continue

            is_water = terrain and is_water_terrain(terrain.terrain_type)
            net_humid = 0.0
            net_moist = 0.0

            for dx, dy in neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = cache.get_env(nk)
                if n_env is None:
                    continue

                # 空气湿度扩散 (水域为湿度源)
                if is_water:
                    # 水域向周围释放水汽
                    net_humid += HUMIDITY_DIFFUSION_COEFF * (1.0 - env.air_humidity) * dt
                else:
                    net_humid += compute_diffusion_flux(
                        env.air_humidity, n_env.air_humidity,
                        HUMIDITY_DIFFUSION_COEFF, dt, MAX_TEMP_CHANGE_PER_STEP
                    )

                # 土壤水分扩散 (坡度修正)
                if terrain and terrain.slope > 0:
                    slope_factor = 1.0 + terrain.slope / 45.0
                else:
                    slope_factor = 1.0

                eff_moist = SOIL_MOISTURE_DIFFUSION_COEFF * slope_factor
                net_moist += compute_diffusion_flux(
                    env.soil_moisture, n_env.soil_moisture,
                    eff_moist, dt, MAX_MOISTURE_CHANGE_PER_STEP
                )

            fluxes_humid[key] = net_humid
            fluxes_moist[key] = net_moist

        # 应用通量
        apply_diffusion_fluxes(
            fluxes_humid, cache,
            lambda e: e.air_humidity,
            lambda e, v: setattr(e, 'air_humidity', v),
            n_nei, 0.01, 1.0
        )
        apply_diffusion_fluxes(
            fluxes_moist, cache,
            lambda e: e.soil_moisture,
            lambda e, v: setattr(e, 'soil_moisture', v),
            n_nei, 0.0, 1.0
        )


class GravityWaterFlowProcessor(ContinuumProcessor):
    """重力水流处理器 — 达西定律简化

    物理模型:
        flow = k * slope^α * moisture * dt

    参数:
        k = 0.005 /h (基础流速)
        α = 1.5 (坡度敏感性指数)

    单位:
        moisture: 0~1 (土壤水分)
        slope: m/m (坡度)
        k: 1/h
        dt: h
    """

    def process(self, world: World, cache: ContinuumCache, grid: Dict, dt: float,
                bounds: Optional[Tuple] = None,
                neighbor_offsets: Optional[list] = None) -> None:
        # 预取海拔
        elevs = {}
        waters = {}
        for key in cache.grid_keys:
            terrain = cache.get_terrain(key)
            elevs[key] = terrain.elevation if terrain else 0.0
            waters[key] = (terrain is not None
                           and is_water_terrain(terrain.terrain_type))

        # 计算净水分损失/增益
        losses = {key: 0.0 for key in cache.grid_keys}

        for key in cache.grid_keys:
            env = cache.get_env(key)
            if env is None:
                continue

            cur_elev = elevs[key]
            is_water = waters[key]
            available = 0.5 if is_water else env.soil_moisture

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nk = (key[0] + dx, key[1] + dy)
                if nk not in grid:
                    continue

                # 只流向下坡
                elev_diff = cur_elev - elevs[nk]
                if elev_diff <= 0:
                    continue

                dist = cached_distance(dx, dy)
                slope = elev_diff / max(dist, 0.1)

                flow = (
                    WATER_FLOW_BASE_RATE
                    * (slope ** WATER_FLOW_SLOPE_EXPONENT)
                    * available
                    * dt
                )
                flow = min(flow, env.soil_moisture * 0.5)

                losses[key] -= flow
                losses[nk] += flow

        # 应用
        for key, delta in losses.items():
            if abs(delta) < 1e-10:
                continue
            env = cache.get_env(key)
            if env is None:
                continue
            env.soil_moisture += delta
            env.soil_moisture = clamp(env.soil_moisture, 0.0, 1.0)


class WindAdvectionProcessor(ContinuumProcessor):
    """风驱平流处理器 — 平流方程

    物理模型:
        dT/dt = C * wind_speed * cos(θ) * (T_neighbor - T_self)
        dH/dt = C * wind_speed * cos(θ) * (H_neighbor - H_self)

    参数:
        C = 0.02 /m (风驱平流系数)
        θ: 风向与邻居方向的夹角

    单位:
        T: °C
        H: 0~1
        wind_speed: m/s
        C: 1/m
        dt: h
    """

    def __init__(self, prevailing_wind_deg: float = 270.0):
        self.prevailing_wind_direction = prevailing_wind_deg

    def process(self, world: World, cache: ContinuumCache, grid: Dict, dt: float,
                bounds: Optional[Tuple] = None,
                neighbor_offsets: Optional[list] = None) -> None:
        if neighbor_offsets is None:
            neighbor_offsets = NEIGHBOR_OFFSETS_MOORE

        wind_rad = math.radians(self.prevailing_wind_direction)
        wind_vx = -math.sin(wind_rad)
        wind_vy = -math.cos(wind_rad)

        n_nei = len(neighbor_offsets)
        fluxes = {}

        for key in cache.grid_keys:
            env = cache.get_env(key)
            if env is None:
                continue

            net_t = 0.0
            net_h = 0.0

            for dx, dy in neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = cache.get_env(nk)
                if n_env is None:
                    continue

                dist = cached_sqrt(dx * dx + dy * dy)
                to_vx = -dx / dist
                to_vy = -dy / dist

                match = to_vx * wind_vx + to_vy * wind_vy
                if match <= 0:
                    continue

                strength = WIND_ADVECTION_COEFF * env.wind_speed * match * dt
                strength = min(strength, 0.3)

                net_t += strength * (n_env.air_temperature - env.air_temperature)
                net_h += strength * (n_env.air_humidity - env.air_humidity)

            fluxes[key] = (net_t, net_h)

        for key, (net_t, net_h) in fluxes.items():
            env = cache.get_env(key)
            if env is None:
                continue
            env.air_temperature += net_t / n_nei
            env.air_humidity += net_h / n_nei
            env.air_temperature = clamp(env.air_temperature, -30.0, 50.0)
            env.air_humidity = clamp(env.air_humidity, 0.01, 1.0)


class SelfRecoveryProcessor(ContinuumProcessor):
    """生态自恢复处理器 — 松弛模型

    物理模型:
        dX/dt = r * sigmoid(X_climax - X) * (X_climax - X)

    参数:
        r: 恢复速率 (1/h)
        X_climax: 顶极状态 (地形依赖)

    单位:
        X: various (T/°C, H/0~1, M/0~1, N/mg/kg, ...)
        r: 1/h
        dt: h
    """

    def process(self, world: World, cache: ContinuumCache, grid: Dict, dt: float,
                bounds: Optional[Tuple] = None,
                neighbor_offsets: Optional[list] = None) -> None:
        for key in cache.grid_keys:
            env = cache.get_env(key)
            terrain = cache.get_terrain(key)
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

            # 气温恢复
            d = c_t - env.air_temperature
            env.air_temperature += RECOVERY_RATE_TEMPERATURE * sigmoid_factor(d, RECOVERY_SIGMOID_K) * d * dt
            env.air_temperature = clamp(env.air_temperature, -30.0, 50.0)

            # 空气湿度恢复
            d = c_h - env.air_humidity
            env.air_humidity += RECOVERY_RATE_HUMIDITY * sigmoid_factor(d, RECOVERY_SIGMOID_K) * d * dt
            env.air_humidity = clamp(env.air_humidity, 0.01, 1.0)

            # 土壤湿度恢复
            d = c_m - env.soil_moisture
            env.soil_moisture += RECOVERY_RATE_MOISTURE * sigmoid_factor(d, RECOVERY_SIGMOID_K) * d * dt
            env.soil_moisture = clamp(env.soil_moisture, 0.0, 1.0)

            # 氮恢复
            d = c_n - env.nitrogen
            env.nitrogen += RECOVERY_RATE_NITROGEN * sigmoid_factor(d, RECOVERY_SIGMOID_K) * d * dt
            env.nitrogen = clamp(env.nitrogen, 0.0, 200.0)

            # 磷恢复
            d = c_p - env.phosphorus
            env.phosphorus += RECOVERY_RATE_PHOSPHORUS * sigmoid_factor(d, RECOVERY_SIGMOID_K) * d * dt
            env.phosphorus = clamp(env.phosphorus, 0.0, 100.0)

            # 钾恢复
            d = c_k - env.potassium
            env.potassium += RECOVERY_RATE_POTASSIUM * sigmoid_factor(d, RECOVERY_SIGMOID_K) * d * dt
            env.potassium = clamp(env.potassium, 0.0, 200.0)
