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
   离散: 按下坡边容量缩放后转移，源头/目的总量守恒
   单位: M (0~1), k (1/h), slope (m/m), dt (h)

4. 风驱平流 (Wind Advection)
   物理: 平流方程
   公式: dT/dt = -v · ∇T
   离散: ΔT = C * wind_speed * cos(θ) * (T_neighbor - T_self) * dt / n_neighbors
   单位: T (°C), v (m/s), C (1/m), dt (h)
   守恒实现：上风单元格减少的温度/湿度等于下风单元格增加的量

5. 生态自恢复 (Ecological Self-Recovery)
   物理: 松弛模型 (向顶极状态恢复)
   公式: dX/dt = r * sigmoid(X_climax - X) * (X_climax - X)
   离散: ΔX = r * sigmoid(d) * d * dt
   单位: X (various), r (1/h), dt (h)
"""

import math
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

from core.sqrt_cache import cached_distance
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
        if neighbor_offsets is None:
            neighbor_offsets = NEIGHBOR_OFFSETS_MOORE

        # 预取海拔与水域标记
        elevs = {}
        is_water = {}
        for key in cache.grid_keys:
            terrain = cache.get_terrain(key)
            elevs[key] = terrain.elevation if terrain else 0.0
            is_water[key] = (terrain is not None
                             and is_water_terrain(terrain.terrain_type))

        # 第一步：计算每条下坡边的原始流量
        edges = []  # (src, dst, flow)
        for key in cache.grid_keys:
            env = cache.get_env(key)
            if env is None:
                continue

            cur_elev = elevs[key]
            available = 0.5 if is_water[key] else env.soil_moisture

            for dx, dy in neighbor_offsets:
                nk = (key[0] + dx, key[1] + dy)
                if nk not in grid:
                    continue

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
                if flow > 0:
                    edges.append((key, nk, flow))

        # 第二步：用剩余水量/剩余容量限制流量，确保质量守恒
        outflows = {key: 0.0 for key in cache.grid_keys}
        inflows = {key: 0.0 for key in cache.grid_keys}
        for src, dst, raw_flow in edges:
            src_env = cache.get_env(src)
            dst_env = cache.get_env(dst)
            if src_env is None or dst_env is None:
                continue

            # 不能超过源头的剩余水量
            src_remaining = max(0.0, src_env.soil_moisture - outflows[src])
            flow = min(raw_flow, src_remaining)

            # 不能超过目的地的剩余容量（避免 clamp 时凭空损失/增加水分）
            dst_capacity = max(0.0, 1.0 - dst_env.soil_moisture - inflows[dst])
            flow = min(flow, dst_capacity)

            if flow > 1e-12:
                outflows[src] += flow
                inflows[dst] += flow

        # 第三步：统一应用净流入/流出
        for key in cache.grid_keys:
            env = cache.get_env(key)
            if env is None:
                continue
            delta = inflows[key] - outflows[key]
            if abs(delta) < 1e-12:
                continue
            env.soil_moisture = clamp(env.soil_moisture + delta, 0.0, 1.0)


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

        # 用增量字典统一应用，避免同一 tick 内读取到已修改值
        delta_t = {key: 0.0 for key in cache.grid_keys}
        delta_h = {key: 0.0 for key in cache.grid_keys}

        for key in cache.grid_keys:
            env = cache.get_env(key)
            if env is None:
                continue

            for dx, dy in neighbor_offsets:
                nk = resolve_boundary((key[0] + dx, key[1] + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = cache.get_env(nk)
                if n_env is None:
                    continue

                dist = cached_distance(dx, dy)
                # to_vx/to_vy 指向 key -> nk，即风从 key 吹向 nk 时 match > 0
                to_vx = -dx / dist
                to_vy = -dy / dist

                match = to_vx * wind_vx + to_vy * wind_vy
                if match <= 0:
                    continue

                strength = WIND_ADVECTION_COEFF * env.wind_speed * match * dt
                strength = min(strength, 0.3)

                # 上风(key) 向下风(nk) 传输热量/湿度，保持总量守恒
                f_t = strength * (env.air_temperature - n_env.air_temperature)
                f_h = strength * (env.air_humidity - n_env.air_humidity)

                delta_t[key] -= f_t / n_nei
                delta_t[nk] += f_t / n_nei
                delta_h[key] -= f_h / n_nei
                delta_h[nk] += f_h / n_nei

        for key in cache.grid_keys:
            env = cache.get_env(key)
            if env is None:
                continue
            env.air_temperature = clamp(
                env.air_temperature + delta_t[key], -30.0, 50.0
            )
            env.air_humidity = clamp(
                env.air_humidity + delta_h[key], 0.01, 1.0
            )


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

            c_t, c_h, c_m = climax[:3]

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

            # 注意：氮/磷/钾由 SoilComponent 与资源再生系统管理，不在连续统中恢复，
            # 避免 EnvironmentComponent 出现未声明字段且导致守恒检查误报。