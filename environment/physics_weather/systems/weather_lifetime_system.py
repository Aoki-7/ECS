#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: weather_lifecycle_system.py
@说明:
    极端天气生命周期管理系统（Physics Weather Version）

职责：
--------------------------------------------------------

1. 更新天气事件生命周期
2. 管理事件阶段切换
3. 清理结束事件
4. 输出事件演化日志
5. 支持长期持续事件保护
6. 支持未来事件链扩展

设计原则：
--------------------------------------------------------

旧系统：
    事件 == 天气修改器

新系统：
    事件 == 物理天气诊断结果

因此：
    本系统只管理“事件实体”

不负责：
    修改天气物理场

--------------------------------------------------------
"""

from __future__ import annotations

from typing import Optional
from typing import Set

from core.system import System
from core.world import World

from environment.physics_weather.components.weather_event_components import (
    EventPhase,
    WeatherEventDiagnosticComponent,
    WeatherEventLifecycleComponent,
)


# ============================================================
# 生命周期系统
# ============================================================

class WeatherLifetimeSystem(System):
    """
    天气事件生命周期系统
    """

    def __init__(

        self,

        protected_event_types: Optional[Set[str]] = None,

        enable_log: bool = True,
    ):

        # 不自动清理的事件
        self.protected_event_types = (
            protected_event_types or set()
        )

        self.enable_log = enable_log

    # ========================================================
    # update
    # ========================================================

    def update(
        self,
        world: World,
        delta_hours: float,
    ):

        entities = list(

            world.get_components(

                WeatherEventDiagnosticComponent,
                WeatherEventLifecycleComponent,
            )
        )

        for entity, comps in entities:

            diagnostic = comps[0]
            lifecycle = comps[1]

            diagnostic: WeatherEventDiagnosticComponent
            lifecycle: WeatherEventLifecycleComponent

            # ------------------------------------------------
            # 生命周期推进
            # ------------------------------------------------

            lifecycle.remaining_hours -= delta_hours

            if lifecycle.remaining_hours < 0:
                lifecycle.remaining_hours = 0

            # ------------------------------------------------
            # 生命周期阶段更新
            # ------------------------------------------------

            self._update_phase(
                lifecycle
            )

            # ------------------------------------------------
            # 生命周期日志
            # ------------------------------------------------

            self._log_phase(
                diagnostic,
                lifecycle,
            )

            # ------------------------------------------------
            # 是否结束
            # ------------------------------------------------

            if lifecycle.expired:

                if (
                    diagnostic.event_type.value
                    in self.protected_event_types
                ):

                    if self.enable_log:

                        print(
                            "[WeatherLifetimeSystem] "
                            f"事件 {diagnostic.label} "
                            "已结束但受保护，不自动清理"
                        )

                    continue

                self._cleanup_entity(
                    world=world,
                    entity=entity,
                    diagnostic=diagnostic,
                )

    # ========================================================
    # phase update
    # ========================================================

    def _update_phase(
        self,
        lifecycle: WeatherEventLifecycleComponent,
    ):

        progress = lifecycle.normalized_age

        old_phase = lifecycle.phase

        # ----------------------------------------------------
        # 生命周期阶段
        # ----------------------------------------------------

        if progress < 0.15:

            lifecycle.phase = EventPhase.FORMING

        elif progress < 0.70:

            lifecycle.phase = EventPhase.MATURE

        elif progress < 1.0:

            lifecycle.phase = EventPhase.DECAYING

        else:

            lifecycle.phase = EventPhase.DISSIPATED

        # ----------------------------------------------------
        # 强度进度
        # ----------------------------------------------------

        if progress < 0.5:

            lifecycle.intensity_progress = (
                progress / 0.5
            )

        else:

            lifecycle.intensity_progress = (
                1.0 - (progress - 0.5) / 0.5
            )

        lifecycle.intensity_progress = max(
            0.0,
            min(
                1.0,
                lifecycle.intensity_progress
            )
        )

        return old_phase != lifecycle.phase

    # ========================================================
    # 日志
    # ========================================================

    def _log_phase(
        self,
        diagnostic: WeatherEventDiagnosticComponent,
        lifecycle: WeatherEventLifecycleComponent,
    ):

        if not self.enable_log:
            return

        print(
            "[WeatherLifetimeSystem] "
            f"{diagnostic.label:<6s} | "
            f"phase={lifecycle.phase.value:<10s} | "
            f"remaining={lifecycle.remaining_hours:7.1f}h | "
            f"intensity={lifecycle.intensity_progress:.2f}"
        )

    # ========================================================
    # cleanup
    # ========================================================

    def _cleanup_entity(
        self,
        world: World,
        entity,
        diagnostic: WeatherEventDiagnosticComponent,
    ):

        if self.enable_log:

            print(
                "[WeatherLifetimeSystem] "
                f"天气事件结束: "
                f"{diagnostic.label}"
            )

        world.remove_entity(entity)