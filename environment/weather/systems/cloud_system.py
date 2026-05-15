#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
云量演化系统

负责模拟云层覆盖度的空间分布和时序变化。
基于大尺度天气系统运动，生成局部地区的云量场。

【ECS 职责】
- CloudSystem 只维护云量物理量（total_cloud_cover / cloud_depth / vertical_profile）
- sky 状态枚举（SkyState）由 WeatherSystem 的半马尔可夫链统一管理
- sunlight 光照强度由 CloudSystem 根据云量和太阳角度计算
"""

import math
import random
from typing import List, Tuple, Optional

from core.world import World
from core.system import System

from environment.weather.components.weather_component import WeatherComponent


def transmittance_to_cloud_cover(transmittance: float) -> float:
    """将透光率转换为云量覆盖度"""
    return max(0.0, min(1.0, 1.0 - transmittance))


def total_cloud_cover_to_sky_state(total_cloud_cover: float) -> str:
    """将总云量转换为天空状态描述符（仅供外部参考，不再由 CloudSystem 写入 WeatherComponent）"""
    if total_cloud_cover < 0.05:
        return "CLEAR"
    elif total_cloud_cover < 0.25:
        return "PARTLY_CLOUDY"
    elif total_cloud_cover < 0.5:
        return "CLOUDY"
    else:
        return "OVERCAST"


class CloudLayer:
    """云层类"""

    def __init__(self, layer_type: str, base_pressure: float, top_pressure: float):
        self.layer_type = layer_type
        self.base_pressure = base_pressure
        self.top_pressure = top_pressure
        self.thickness_m = (base_pressure - top_pressure) * 10  # 简化换算

    def to_dict(self):
        return {
            "type": self.layer_type,
            "base_pressure_hpa": self.base_pressure,
            "top_pressure_hpa": self.top_pressure,
            "thickness_m": round(self.thickness_m, 1),
        }


class CloudSystem(System):
    """云量演化系统

    仅维护云量物理量字段：
    - total_cloud_cover: 总云量 (0~1)
    - cloud_depth: 云层平均厚度 (km)
    - vertical_profile: 高度-云量剖面
    - sunlight: 光照强度 (0~1)

    不写入 sky 状态枚举（那由 WeatherSystem 负责）。
    """

    def __init__(self, world: World, delta_time_hours: float = 0.5):
        super().__init__()
        self.world = world
        self.delta_time = delta_time_hours
        self.cloud_layers: List[CloudLayer] = []
        self._ensure_component_exists()

    def add_cloud_layer(self, layer_type: str, base_pressure: float, top_pressure: float) -> int:
        """添加新云层"""
        if not (0 < top_pressure < base_pressure <= 1050):
            raise ValueError("气压值超出有效范围")

        layer = CloudLayer(layer_type, base_pressure, top_pressure)
        self.cloud_layers.append(layer)
        return len(self.cloud_layers) - 1

    def update(self, world: World, delta_hours: float):
        """云量系统更新

        职责（仅物理量）：
        1. 计算 total_cloud_cover — 写入 WeatherComponent
        2. 计算光照强度 sunlight — 写入 WeatherComponent
        3. **不写入** sky 状态枚举
        """
        weather = self.world._world_entity.get_component(WeatherComponent)

        if not weather:
            return

        # ── 计算总云量 ──
        total_cover = self._compute_total_cover()
        weather.total_cloud_cover = total_cover

        # ── 计算云层平均厚度 ──
        if self.cloud_layers:
            weather.cloud_depth = sum(
                l.thickness_m for l in self.cloud_layers
            ) / len(self.cloud_layers) / 1000  # m → km
        else:
            weather.cloud_depth = 0.0

        # ── 计算光照强度 ──
        weather.sunlight = max(0.05, 1.0 - total_cover * 0.85)

    def _compute_total_cover(self) -> float:
        """从各云层计算总云量覆盖度"""
        if not self.cloud_layers:
            return 0.0

        total_cover = 0.0
        for layer in self.cloud_layers:
            # 模拟光学厚度
            base_tau = 0.5 * (0.5 + 2.0) / 10.0
            transmittance = math.exp(-base_tau)
            layer_cover = transmittance_to_cloud_cover(transmittance)
            total_cover = min(1.0, total_cover + layer_cover * (1 - 0.3 * total_cover))

        return min(1.0, max(0.0, total_cover))

    def get_active_layers(self):
        """获取当前活跃的云层"""
        return self.cloud_layers

    def _ensure_component_exists(self):
        """确保天气组件存在"""
        if not self.world._world_entity.get_component(WeatherComponent):
            entity = self.world.create_entity()
            self.world.add_component(entity, WeatherComponent())


__all__ = ['CloudSystem', 'CloudLayer', 'total_cloud_cover_to_sky_state']
