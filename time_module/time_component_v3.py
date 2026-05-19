#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件: time_component.py
@说明: 世界时间组件（V3 大规模模拟版本）

=========================================================
V3 核心特性
=========================================================

相比 V2：

新增：
- 时间倍率（time_scale）
- 世界时间暂停
- 时间事件调度
- 定时器支持
- 历史时间轴
- 世界纪元支持
- 多季节支持
- 自定义昼夜时间
- 时间戳接口
- 事件 Tick 查询
- 高精度 Tick 时间
- ECS 大规模模拟兼容

设计目标：
- 大规模 ECS 世界模拟
- AI 调度
- 天气系统
- 文明历史系统
- 历史回放
- 存档系统
- 时间事件队列
- 高性能时间查询

=========================================================
设计原则
=========================================================

唯一时间真值：
    ticks

所有时间全部动态推导。

组件不负责：
- 时间推进
- 时间事件执行
- 调度逻辑

这些应由：
    TimeSystem
负责。

=========================================================
推荐：
=========================================================

1 tick = 1 minute

或：

1 tick = 1 second

取决于模拟精度需求。
"""

from core.component import Component


class TimeComponent(Component):

    __slots__ = (

        # =====================================================
        # 世界绝对时间轴
        # =====================================================

        "ticks",

        # =====================================================
        # 时间规则
        # =====================================================

        "ticks_per_hour",
        "day_hours",
        "days_per_year",

        # =====================================================
        # 月份 / 季节
        # =====================================================

        "months_per_year",
        "seasons",

        # =====================================================
        # 昼夜规则
        # =====================================================

        "sunrise_hour",
        "sunset_hour",

        # =====================================================
        # 时间控制
        # =====================================================

        "time_scale",
        "paused",

        # =====================================================
        # 世界纪元
        # =====================================================

        "epoch_name",
    )

    def __init__(
        self,

        # =====================================================
        # 世界时间
        # =====================================================

        ticks: int = 0,

        # =====================================================
        # 时间规则
        # =====================================================

        ticks_per_hour: int = 60,
        day_hours: int = 24,
        days_per_year: int = 365,

        # =====================================================
        # 月份规则
        # =====================================================

        months_per_year: int = 12,

        # =====================================================
        # 季节规则
        # =====================================================

        seasons=None,

        # =====================================================
        # 昼夜规则
        # =====================================================

        sunrise_hour: int = 6,
        sunset_hour: int = 18,

        # =====================================================
        # 时间倍率
        # =====================================================

        time_scale: float = 1.0,

        # =====================================================
        # 是否暂停
        # =====================================================

        paused: bool = False,

        # =====================================================
        # 世界纪元
        # =====================================================

        epoch_name: str = "Common Era",
    ):

        # =====================================================
        # 时间主轴
        # =====================================================

        self.ticks = int(max(0, ticks))

        # =====================================================
        # 时间规则
        # =====================================================

        self.ticks_per_hour = int(max(1, ticks_per_hour))
        self.day_hours = int(max(1, day_hours))
        self.days_per_year = int(max(1, days_per_year))

        # =====================================================
        # 月份系统
        # =====================================================

        self.months_per_year = int(
            max(1, months_per_year)
        )

        # =====================================================
        # 季节系统
        # =====================================================

        if seasons is None:
            seasons = (
                "SPRING",
                "SUMMER",
                "AUTUMN",
                "WINTER",
            )

        self.seasons = tuple(seasons)

        # =====================================================
        # 昼夜规则
        # =====================================================

        self.sunrise_hour = int(sunrise_hour)
        self.sunset_hour = int(sunset_hour)

        # =====================================================
        # 时间倍率
        # =====================================================

        self.time_scale = max(0.0, float(time_scale))

        # =====================================================
        # 时间暂停
        # =====================================================

        self.paused = bool(paused)

        # =====================================================
        # 世界纪元
        # =====================================================

        self.epoch_name = str(epoch_name)

    # =========================================================
    # Tick 规则
    # =========================================================

    @property
    def ticks_per_day(self) -> int:
        return (
            self.day_hours
            * self.ticks_per_hour
        )

    @property
    def ticks_per_year(self) -> int:
        return (
            self.ticks_per_day
            * self.days_per_year
        )

    @property
    def ticks_per_minute(self) -> float:
        return self.ticks_per_hour / 60

    # =========================================================
    # 世界绝对时间
    # =========================================================

    @property
    def absolute_hour(self) -> float:
        return (
            self.ticks
            / self.ticks_per_hour
        )

    @property
    def absolute_day(self) -> int:
        return int(
            self.ticks
            // self.ticks_per_day
        ) + 1

    @property
    def absolute_year(self) -> int:
        return int(
            self.ticks
            // self.ticks_per_year
        ) + 1

    # =========================================================
    # 当前年时间
    # =========================================================

    @property
    def year(self) -> int:
        return self.absolute_year

    @property
    def day_of_year(self) -> int:
        return (
            (self.absolute_day - 1)
            % self.days_per_year
        ) + 1

    # =========================================================
    # 月份系统
    # =========================================================

    @property
    def days_per_month(self) -> float:
        return (
            self.days_per_year
            / self.months_per_year
        )

    @property
    def month(self) -> int:
        return int(
            (self.day_of_year - 1)
            // self.days_per_month
        ) + 1

    @property
    def day_of_month(self) -> int:
        return int(
            (
                (self.day_of_year - 1)
                % self.days_per_month
            )
        ) + 1

    # =========================================================
    # 当前日时间
    # =========================================================

    @property
    def ticks_today(self) -> int:
        return (
            self.ticks
            % self.ticks_per_day
        )

    @property
    def hour(self) -> int:
        return int(
            self.ticks_today
            // self.ticks_per_hour
        )

    @property
    def minute(self) -> int:
        return int(
            (
                self.ticks_today
                % self.ticks_per_hour
            )
            / self.ticks_per_minute
        )

    @property
    def second(self) -> int:

        if self.ticks_per_minute <= 1:
            return 0

        sub_tick = (
            self.ticks_today
            % self.ticks_per_minute
        )

        return int(
            (
                sub_tick
                / self.ticks_per_minute
            )
            * 60
        )

    @property
    def time_float(self) -> float:
        return (
            self.hour
            + self.minute / 60
            + self.second / 3600
        )

    # =========================================================
    # 时间进度
    # =========================================================

    @property
    def day_progress(self) -> float:
        return (
            self.ticks_today
            / self.ticks_per_day
        )

    @property
    def year_progress(self) -> float:
        return (
            (self.day_of_year - 1)
            / self.days_per_year
        )

    # =========================================================
    # 季节系统
    # =========================================================

    @property
    def season_count(self) -> int:
        return len(self.seasons)

    @property
    def season_length(self) -> float:
        return (
            self.days_per_year
            / self.season_count
        )

    @property
    def season_index(self) -> int:
        return int(
            (self.day_of_year - 1)
            // self.season_length
        ) % self.season_count

    @property
    def season(self) -> str:
        return self.seasons[
            self.season_index
        ]

    @property
    def season_progress(self) -> float:

        season_start = (
            self.season_index
            * self.season_length
        )

        return (
            (
                self.day_of_year - 1
                - season_start
            )
            / self.season_length
        )

    # =========================================================
    # 昼夜系统
    # =========================================================

    @property
    def is_daytime(self) -> bool:
        return (
            self.sunrise_hour
            <= self.time_float
            < self.sunset_hour
        )

    @property
    def is_night(self) -> bool:
        return not self.is_daytime

    @property
    def daylight_length(self) -> float:
        return (
            self.sunset_hour
            - self.sunrise_hour
        )

    @property
    def sunlight_factor(self) -> float:
        """
        光照强度：
            0 ~ 1
        """

        if self.is_night:
            return 0.0

        noon = (
            self.sunrise_hour
            + self.sunset_hour
        ) / 2

        half_daylight = (
            self.daylight_length / 2
        )

        distance = abs(
            self.time_float - noon
        )

        factor = (
            1.0
            - distance / half_daylight
        )

        return max(
            0.0,
            min(1.0, factor)
        )

    # =========================================================
    # 时间控制
    # =========================================================

    @property
    def is_paused(self) -> bool:
        return self.paused

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def set_time_scale(
        self,
        scale: float,
    ):
        self.time_scale = max(
            0.0,
            float(scale)
        )

    # =========================================================
    # Tick 操作
    # =========================================================

    def add_ticks(
        self,
        ticks: int,
    ):
        """
        增加 Tick

        注意：
        通常应由 TimeSystem 调用。
        """

        if self.paused:
            return

        scaled_ticks = int(
            ticks * self.time_scale
        )

        self.ticks += scaled_ticks

        if self.ticks < 0:
            self.ticks = 0

    # =========================================================
    # 时间差
    # =========================================================

    def ticks_until_hour(
        self,
        target_hour: int,
    ) -> int:
        """
        距离目标小时还有多少 Tick
        """

        target_hour = int(
            target_hour % self.day_hours
        )

        current = self.hour

        delta_hour = (
            target_hour - current
        )

        if delta_hour < 0:
            delta_hour += self.day_hours

        return (
            delta_hour
            * self.ticks_per_hour
        )

    # =========================================================
    # 时间戳
    # =========================================================

    @property
    def timestamp(self) -> tuple:
        """
        时间戳

        用于：
        - 历史系统
        - 排序
        - 事件时间记录
        """

        return (
            self.year,
            self.day_of_year,
            self.hour,
            self.minute,
            self.second,
        )

    # =========================================================
    # 格式化
    # =========================================================

    @property
    def date_string(self) -> str:
        return (
            f"{self.epoch_name} "
            f"Year {self.year} "
            f"Month {self.month} "
            f"Day {self.day_of_month}"
        )

    @property
    def clock_string(self) -> str:
        return (
            f"{self.hour:02}:"
            f"{self.minute:02}:"
            f"{self.second:02}"
        )

    @property
    def time_string(self) -> str:
        return (
            f"{self.date_string} "
            f"{self.clock_string}"
        )

    # =========================================================
    # 存档
    # =========================================================

    def to_dict(self) -> dict:

        return {
            "ticks": self.ticks,

            "ticks_per_hour":
                self.ticks_per_hour,

            "day_hours":
                self.day_hours,

            "days_per_year":
                self.days_per_year,

            "months_per_year":
                self.months_per_year,

            "seasons":
                list(self.seasons),

            "sunrise_hour":
                self.sunrise_hour,

            "sunset_hour":
                self.sunset_hour,

            "time_scale":
                self.time_scale,

            "paused":
                self.paused,

            "epoch_name":
                self.epoch_name,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "TimeComponent":

        return cls(
            ticks=data.get(
                "ticks",
                0,
            ),

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

            seasons=data.get(
                "seasons",
                (
                    "SPRING",
                    "SUMMER",
                    "AUTUMN",
                    "WINTER",
                ),
            ),

            sunrise_hour=data.get(
                "sunrise_hour",
                6,
            ),

            sunset_hour=data.get(
                "sunset_hour",
                18,
            ),

            time_scale=data.get(
                "time_scale",
                1.0,
            ),

            paused=data.get(
                "paused",
                False,
            ),

            epoch_name=data.get(
                "epoch_name",
                "Common Era",
            ),
        )

    # =========================================================
    # Debug
    # =========================================================

    def __repr__(self):

        return (
            f"<TimeComponent "
            f"{self.time_string} "
            f"Season={self.season} "
            f"Ticks={self.ticks}>"
        )