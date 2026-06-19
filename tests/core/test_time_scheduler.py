#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间事件调度器测试

v3.0.1
"""

import unittest

from time_module.time_scheduler import TimeScheduler, ScheduledEvent


class TestTimeScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = TimeScheduler()
        self.scheduler.clear()

    def test_schedule_once(self):
        """一次性事件"""
        called = []

        def callback():
            called.append(True)

        self.scheduler.schedule(tick=10, callback=callback)
        self.assertEqual(self.scheduler.get_pending_count(), 1)

        results = self.scheduler.update(10)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(called), 1)
        self.assertEqual(self.scheduler.get_pending_count(), 0)

    def test_schedule_periodic(self):
        """周期性事件"""
        counter = [0]

        def callback():
            counter[0] += 1

        self.scheduler.schedule(
            tick=10, callback=callback, interval=5, repeat=-1
        )

        self.scheduler.update(10)
        self.assertEqual(counter[0], 1)

        self.scheduler.update(15)
        self.assertEqual(counter[0], 2)

        self.scheduler.update(20)
        self.assertEqual(counter[0], 3)

    def test_cancel_event(self):
        """取消事件"""
        called = []

        def callback():
            called.append(True)

        event_id = self.scheduler.schedule(tick=10, callback=callback)
        self.scheduler.cancel(event_id)

        results = self.scheduler.update(10)
        self.assertEqual(len(results), 0)
        self.assertEqual(len(called), 0)

    def test_order_execution(self):
        """按顺序执行"""
        order = []

        def make_callback(n):
            def callback():
                order.append(n)
            return callback

        self.scheduler.schedule(tick=20, callback=make_callback(2))
        self.scheduler.schedule(tick=10, callback=make_callback(1))
        self.scheduler.schedule(tick=30, callback=make_callback(3))

        self.scheduler.update(25)
        self.assertEqual(order, [1, 2])

    def test_callback_with_args(self):
        """带参数的回调"""
        result = []

        def callback(a, b, c=None):
            result.append((a, b, c))

        self.scheduler.schedule(
            tick=5, callback=callback, args=(1, 2), kwargs={"c": 3}
        )
        self.scheduler.update(5)

        self.assertEqual(result, [(1, 2, 3)])

    def test_get_next_tick(self):
        """获取下一个触发 tick"""
        self.scheduler.schedule(tick=100, callback=lambda: None)
        self.assertEqual(self.scheduler.get_next_tick(), 100)

    def test_clear(self):
        """清空"""
        self.scheduler.schedule(tick=10, callback=lambda: None)
        self.scheduler.clear()
        self.assertEqual(self.scheduler.get_pending_count(), 0)


if __name__ == "__main__":
    unittest.main()
