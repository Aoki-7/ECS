#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
季节组件（世界级）— 纯天文参数版

不再存储"春夏秋冬"枚举或固定气候偏移。
只保留年份进度，供天文计算使用。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class SeasonComponent(Component):
    """
    季节组件

    仅保存年份循环进度，所有季节效应由天文参数实时推导。
    """

    # 一年长度（小时）
    year_length_hours: float = 360 * 24

    # 当前年份时间进度（小时）
    year_progress: float = 0.0

    def to_dict(self):
        return {
            "year_length_hours": self.year_length_hours,
            "year_progress": self.year_progress,
        }
