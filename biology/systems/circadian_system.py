#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昼夜节律系统

v3.0.3 新增 — P0

职责：
    - 更新所有生物的昼夜节律相位
    - 根据节律状态影响行为和生理
    - 管理睡眠/觉醒转换

依赖：
    - CircadianComponent
    - PhysiologyNeedsComponent（energy, sleepiness）
    - ActionComponent（设置 SLEEP 动作）
    - TimeComponent（获取当前时间）
"""

import math
from typing import Optional

from core.system import System
from core.world import World

from biology.components.circadian_component import CircadianComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus

import logging

logger = logging.getLogger(__name__)


class CircadianSystem(System):
    """
    昼夜节律系统

    每帧更新生物的节律相位，并根据节律状态：
    - 增加睡眠债务
    - 影响能量恢复速率
    - 在适当时候触发睡眠意图
    """

    tick_interval = 1  # 每帧执行（节律需要连续更新）

    # 睡眠债务累积速率（每 tick）
    SLEEP_DEBT_RATE = 0.0005
    # 睡眠债务恢复速率（每 tick 睡眠中）
    SLEEP_RECOVERY_RATE = 0.002
    # 强制睡眠阈值
    FORCED_SLEEP_THRESHOLD = 0.85
    # 自然醒来阈值
    WAKE_THRESHOLD = 0.15
    # 节律对能量的影响系数
    RHYTHM_ENERGY_FACTOR = 0.3

    def update(self, world: World, dt: float) -> None:
        """更新所有生物的昼夜节律"""
        for entity, (circadian, needs, action) in world.get_components(
            CircadianComponent, PhysiologyNeedsComponent, ActionComponent
        ):
            if circadian is None or needs is None:
                continue

            self._update_phase(circadian, dt)
            self._update_sleep_debt(circadian, needs, action)
            self._apply_rhythm_effects(circadian, needs)

    def _update_phase(self, circadian: CircadianComponent, dt: float) -> None:
        """更新节律相位"""
        # 相位前进：dt / period
        phase_delta = dt / circadian.period
        circadian.phase = (circadian.phase + phase_delta) % 1.0

    def _update_sleep_debt(
        self,
        circadian: CircadianComponent,
        needs: PhysiologyNeedsComponent,
        action: ActionComponent,
    ) -> None:
        """更新睡眠债务，管理睡眠/觉醒"""
        is_sleeping = action.current_action == ActionType.SLEEP

        if is_sleeping:
            # 睡眠中：减少睡眠债务
            circadian.sleep_debt = max(
                0.0,
                circadian.sleep_debt - self.SLEEP_RECOVERY_RATE
            )
            circadian.awake_duration = 0

            # 检查是否应该醒来
            if circadian.sleep_debt <= self.WAKE_THRESHOLD:
                # 自然醒来
                action.current_action = ActionType.IDLE
                action.status = ActionStatus.IDLE
                circadian.sleep_quality = self._calculate_sleep_quality(circadian)
        else:
            # 清醒中：增加睡眠债务
            circadian.awake_duration += 1
            circadian.sleep_debt = min(
                1.0,
                circadian.sleep_debt + self.SLEEP_DEBT_RATE
            )

            # 检查是否应该入睡
            if circadian.sleep_debt >= self.FORCED_SLEEP_THRESHOLD:
                # 强制睡眠
                action.current_action = ActionType.SLEEP
                action.status = ActionStatus.RUNNING
                circadian.last_sleep_tick = getattr(
                    circadian, '_current_tick', 0
                )

    def _apply_rhythm_effects(
        self,
        circadian: CircadianComponent,
        needs: PhysiologyNeedsComponent,
    ) -> None:
        """应用节律对生理的影响"""
        # 计算当前节律活跃度（1.0=高峰，0.0=低谷）
        activity = self._calculate_activity(circadian)

        # 节律影响能量恢复速率
        # 在活跃期：能量恢复较快
        # 在休息期：能量恢复较慢（甚至消耗）
        energy_factor = 1.0 + (activity - 0.5) * self.RHYTHM_ENERGY_FACTOR
        # 直接修改 energy，模拟节律影响
        base_recovery = 0.01
        recovery = base_recovery * energy_factor
        needs.energy = min(needs.max_energy, needs.energy + recovery)

    def _calculate_activity(self, circadian: CircadianComponent) -> float:
        """
        计算当前节律活跃度

        Returns:
            0.0-1.0，越高越活跃
        """
        # 与活动高峰的距离
        dist_to_peak = abs(circadian.phase - circadian.activity_peak)
        dist_to_peak = min(dist_to_peak, 1.0 - dist_to_peak)

        # 余弦曲线模拟节律
        activity = math.cos(dist_to_peak * math.pi * 2) * 0.5 + 0.5

        # 根据昼行性/夜行性调整
        if not circadian.is_diurnal:
            activity = 1.0 - activity

        # 应用节律强度
        activity = activity * circadian.rhythm_strength + 0.5 * (1 - circadian.rhythm_strength)

        return activity

    def _calculate_sleep_quality(self, circadian: CircadianComponent) -> float:
        """计算睡眠质量"""
        # 睡眠时长因素
        duration_factor = min(1.0, circadian.awake_duration / 480.0)  # 8小时基准

        # 节律同步因素（在睡眠高峰期入睡质量更好）
        dist_to_sleep_peak = abs(circadian.phase - circadian.sleep_peak)
        dist_to_sleep_peak = min(dist_to_sleep_peak, 1.0 - dist_to_sleep_peak)
        rhythm_factor = 1.0 - dist_to_sleep_peak * 2

        return (duration_factor + rhythm_factor) / 2

    @staticmethod
    def is_night_time(circadian: CircadianComponent) -> bool:
        """判断是否为夜间（简化：相位 0.75-0.25 为夜间）"""
        phase = circadian.phase
        return phase > 0.75 or phase < 0.25

    @staticmethod
    def is_active_time(circadian: CircadianComponent) -> bool:
        """判断是否为活跃时间"""
        activity = CircadianSystem._calculate_activity_static(circadian)
        return activity > 0.5

    @staticmethod
    def _calculate_activity_static(circadian: CircadianComponent) -> float:
        """静态方法计算活跃度"""
        dist_to_peak = abs(circadian.phase - circadian.activity_peak)
        dist_to_peak = min(dist_to_peak, 1.0 - dist_to_peak)
        activity = math.cos(dist_to_peak * math.pi * 2) * 0.5 + 0.5
        if not circadian.is_diurnal:
            activity = 1.0 - activity
        return activity * circadian.rhythm_strength + 0.5 * (1 - circadian.rhythm_strength)
