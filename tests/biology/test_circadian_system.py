#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
昼夜节律系统测试

v3.0.3 新增
"""

import pytest
import math

from core.world import World
from core.entity import Entity
from biology.components.circadian_component import CircadianComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from biology.systems.circadian_system import CircadianSystem


class TestCircadianComponent:
    """测试昼夜节律组件"""

    def test_default_values(self):
        comp = CircadianComponent()
        assert comp.phase == 0.0
        assert comp.period == 1440.0
        assert comp.is_diurnal is True
        assert comp.sleep_debt == 0.0
        assert comp.rhythm_strength == 0.8

    def test_serialization(self):
        comp = CircadianComponent(
            phase=0.5,
            sleep_debt=0.3,
            is_diurnal=False,
        )
        data = comp.to_dict()
        restored = CircadianComponent.from_dict(data)
        assert restored.phase == 0.5
        assert restored.sleep_debt == 0.3
        assert restored.is_diurnal is False


class TestCircadianSystem:
    """测试昼夜节律系统"""

    @pytest.fixture
    def world(self):
        return World()

    @pytest.fixture
    def system(self):
        return CircadianSystem()

    def test_phase_update(self, world, system):
        """测试相位更新"""
        entity = world.create_entity()
        circadian = CircadianComponent(phase=0.0, period=1440.0)
        needs = PhysiologyNeedsComponent()
        action = ActionComponent()

        world.add_component(entity, circadian)
        world.add_component(entity, needs)
        world.add_component(entity, action)

        # 更新 720 tick（半天）
        system.update(world, 720.0)

        # 相位应该前进 0.5
        assert abs(circadian.phase - 0.5) < 0.01

    def test_sleep_debt_accumulation(self, world, system):
        """测试睡眠债务累积"""
        entity = world.create_entity()
        circadian = CircadianComponent(sleep_debt=0.0)
        needs = PhysiologyNeedsComponent()
        action = ActionComponent()

        world.add_component(entity, circadian)
        world.add_component(entity, needs)
        world.add_component(entity, action)

        # 更新一段时间
        for _ in range(100):
            system.update(world, 1.0)

        # 睡眠债务应该增加
        assert circadian.sleep_debt > 0.0
        assert circadian.awake_duration == 100

    def test_forced_sleep(self, world, system):
        """测试强制睡眠"""
        entity = world.create_entity()
        circadian = CircadianComponent(sleep_debt=0.9)
        needs = PhysiologyNeedsComponent()
        action = ActionComponent()

        world.add_component(entity, circadian)
        world.add_component(entity, needs)
        world.add_component(entity, action)

        # 更新使睡眠债务超过阈值
        system.update(world, 1.0)

        # 应该触发睡眠
        assert action.current_action == ActionType.SLEEP

    def test_sleep_recovery(self, world, system):
        """测试睡眠恢复"""
        entity = world.create_entity()
        circadian = CircadianComponent(sleep_debt=0.9)
        needs = PhysiologyNeedsComponent()
        action = ActionComponent()
        action.current_action = ActionType.SLEEP
        action.status = ActionStatus.RUNNING

        world.add_component(entity, circadian)
        world.add_component(entity, needs)
        world.add_component(entity, action)

        # 更新一段时间
        for _ in range(500):
            system.update(world, 1.0)

        # 睡眠债务应该减少
        assert circadian.sleep_debt < 0.9

    def test_wake_up(self, world, system):
        """测试自然醒来"""
        entity = world.create_entity()
        circadian = CircadianComponent(sleep_debt=0.1)
        needs = PhysiologyNeedsComponent()
        action = ActionComponent()
        action.current_action = ActionType.SLEEP
        action.status = ActionStatus.RUNNING

        world.add_component(entity, circadian)
        world.add_component(entity, needs)
        world.add_component(entity, action)

        # 更新
        system.update(world, 1.0)

        # 应该醒来
        assert action.current_action == ActionType.IDLE

    def test_night_time_detection(self):
        """测试夜间判断"""
        circadian = CircadianComponent(phase=0.0)  # 午夜
        assert CircadianSystem.is_night_time(circadian) is True

        circadian.phase = 0.5  # 正午
        assert CircadianSystem.is_night_time(circadian) is False

    def test_activity_calculation(self):
        """测试活跃度计算"""
        circadian = CircadianComponent(
            phase=0.5,  # 正午
            activity_peak=0.5,
            is_diurnal=True,
            rhythm_strength=1.0,
        )
        activity = CircadianSystem._calculate_activity_static(circadian)
        assert activity > 0.8  # 正午应该很活跃

        circadian.phase = 0.0  # 午夜
        activity = CircadianSystem._calculate_activity_static(circadian)
        assert activity < 0.2  # 午夜应该不活跃

    def test_nocturnal_activity(self):
        """测试夜行性生物"""
        circadian = CircadianComponent(
            phase=0.0,  # 午夜
            is_diurnal=False,
            rhythm_strength=1.0,
        )
        activity = CircadianSystem._calculate_activity_static(circadian)
        assert activity > 0.8  # 夜行性在午夜活跃

    def test_energy_recovery_rate(self, world, system):
        """测试节律对能量恢复的影响"""
        entity = world.create_entity()
        circadian = CircadianComponent(
            phase=0.5,  # 正午（活跃期）
            is_diurnal=True,
        )
        needs = PhysiologyNeedsComponent()
        action = ActionComponent()

        world.add_component(entity, circadian)
        world.add_component(entity, needs)
        world.add_component(entity, action)

        system.update(world, 1.0)

        # 活跃期能量应该增加
        assert needs.energy > 70.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])