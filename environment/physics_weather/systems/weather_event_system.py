#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
物理异常检测系统

旧系统：预定义事件类型（台风/暴雪/热浪...）+ 固定阈值检测
新系统：滑动窗口统计 + 实时偏离检测

核心思想：
- 维护每个物理量的近期历史统计（均值、标准差）
- 当 |当前值 - 均值| > N * 标准差 时标记为异常
- 异常标签由物理量名称自动生成，无预设枚举
- 异常存在时间由物理异常持续时长决定

不修改任何天气物理量，只作诊断记录。

变更（2026-06-01）：
- 修复异常创建过早：首次偏离不立即创建实体，持续满足条件后才创建
- 移除 pass 占位符，添加结构化日志
"""

from __future__ import annotations

import math
from collections import deque
from typing import Dict, Optional

from core.system import System
from core.world import World
from core.systems.event_log_system import EventLog

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.components.weather_event_components import (
    PhysicalAnomalyComponent,
    AnomalyStatisticsComponent,
)


class WeatherEventSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    物理异常检测系统

    跟踪天气物理量的统计分布，识别偏离历史常态的时段。
    """

    # 滑动窗口大小（样本数）
    WINDOW_SIZE: int = 720  # 约30天（每小时一个样本）

    # 异常判定阈值（偏离几个标准差）
    ANOMALY_THRESHOLD_SIGMA: float = 2.5

    # 异常结束阈值（回到几个标准差内）
    END_THRESHOLD_SIGMA: float = 1.5

    # 最小持续时间（小时）才创建记录
    MIN_DURATION_HOURS: float = 3.0

    def __init__(self):
        self._next_anomaly_id = 1

        # 每个物理量的历史滑动窗口
        self._history: Dict[str, deque] = {
            "temperature": deque(maxlen=self.WINDOW_SIZE),
            "pressure": deque(maxlen=self.WINDOW_SIZE),
            "wind_speed": deque(maxlen=self.WINDOW_SIZE),
            "precipitation_rate": deque(maxlen=self.WINDOW_SIZE),
            "relative_humidity": deque(maxlen=self.WINDOW_SIZE),
            "cloud_cover": deque(maxlen=self.WINDOW_SIZE),
        }

        # 当前活跃异常：variable -> entity_id
        self._active_anomalies: Dict[str, int] = {}

        # 待确认异常：variable -> {start_hour, current_value, mean, std, sigma}
        self._pending_anomalies: Dict[str, Dict] = {}

    def update(self, world: World, delta_hours: float):
        weather = world.get_world_entity().get_component(PhysicalWeatherComponent)
        if weather is None:
            return

        current_time = world.get_time().total_hours

        # 当前物理量快照
        snapshot = {
            "temperature": weather.temperature,
            "pressure": weather.pressure,
            "wind_speed": weather.wind_speed,
            "precipitation_rate": weather.precipitation_rate,
            "relative_humidity": weather.relative_humidity,
            "cloud_cover": weather.cloud_cover,
        }

        # 更新历史窗口并检测异常
        for variable, value in snapshot.items():
            history = self._history[variable]
            history.append(value)

            # 窗口足够大时才做统计检测
            if len(history) < 48:  # 至少2天数据
                continue

            mean = sum(history) / len(history)
            variance = sum((x - mean) ** 2 for x in history) / len(history)
            std = math.sqrt(variance) if variance > 0 else 1.0

            # 防止 std 过小导致噪声触发
            std = max(std, abs(mean) * 0.05 + 0.01)

            deviation = abs(value - mean)
            sigma = deviation / std

            has_active = variable in self._active_anomalies
            pending = self._pending_anomalies.get(variable)

            if not has_active and sigma > self.ANOMALY_THRESHOLD_SIGMA:
                if pending is None:
                    # 首次偏离，进入待确认状态
                    self._pending_anomalies[variable] = {
                        "start_hour": current_time,
                        "current_value": value,
                        "mean": mean,
                        "std": std,
                        "sigma": sigma,
                    }
                else:
                    # 持续偏离，检查是否满足最小持续时间
                    duration = current_time - pending["start_hour"]
                    if duration >= self.MIN_DURATION_HOURS:
                        # 确认异常，创建实体
                        self._create_anomaly_entity(
                            world, variable, value, pending["mean"],
                            pending["std"], sigma, pending["start_hour"],
                            current_time
                        )
                        del self._pending_anomalies[variable]
            elif not has_active and pending is not None:
                # 偏离已结束但未达到持续时间，取消待确认
                if sigma <= self.ANOMALY_THRESHOLD_SIGMA:
                    del self._pending_anomalies[variable]

            elif has_active:
                entity_id = self._active_anomalies[variable]
                entity = world.query_entity(entity_id)

                if entity is None:
                    del self._active_anomalies[variable]
                    continue

                anomaly = world.get_component(entity, PhysicalAnomalyComponent)
                stats = world.get_component(entity, AnomalyStatisticsComponent)

                if anomaly is None:
                    del self._active_anomalies[variable]
                    continue

                if sigma < self.END_THRESHOLD_SIGMA:
                    # 异常结束，记录日志后清理
                    self._finalize_anomaly(world, entity, anomaly, current_time)
                    world.remove_entity(entity)
                    del self._active_anomalies[variable]
                else:
                    # 异常持续，更新状态
                    anomaly.current_value = value
                    anomaly.duration_hours += delta_hours
                    anomaly.deviation_sigma = sigma
                    anomaly.severity = min(
                        1.0, (sigma - self.ANOMALY_THRESHOLD_SIGMA) / 2.0
                    )

                    if stats is not None:
                        stats.max_value = max(stats.max_value, value)
                        stats.min_value = min(stats.min_value, value)
                        stats.peak_severity = max(stats.peak_severity, anomaly.severity)

    def _create_anomaly_entity(self, world: World, variable: str, value: float,
                               mean: float, std: float, sigma: float,
                               start_hour: float, current_time: float):
        """创建异常实体并记录事件"""
        entity = world.create_entity()
        anomaly_id = self._allocate_anomaly_id()
        severity = min(1.0, (sigma - self.ANOMALY_THRESHOLD_SIGMA) / 2.0)

        world.add_component(
            entity,
            PhysicalAnomalyComponent(
                anomaly_id=anomaly_id,
                variable=variable,
                current_value=value,
                baseline_value=mean,
                baseline_std=std,
                deviation_sigma=sigma,
                start_hour=start_hour,
                duration_hours=current_time - start_hour,
                severity=severity,
            )
        )
        world.add_component(
            entity,
            AnomalyStatisticsComponent(
                anomaly_id=anomaly_id,
                max_value=value,
                min_value=value,
                peak_severity=severity,
            )
        )

        self._active_anomalies[variable] = entity.id

        EventLog.log(
            world,
            event_type="weather_anomaly_start",
            description=f"{variable} 异常开始，偏离 {sigma:.2f}σ",
            data={"variable": variable, "sigma": sigma, "value": value},
            severity="warning"
        )

    def _finalize_anomaly(self, world: World, entity, anomaly, current_time: float):
        """异常结束时的收尾记录"""
        EventLog.log(
            world,
            event_type="weather_anomaly_end",
            description=f"{anomaly.variable} 异常结束，持续 {anomaly.duration_hours:.1f}h",
            data={
                "variable": anomaly.variable,
                "duration_hours": anomaly.duration_hours,
                "peak_sigma": anomaly.deviation_sigma,
            },
            severity="info"
        )

    def _allocate_anomaly_id(self) -> int:
        aid = self._next_anomaly_id
        self._next_anomaly_id += 1
        return aid
