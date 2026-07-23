#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
季节推进系统 — 纯天文版

职责：推进年份进度。
不再切换季节状态、不再提供固定气候偏移。
"""

from core.world import World
from core.system import System
from environment.season.season_component import SeasonComponent


class SeasonSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    季节系统

    仅推进年份进度，所有季节效应由 PhysicalWeatherSystem
    通过天文参数实时计算。
    """

    def update(self, world: World, delta_hours: float):
        # 防御：使用 world.get_world_component 替代 entity.get_component
        season = world.get_world_component(SeasonComponent)
        if season is None:
            return

        season.year_progress += delta_hours

        # 循环年份
        if season.year_progress > season.year_length_hours:
            season.year_progress -= season.year_length_hours