#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: weather_event_system.py
@说明:
    极端天气诊断系统

设计思想：
--------------------------------------------------------

旧系统：
    概率生成事件
        ↓
    事件修改天气

新系统：
    物理天气自然演化
        ↓
    系统检测异常模式
        ↓
    推导天气事件
        ↓
    创建诊断事件实体

即：

    physics field -> diagnose -> event

而不是：

    random event -> modify weather

--------------------------------------------------------

该系统职责：
1. 从 PhysicalWeatherComponent 中识别极端天气
2. 创建 WeatherEventDiagnosticComponent
3. 管理事件生命周期
4. 避免重复生成相同事件
5. 提供灾害/NPC/UI系统事件源

注意：
--------------------------------------------------------
该系统：

不直接修改天气物理量。
"""

from __future__ import annotations

from typing import Optional

from core.system import System
from core.world import World

from time_module.time_component import TimeComponent

from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)

from environment.physics_weather.components.weather_event_components import (
    EventPhase,
    WeatherEventDiagnosticComponent,
    WeatherEventLifecycleComponent,
    WeatherEventSeverityComponent,
    WeatherEventSourceComponent,
    WeatherEventSourceType,
    WeatherEventType,
)

from environment.physics_weather.utils.weather_classifier import (
    classify_from_component,
)


# ============================================================
# 极端天气诊断系统
# ============================================================

class WeatherEventSystem(System):
    """
    极端天气事件诊断系统
    """

    def __init__(self):

        self._next_event_id = 1

    # ========================================================
    # update
    # ========================================================

    def update(
        self,
        world: World,
        delta_hours: float,
    ):

        weather = world._world_entity.get_component(
            PhysicalWeatherComponent
        )

        if weather is None:
            return

        current_time = world.get_time()

        # ----------------------------------------------------
        # 1. 更新生命周期
        # ----------------------------------------------------

        self._update_lifecycles(
            world,
            delta_hours,
        )

        # ----------------------------------------------------
        # 2. 检测天气事件
        # ----------------------------------------------------

        detected_event = self._detect_event(
            weather=weather,
            world=world,
        )

        if detected_event is None:
            return

        event_type, severity = detected_event

        # ----------------------------------------------------
        # 3. 检查是否已存在同类事件
        # ----------------------------------------------------

        if self._has_active_event(
            world,
            event_type,
        ):
            return

        # ----------------------------------------------------
        # 4. 创建诊断事件
        # ----------------------------------------------------

        self._create_event(
            world=world,
            event_type=event_type,
            severity=severity,
            current_hour=current_time.total_hours,
        )

    # ========================================================
    # 检测事件
    # ========================================================

    def _detect_event(
        self,
        weather: PhysicalWeatherComponent,
        world: World,
    ) -> Optional[tuple]:

        temp = weather.temperature
        humidity = weather.relative_humidity
        pressure = weather.pressure
        rain = weather.precipitation_rate
        wind = weather.wind_speed
        cloud = weather.cloud_cover

        # ----------------------------------------------------
        # 台风
        # ----------------------------------------------------

        if (
            pressure <= 970
            and wind >= 28
            and humidity >= 0.85
        ):

            severity = min(
                1.0,
                (
                    (1000 - pressure) / 50
                    + wind / 60
                ) * 0.5
            )

            return (
                WeatherEventType.TYPHOON,
                severity,
            )

        # ----------------------------------------------------
        # 暴雪
        # ----------------------------------------------------

        if (
            temp <= -2
            and rain >= 5
            and cloud >= 0.8
        ):

            severity = min(
                1.0,
                abs(temp) / 20 + rain / 50
            )

            return (
                WeatherEventType.SNOWSTORM,
                severity,
            )

        # ----------------------------------------------------
        # 暴雨
        # ----------------------------------------------------

        if (
            rain >= 20
            and humidity >= 0.9
        ):

            severity = min(
                1.0,
                rain / 100
            )

            return (
                WeatherEventType.STORM,
                severity,
            )

        # ----------------------------------------------------
        # 热浪
        # ----------------------------------------------------

        if (
            temp >= 35
            and humidity <= 0.6
        ):

            severity = min(
                1.0,
                (temp - 35) / 15
            )

            return (
                WeatherEventType.HEAT_WAVE,
                severity,
            )

        # ----------------------------------------------------
        # 寒潮
        # ----------------------------------------------------

        if (
            temp <= -10
            and wind >= 8
        ):

            severity = min(
                1.0,
                abs(temp + 10) / 20
            )

            return (
                WeatherEventType.COLD_WAVE,
                severity,
            )

        # ----------------------------------------------------
        # 干旱
        # ----------------------------------------------------

        if (
            humidity <= 0.2
            and rain <= 0.01
            and cloud <= 0.2
            and temp >= 28
        ):

            severity = min(
                1.0,
                (
                    (28 - humidity * 100)
                    / 50
                )
            )

            return (
                WeatherEventType.DROUGHT,
                severity,
            )

        return None

    # ========================================================
    # 是否存在同类事件
    # ========================================================

    def _has_active_event(
        self,
        world: World,
        event_type: WeatherEventType,
    ) -> bool:

        events = world.get_components(
            WeatherEventDiagnosticComponent
        )

        for entity, comps in events:

            comp: WeatherEventDiagnosticComponent = comps[0]

            if comp.event_type == event_type:
                return True

        return False

    # ========================================================
    # 创建事件
    # ========================================================

    def _create_event(
        self,
        world: World,
        event_type: WeatherEventType,
        severity: float,
        current_hour: float,
    ):

        event_id = self._allocate_event_id()

        entity = world.create_entity()

        # ----------------------------------------------------
        # 诊断组件
        # ----------------------------------------------------

        entity.add_component(

            WeatherEventDiagnosticComponent(
                event_id=event_id,
                event_type=event_type,
                severity=severity,
                confidence=1.0,
                detected_hour=current_hour,
            )
        )

        # ----------------------------------------------------
        # 生命周期
        # ----------------------------------------------------

        duration = self._estimate_duration(
            event_type,
            severity,
        )

        entity.add_component(

            WeatherEventLifecycleComponent(
                event_id=event_id,
                total_duration_hours=duration,
                remaining_hours=duration,
                phase=EventPhase.FORMING,
            )
        )

        # ----------------------------------------------------
        # 严重等级
        # ----------------------------------------------------

        entity.add_component(

            WeatherEventSeverityComponent(
                event_id=event_id,
                severity=severity,
                category=self._severity_to_category(
                    severity
                ),
                damage_multiplier=1.0 + severity,
                emergency_level=int(
                    severity * 5
                ),
            )
        )

        # ----------------------------------------------------
        # 来源组件
        # ----------------------------------------------------

        entity.add_component(

            WeatherEventSourceComponent(
                event_id=event_id,
                source_type=WeatherEventSourceType.NATURAL,
            )
        )

        print(
            f"[WeatherEvent] "
            f"{event_type.value} "
            f"severity={severity:.2f} "
            f"duration={duration:.1f}h"
        )

    # ========================================================
    # 生命周期更新
    # ========================================================

    def _update_lifecycles(
        self,
        world: World,
        delta_hours: float,
    ):

        events = list(
            world.get_components(
                WeatherEventLifecycleComponent
            )
        )

        for entity, comps in events:

            lifecycle: WeatherEventLifecycleComponent = comps[0]

            lifecycle.remaining_hours -= delta_hours

            progress = lifecycle.normalized_age

            # ------------------------------------------------
            # 生命周期阶段
            # ------------------------------------------------

            if progress < 0.2:
                lifecycle.phase = EventPhase.FORMING

            elif progress < 0.7:
                lifecycle.phase = EventPhase.MATURE

            elif progress < 1.0:
                lifecycle.phase = EventPhase.DECAYING

            else:
                lifecycle.phase = EventPhase.DISSIPATED

            # ------------------------------------------------
            # 删除结束事件
            # ------------------------------------------------

            if lifecycle.expired:

                world.remove_entity(entity)

    # ========================================================
    # duration 估计
    # ========================================================

    def _estimate_duration(
        self,
        event_type: WeatherEventType,
        severity: float,
    ) -> float:

        base = {

            WeatherEventType.STORM: 12,

            WeatherEventType.TYPHOON: 72,

            WeatherEventType.HEAT_WAVE: 120,

            WeatherEventType.COLD_WAVE: 96,

            WeatherEventType.DROUGHT: 240,

            WeatherEventType.SNOWSTORM: 48,

        }.get(event_type, 24)

        return base * (0.5 + severity)

    # ========================================================
    # severity -> category
    # ========================================================

    def _severity_to_category(
        self,
        severity: float,
    ) -> int:

        if severity < 0.2:
            return 1

        if severity < 0.4:
            return 2

        if severity < 0.6:
            return 3

        if severity < 0.8:
            return 4

        return 5

    # ========================================================
    # event id
    # ========================================================

    def _allocate_event_id(self) -> int:

        eid = self._next_event_id

        self._next_event_id += 1

        return eid