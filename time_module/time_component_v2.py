#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: time_component.py
@说明: 世界时间组件（V2 Tick 时间轴版本）
@时间:2026/05/19 07:27:38
@作者:Sherry
@版本:2.0

核心设计：
- 使用“统一 Tick 时间轴”作为唯一时间真值
- 所有时间数据全部动态推导
- 不保存冗余状态
- 不保存瞬时事件状态
- 适用于 ECS / 大规模世界模拟

设计目标：
- 高性能
- 强一致性
- 易存档
- 易回放
- 易扩展
- 易于事件调度
- 支持不同世界时间规则

推荐：
1 tick = 1 minute

例如：
ticks = 60
表示世界经过 1 小时
"""


from core.component import Component


class TimeComponent(Component):
    """
    世界时间组件（统一 Tick 时间轴）

    时间系统唯一真值：
        ticks

    所有：
    - 年
    - 天
    - 小时
    - 分钟
    - 季节
    - 昼夜

    全部由 ticks 动态推导。

    注意：
    本组件不负责时间推进。
    时间推进应由 TimeSystem 负责。
    """

    __slots__ = (
        # ===== 时间主轴 =====
        "ticks",

        # ===== 时间规则 =====
        "ticks_per_hour",
        "day_hours",
        "days_per_year",

        # ===== 可选世界规则 =====
        "months_per_year",
        "days_per_month",
    )

    def __init__(
        self,

        # ===== 世界当前时间 =====
        ticks: int = 0,

        # ===== 世界时间规则 =====
        ticks_per_hour: int = 60,  # 1 tick = 1 minute
        day_hours: int = 24,
        days_per_year: int = 365,

        # ===== 月份系统（可选）=====
        months_per_year: int = 12,
    ):
        # ===== 时间主轴 =====

        # 世界起点以来累计 Tick
        # 唯一时间真值
        self.ticks = int(max(0, ticks))

        # ===== 时间规则 =====

        # 每小时包含多少 Tick
        self.ticks_per_hour = int(max(1, ticks_per_hour))

        # 一天多少小时
        self.day_hours = int(max(1, day_hours))

        # 一年多少天
        self.days_per_year = int(max(1, days_per_year))

        # ===== 月份规则 =====

        self.months_per_year = int(max(1, months_per_year))

        # 平均每月天数
        self.days_per_month = (
            self.days_per_year / self.months_per_year
        )

    # =========================================================
    # 基础时间单位
    # =========================================================

    @property
    def ticks_per_day(self) -> int:
        """
        一天包含多少 Tick
        """
        return self.day_hours * self.ticks_per_hour

    @property
    def ticks_per_year(self) -> int:
        """
        一年包含多少 Tick
        """
        return self.ticks_per_day * self.days_per_year

    # =========================================================
    # 世界绝对时间
    # =========================================================

    @property
    def absolute_hour(self) -> float:
        """
        世界绝对小时数
        """
        return self.ticks / self.ticks_per_hour

    @property
    def absolute_day(self) -> int:
        """
        世界绝对天数（从1开始）
        """
        return int(self.ticks // self.ticks_per_day) + 1

    @property
    def absolute_year(self) -> int:
        """
        世界绝对年份（从1开始）
        """
        return int(
            self.ticks // self.ticks_per_year
        ) + 1

    # =========================================================
    # 当前年时间
    # =========================================================

    @property
    def year(self) -> int:
        """
        当前年份（从1开始）
        """
        return self.absolute_year

    @property
    def day_of_year(self) -> int:
        """
        当前是本年第几天（1开始）
        """
        return (
            (self.absolute_day - 1)
            % self.days_per_year
        ) + 1

    # =========================================================
    # 当前日时间
    # =========================================================

    @property
    def hour(self) -> int:
        """
        当前小时
        """
        ticks_today = self.ticks % self.ticks_per_day

        return int(
            ticks_today // self.ticks_per_hour
        )

    @property
    def minute(self) -> int:
        """
        当前分钟
        """
        return int(
            self.ticks % self.ticks_per_hour
        )

    @property
    def time_float(self) -> float:
        """
        当前时间（浮点小时）

        示例：
            13.5 -> 13:30
        """
        return (
            self.hour
            + self.minute / self.ticks_per_hour
        )

    # =========================================================
    # 月份系统
    # =========================================================

    @property
    def month(self) -> int:
        """
        当前月份（1开始）
        """
        return int(
            (self.day_of_year - 1)
            // self.days_per_month
        ) + 1

    # =========================================================
    # 时间进度
    # =========================================================

    @property
    def day_progress(self) -> float:
        """
        当天时间进度（0~1）
        """
        return (
            (self.hour * self.ticks_per_hour + self.minute)
            / self.ticks_per_day
        )

    @property
    def year_progress(self) -> float:
        """
        当年时间进度（0~1）
        """
        return (
            (self.day_of_year - 1)
            / self.days_per_year
        )

    # =========================================================
    # 季节系统
    # =========================================================

    @property
    def season(self) -> str:
        """
        当前季节
        """

        season_length = self.days_per_year / 4

        index = int(
            (self.day_of_year - 1)
            // season_length
        )

        seasons = (
            "SPRING",
            "SUMMER",
            "AUTUMN",
            "WINTER",
        )

        return seasons[index % 4]

    # =========================================================
    # 昼夜系统
    # =========================================================

    @property
    def is_daytime(self) -> bool:
        """
        是否白天

        默认：
            6:00 ~ 18:00
        """
        return 6 <= self.hour < 18

    @property
    def is_night(self) -> bool:
        """
        是否夜晚
        """
        return not self.is_daytime

    @property
    def sunlight_factor(self) -> float:
        """
        光照强度（0~1）

        用于：
        - 天气系统
        - 温度系统
        - 植物系统
        - AI行为系统
        """

        # 夜晚
        if self.is_night:
            return 0.0

        # 白天：
        # 6 -> 0
        # 12 -> 1
        # 18 -> 0

        noon = 12

        distance = abs(self.time_float - noon)

        factor = 1.0 - (distance / 6)

        return max(0.0, min(1.0, factor))

    # =========================================================
    # 时间推进辅助
    # =========================================================

    def add_ticks(self, ticks: int):
        """
        增加 Tick

        注意：
        正常应由 TimeSystem 调用
        """
        self.ticks += int(ticks)

        if self.ticks < 0:
            self.ticks = 0

    # =========================================================
    # 格式化
    # =========================================================

    @property
    def time_string(self) -> str:
        """
        格式化时间

        示例：
            Year 3 Day 120 08:30
        """
        return (
            f"Year {self.year} "
            f"Day {self.day_of_year} "
            f"{self.hour:02}:{self.minute:02}"
        )

    # =========================================================
    # 序列化
    # =========================================================

    def to_dict(self) -> dict:
        """
        导出存档
        """
        return {
            "ticks": self.ticks,
            "ticks_per_hour": self.ticks_per_hour,
            "day_hours": self.day_hours,
            "days_per_year": self.days_per_year,
            "months_per_year": self.months_per_year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimeComponent":
        """
        从存档恢复
        """
        return cls(
            ticks=data.get("ticks", 0),
            ticks_per_hour=data.get(
                "ticks_per_hour",
                60,
            ),
            day_hours=data.get(
                "day_hours",
                24,
            ),
            days_per_year=data.get(
                "days_per_year",
                365,
            ),
            months_per_year=data.get(
                "months_per_year",
                12,
            ),
        )

    # =========================================================
    # Debug
    # =========================================================

    def __repr__(self):
        return (
            f"<TimeComponent "
            f"{self.time_string} "
            f"ticks={self.ticks}>"
        )