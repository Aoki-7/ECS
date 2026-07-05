#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:time_component.py
@说明:时间组件
@时间:2026/03/14 11:37:50
@作者:Sherry
@版本:1.0
'''



from core.component import Component


class TimeComponent(Component):
    """
    世界时间数据组件（World Time State）

    该组件只负责保存时间状态数据，不包含任何时间推进逻辑。
    时间推进逻辑应由 TimeSystem 负责。

    设计目标：
    - 作为 ECS 架构中的纯数据组件
    - 支持时间序列化/存档
    - 提供常用派生时间属性
    """

    __slots__ = (
        "day_hours",     # 一天包含的小时数（例如现实世界为24）
        "days_per_year", # 一年包含的天数（例如现实世界为365）
        "hour",          # 当前天内时间（单位：小时）
        "day_of_year",   # 当前是本年的第几天（1 ~ days_per_year）
        "year",          # 当前年份（从1开始计数）
        "total_hours",   # 总小时数
        "day_changed",   # 本次系统更新是否跨天（由 TimeSystem 写入）
        "year_changed",  # 本次系统更新是否跨年（由 TimeSystem 写入）
    )

    def __init__(
        self,
        day_hours: float = 24.0,   # 一天的小时数（时间系统基础规则）
        days_per_year: int = 365,  # 一年的天数（时间系统基础规则）
        hour: float = 0.0,         # 当前天内时间（0 ~ day_hours）
        day_of_year: int = 1,      # 当前是本年的第几天（1开始）
        year: int = 1,             # 当前年份（从1开始）
    ):
        # =====
        # 时间规则（世界基础时间单位）
        # =====

        # 一天包含多少小时（用于不同世界设定）
        self.day_hours = float(day_hours)

        # 一年包含多少天
        self.days_per_year = int(days_per_year)

        # =====
        # 当前时间状态
        # =====

        # 当前天内时间（单位：小时）
        # 例如 6.5 表示早上6点30
        self.hour = float(hour)

        # 当前是本年的第几天
        # 范围：1 ~ days_per_year
        self.day_of_year = int(day_of_year)

        # 当前年份（从1开始）
        self.year = int(year)

        # 总小时数
        self.total_hours = float(hour)

        # =====
        # 时间变化标记（系统写入）
        # =====

        # 本次时间推进是否跨天
        # True 表示 hour 溢出导致进入下一天
        self.day_changed: bool = False

        # 本次时间推进是否跨年
        # True 表示 day_of_year 溢出导致进入下一年
        self.year_changed: bool = False

    # ==
    # 常用派生属性
    # ==

    def to_dict(self) -> dict:
        """
        导出为字典（用于存档/序列化）
        """
        return {
            "当前时间": f"{self.hour} / {self.day_hours}",
            "一年天数": f"{self.days_per_year} / {self.day_of_year}",
            "年份": self.year,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimeComponent":
        """
        从字典恢复时间组件（用于读档）
        """
        return cls(
            day_hours=data["一天小时数"],
            days_per_year=data["一年天数"],
            hour=data["当前小时"],
            day_of_year=data["本年第几天"],
            year=data["年份"],
        )