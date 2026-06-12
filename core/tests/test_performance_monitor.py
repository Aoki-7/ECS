#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能监控系统测试
"""

import pytest
import time

from core.performance_monitor import PerformanceMonitor, monitored_update
from core.system import System
from core.world import World


class DummySystem(System):
    """测试用的虚拟系统"""

    def update(self, world: World, dt: float = 1.0) -> None:
        time.sleep(0.001)  # 模拟 1ms 工作


class MonitoredSystem(System):
    """带监控的虚拟系统"""

    @monitored_update
    def update(self, world: World, dt: float = 1.0) -> None:
        time.sleep(0.002)  # 模拟 2ms 工作


class TestPerformanceMonitor:
    """测试性能监控器"""

    def setup_method(self):
        """每个测试前重置"""
        PerformanceMonitor.reset_instance()
        self.monitor = PerformanceMonitor.get_instance()

    def teardown_method(self):
        """每个测试后清理"""
        self.monitor.disable()
        PerformanceMonitor.reset_instance()

    def test_singleton(self):
        """测试单例模式"""
        m1 = PerformanceMonitor.get_instance()
        m2 = PerformanceMonitor.get_instance()
        assert m1 is m2

    def test_enable_disable(self):
        """测试启用/禁用"""
        assert not self.monitor.is_enabled()
        self.monitor.enable()
        assert self.monitor.is_enabled()
        self.monitor.disable()
        assert not self.monitor.is_enabled()

    def test_record_when_enabled(self):
        """启用时记录数据"""
        self.monitor.enable()
        self.monitor.record("TestSystem", 5.0)

        stats = self.monitor.get_stats("TestSystem")
        assert stats["TestSystem"]["count"] == 1
        assert stats["TestSystem"]["avg_ms"] == 5.0

    def test_no_record_when_disabled(self):
        """禁用时不会记录"""
        self.monitor.record("TestSystem", 5.0)
        stats = self.monitor.get_stats("TestSystem")
        assert stats["TestSystem"]["count"] == 0

    def test_multiple_records(self):
        """多次记录统计"""
        self.monitor.enable()
        for i in range(10):
            self.monitor.record("TestSystem", float(i))

        stats = self.monitor.get_stats("TestSystem")["TestSystem"]
        assert stats["count"] == 10
        assert stats["avg_ms"] == 4.5  # (0+1+...+9)/10
        assert stats["max_ms"] == 9.0
        assert stats["min_ms"] == 0.0

    def test_max_history(self):
        """测试历史记录上限"""
        self.monitor = PerformanceMonitor(max_history=5)
        self.monitor.enable()

        for i in range(10):
            self.monitor.record("TestSystem", float(i))

        stats = self.monitor.get_stats("TestSystem")["TestSystem"]
        assert stats["count"] == 5  # 只保留最近 5 条

    def test_get_slow_systems(self):
        """测试获取慢系统"""
        self.monitor.enable()
        self.monitor.record("FastSystem", 0.5)
        self.monitor.record("SlowSystem", 2.0)
        self.monitor.record("VerySlowSystem", 5.0)

        slow = self.monitor.get_slow_systems(threshold_ms=1.0)
        assert len(slow) == 2
        assert slow[0][0] == "VerySlowSystem"
        assert slow[1][0] == "SlowSystem"

    def test_clear(self):
        """测试清空数据"""
        self.monitor.enable()
        self.monitor.record("TestSystem", 5.0)
        assert self.monitor.get_stats()["TestSystem"]["count"] == 1

        self.monitor.clear()
        assert len(self.monitor.get_stats()) == 0

    def test_decorator_with_monitor_enabled(self):
        """测试装饰器在启用时记录"""
        self.monitor.enable()
        world = World()
        system = MonitoredSystem()

        system.update(world, 1.0)

        stats = self.monitor.get_stats("MonitoredSystem")
        assert stats["MonitoredSystem"]["count"] == 1
        assert stats["MonitoredSystem"]["avg_ms"] >= 1.0  # 至少 1.0ms（允许性能波动）

    def test_decorator_with_monitor_disabled(self):
        """测试装饰器在禁用时不会记录"""
        world = World()
        system = MonitoredSystem()

        system.update(world, 1.0)

        stats = self.monitor.get_stats("MonitoredSystem")
        assert stats["MonitoredSystem"]["count"] == 0

    def test_frame_summary(self):
        """测试帧摘要"""
        self.monitor.enable()
        self.monitor.record("SystemA", 5.0)
        self.monitor.record("SystemB", 3.0)

        summary = self.monitor.get_frame_summary()
        assert "性能监控摘要" in summary
        assert "SystemA" in summary
        assert "SystemB" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
