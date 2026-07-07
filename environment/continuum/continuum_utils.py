#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续统共享工具模块

提供所有处理器共享的:
- 边界解析
- 组件缓存管理
- 守恒检查
- 数值稳定性工具

数学符号约定:
- T: 温度 (°C)
- H: 湿度 (0~1)
- M: 土壤水分 (0~1)
- N: 氮 (mg/kg)
- P: 磷 (mg/kg)
- K: 钾 (mg/kg)
- t: 时间步长 (hours)
- dx, dy: 空间步长 (m)
- D: 扩散系数 (m²/h)
- F: 通量 (单位/h)
"""

import math
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

from core.world import World
from core.entity import Entity

from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent


# ─────────────────────────────────────────────
# 边界解析
# ─────────────────────────────────────────────

def resolve_boundary(coord: Tuple[int, int], grid: Dict, bounds: Optional[Tuple] = None) -> Optional[Tuple[int, int]]:
    """
    解析网格边界

    支持反射边界条件:
    - 超出边界返回 None (反射边界)
    - 未来可扩展: 周期边界、固定值边界、开放边界

    Args:
        coord: (x, y) 坐标
        grid: 网格索引 {(x,y): Entity}
        bounds: 边界范围 (min_x, max_x, min_y, max_y)

    Returns:
        有效坐标 或 None (超出边界)
    """
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


# ─────────────────────────────────────────────
# 组件缓存管理
# ─────────────────────────────────────────────

@dataclass
class ContinuumCache:
    """连续统计算缓存

    一次性查询所有组件，避免重复查询
    利用 ArchetypeStore 的列式存储优势
    """
    env_cache: Dict[Tuple[int, int], EnvironmentComponent]
    terrain_cache: Dict[Tuple[int, int], TerrainComponent]
    space_cache: Dict[Tuple[int, int], SpaceComponent]
    grid_keys: List[Tuple[int, int]]
    n_cells: int

    @classmethod
    def build(cls, world: World, grid: Dict[Tuple[int, int], Entity]) -> "ContinuumCache":
        """构建缓存

        一次性查询所有组件，利用 ArchetypeStore 的列式存储
        """
        env_cache = {}
        terrain_cache = {}
        space_cache = {}

        for key, eid in grid.items():
            env_cache[key] = world.get_component(eid, EnvironmentComponent)
            terrain_cache[key] = world.get_component(eid, TerrainComponent)
            space_cache[key] = world.get_component(eid, SpaceComponent)

        return cls(
            env_cache=env_cache,
            terrain_cache=terrain_cache,
            space_cache=space_cache,
            grid_keys=list(grid.keys()),
            n_cells=len(grid),
        )

    def get_env(self, key: Tuple[int, int]) -> Optional[EnvironmentComponent]:
        return self.env_cache.get(key)

    def get_terrain(self, key: Tuple[int, int]) -> Optional[TerrainComponent]:
        return self.terrain_cache.get(key)

    def get_space(self, key: Tuple[int, int]) -> Optional[SpaceComponent]:
        return self.space_cache.get(key)


# ─────────────────────────────────────────────
# 数值稳定性工具
# ─────────────────────────────────────────────

def clamp(value: float, min_val: float, max_val: float) -> float:
    """限制值在范围内"""
    return max(min_val, min(max_val, value))


def sigmoid_factor(deviation: float, k: float = 2.0) -> float:
    """
    Sigmoid 形状因子

    偏离越大，恢复越快
    sigmoid(d) = 2 / (1 + exp(-k * |d|)) - 1

    Args:
        deviation: 偏离值
        k: 形状因子 (k=0: 线性, k>0: 偏离大时加速)

    Returns:
        0~1 的恢复强度因子
    """
    if abs(deviation) < 1e-10:
        return 0.0
    return 2.0 / (1.0 + math.exp(-k * abs(deviation))) - 1.0


def limit_change(current: float, delta: float, max_change: float,
                 min_val: float, max_val: float) -> float:
    """
    限制变化量并 clamp

    先限制单步变化量，再限制范围
    """
    limited_delta = max(-max_change, min(max_change, delta))
    return clamp(current + limited_delta, min_val, max_val)


# ─────────────────────────────────────────────
# 守恒检查
# ─────────────────────────────────────────────

@dataclass
class ConservationSnapshot:
    """守恒快照"""
    total_temperature: float  # 温度总和 (°C)
    total_humidity: float   # 湿度总和
    total_moisture: float   # 土壤水分总和
    total_nitrogen: float   # 氮总和 (mg/kg)
    total_phosphorus: float # 磷总和 (mg/kg)
    total_potassium: float  # 钾总和 (mg/kg)

    def __sub__(self, other: "ConservationSnapshot") -> "ConservationSnapshot":
        return ConservationSnapshot(
            total_temperature=self.total_temperature - other.total_temperature,
            total_humidity=self.total_humidity - other.total_humidity,
            total_moisture=self.total_moisture - other.total_moisture,
            total_nitrogen=self.total_nitrogen - other.total_nitrogen,
            total_phosphorus=self.total_phosphorus - other.total_phosphorus,
            total_potassium=self.total_potassium - other.total_potassium,
        )

    def max_abs_diff(self) -> float:
        return max(
            abs(self.total_temperature),
            abs(self.total_humidity),
            abs(self.total_moisture),
            abs(self.total_nitrogen),
            abs(self.total_phosphorus),
            abs(self.total_potassium),
        )


def take_conservation_snapshot(cache: ContinuumCache) -> ConservationSnapshot:
    """拍摄守恒快照"""
    total_temp = 0.0
    total_humid = 0.0
    total_moist = 0.0
    total_n = 0.0
    total_p = 0.0
    total_k = 0.0

    for key in cache.grid_keys:
        env = cache.get_env(key)
        if env is None:
            continue
        total_temp += env.air_temperature
        total_humid += env.air_humidity
        total_moist += env.soil_moisture
        total_n += env.nitrogen
        total_p += env.phosphorus
        total_k += env.potassium

    return ConservationSnapshot(
        total_temperature=total_temp,
        total_humidity=total_humid,
        total_moisture=total_moist,
        total_nitrogen=total_n,
        total_phosphorus=total_p,
        total_potassium=total_k,
    )


def check_conservation(before: ConservationSnapshot, after: ConservationSnapshot,
                       tolerance: float = 1e-6) -> Optional[str]:
    """
    检查守恒性

    注意：本检查仅对封闭系统有意义。自恢复、水域湿度源、火灾等处理器会引入
    有意的源/汇，启用检查时会产生预期内的警告。生产环境默认关闭该检查。

    Args:
        before: 处理前快照
        after: 处理后快照
        tolerance: 允许误差

    Returns:
        守恒则返回 None，不守恒则返回错误信息
    """
    diff = after - before
    max_diff = diff.max_abs_diff()

    if max_diff > tolerance:
        return (
            f"Conservation violation: max_diff={max_diff:.6f} > tolerance={tolerance}\n"
            f"  Temperature: {diff.total_temperature:.6f}\n"
            f"  Humidity: {diff.total_humidity:.6f}\n"
            f"  Moisture: {diff.total_moisture:.6f}\n"
            f"  Nitrogen: {diff.total_nitrogen:.6f}\n"
            f"  Phosphorus: {diff.total_phosphorus:.6f}\n"
            f"  Potassium: {diff.total_potassium:.6f}"
        )
    return None


# ─────────────────────────────────────────────
# 通用扩散内核
# ─────────────────────────────────────────────

def compute_diffusion_flux(value_self: float, value_neighbor: float,
                           diffusion_coeff: float, dt: float,
                           max_change: float) -> float:
    """
    通用扩散通量计算

    物理公式: F = D * (V_neighbor - V_self) * dt

    Args:
        value_self: 本单元格值
        value_neighbor: 邻居值
        diffusion_coeff: 扩散系数
        dt: 时间步长
        max_change: 最大单步变化

    Returns:
        限制后的通量
    """
    dV = value_neighbor - value_self
    flux = diffusion_coeff * dV * dt
    return max(-max_change, min(max_change, flux))


def apply_diffusion_fluxes(fluxes: Dict[Tuple[int, int], float],
                           cache: ContinuumCache,
                           getter, setter,
                           n_neighbors: int,
                           min_val: float, max_val: float) -> None:
    """
    应用扩散通量

    统一应用通量并 clamp，避免多个处理器叠加后超界

    Args:
        fluxes: {(x,y): net_flux} 净通量
        cache: 组件缓存
        getter: 获取值的函数 (env) -> value
        setter: 设置值的函数 (env, new_value) -> None
        n_neighbors: 邻居数 (用于平均)
        min_val: 最小值
        max_val: 最大值
    """
    for key, net_flux in fluxes.items():
        env = cache.get_env(key)
        if env is None:
            continue

        current = getter(env)
        new_value = current + net_flux / n_neighbors
        new_value = clamp(new_value, min_val, max_val)
        setter(env, new_value)


# ─────────────────────────────────────────────
# 邻居偏移
# ─────────────────────────────────────────────

NEIGHBOR_OFFSETS_VON_NEUMANN = [(0, 1), (0, -1), (1, 0), (-1, 0)]
NEIGHBOR_OFFSETS_MOORE = [
    (0, 1), (0, -1), (1, 0), (-1, 0),
    (1, 1), (1, -1), (-1, 1), (-1, -1)
]


def get_neighbor_offsets(neighborhood: str = "moore") -> List[Tuple[int, int]]:
    """获取邻居偏移"""
    if neighborhood == "moore":
        return NEIGHBOR_OFFSETS_MOORE
    elif neighborhood == "von_neumann":
        return NEIGHBOR_OFFSETS_VON_NEUMANN
    else:
        raise ValueError(f"Unknown neighborhood: {neighborhood}")
