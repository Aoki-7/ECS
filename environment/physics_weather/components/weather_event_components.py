#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
物理异常事件组件

不再预定义天气事件类型（台风/暴雪/热浪等）。
所有异常从物理量的统计偏离实时检测，
事件标签由异常组合推导，不存储、不驱动演化。
"""

from dataclasses import dataclass, field
from typing import Optional, List
from core.component import Component


@dataclass(slots=True)
class PhysicalAnomalyComponent(Component):
    """
    物理异常记录组件

    记录某一物理量偏离其历史统计基准的状态。
    不预定义异常类型，variable 字段直接写物理量名称。
    """

    anomaly_id: int

    # 异常物理量名称："temperature", "pressure", "wind_speed",
    # "precipitation_rate", "relative_humidity", "cloud_cover"
    variable: str

    # 当前值
    current_value: float = 0.0

    # 历史基准值（滑动窗口均值）
    baseline_value: float = 0.0

    # 历史标准差
    baseline_std: float = 1.0

    # 偏离标准差数（|current - baseline| / std）
    deviation_sigma: float = 0.0

    # 异常开始时间（世界总小时）
    start_hour: float = 0.0

    # 已持续时间（小时）
    duration_hours: float = 0.0

    # 严重度 0-1（基于偏离程度）
    severity: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.deviation_sigma > 0.0

    @property
    def label(self) -> str:
        """由物理量名称和方向生成人类可读标签"""
        direction = "high" if self.current_value > self.baseline_value else "low"
        return f"{self.variable}_{direction}"


@dataclass(slots=True)
class AnomalySpatialComponent(Component):
    """异常空间属性（可选）"""

    anomaly_id: int
    center_x: float = 0.0
    center_y: float = 0.0
    radius_km: float = 0.0


@dataclass(slots=True)
class AnomalyStatisticsComponent(Component):
    """异常统计信息（可选，供调试/诊断）"""

    anomaly_id: int
    max_value: Optional[float] = None
    min_value: Optional[float] = None
    peak_severity: float = 0.0


__all__ = [
    "PhysicalAnomalyComponent",
    "AnomalySpatialComponent",
    "AnomalyStatisticsComponent",
]