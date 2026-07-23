#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
季节变化系统

v3.3 新增 — P0

职责：
    - 根据时间推进计算当前季节
    - 季节影响温度、降水、光照等环境参数
    - 支持南北半球季节反转

设计原则：
    - 季节基于一年中的天数计算（简化模型）
    - 每个季节有预设的环境参数偏移
    - 过渡期间平滑插值
"""

import math
from typing import Dict, Optional

from core.system import System
from core.world import World

from environment.season.season_component import SeasonComponent
from environment.environment_component import EnvironmentComponent
from environment.astronomy.components.celestial_body_component import CelestialBodyComponent
from environment.astronomy.systems.tidal_system import TidalSystem
from time_module.time_component import TimeComponent

import logging

logger = logging.getLogger(__name__)


class SeasonChangeSystem(System):
    """
    季节变化系统

    每帧更新：
    1. 根据当前时间计算季节
    2. 应用季节对环境参数的影响
    3. 季节过渡时平滑插值
    """

    tick_interval = 10  # 每10帧执行一次（季节变化较慢）

    # 季节定义（北半球）
    SEASONS = ["spring", "summer", "autumn", "winter"]

    # 季节起始日（一年中的第几天）
    SEASON_START_DAYS = {
        "spring": 80,   # 3月21日左右
        "summer": 172,  # 6月21日左右
        "autumn": 266,  # 9月23日左右
        "winter": 355,  # 12月21日左右
    }

    # 季节对环境参数的影响（偏移量）
    SEASON_EFFECTS = {
        "spring": {
            "temp_offset": 5.0,
            "rain_offset": 20.0,
            "humidity_offset": 0.1,
            "par_offset": 50.0,
        },
        "summer": {
            "temp_offset": 15.0,
            "rain_offset": -10.0,
            "humidity_offset": -0.05,
            "par_offset": 100.0,
        },
        "autumn": {
            "temp_offset": 0.0,
            "rain_offset": 10.0,
            "humidity_offset": 0.05,
            "par_offset": 0.0,
        },
        "winter": {
            "temp_offset": -10.0,
            "rain_offset": 0.0,
            "humidity_offset": -0.1,
            "par_offset": -50.0,
        },
    }

    def __init__(self, northern_hemisphere: bool = True):
        super().__init__()
        self.northern_hemisphere = northern_hemisphere

    def update(self, world: World, dt: float) -> None:
        """更新季节并应用环境影响"""
        time_comp = world.get_world_component(TimeComponent)
        if time_comp is None:
            return

        # 计算当前季节（基于天文参数）
        day_of_year = getattr(time_comp, 'day_of_year', 0)
        
        # 如果有天体数据，使用天文计算
        astronomical_day = self._calculate_astronomical_day(world, day_of_year)
        
        current_season = self._calculate_season(astronomical_day)

        # 应用季节效果到所有环境实体
        for entity, (env,) in world.get_components(EnvironmentComponent):
            if env is None:
                continue
            self._apply_season_effects(env, current_season, astronomical_day)

    def _calculate_season(self, day_of_year: int) -> str:
        """根据一年中的天数计算当前季节"""
        if day_of_year < self.SEASON_START_DAYS["spring"]:
            return "winter"
        elif day_of_year < self.SEASON_START_DAYS["summer"]:
            return "spring"
        elif day_of_year < self.SEASON_START_DAYS["autumn"]:
            return "summer"
        elif day_of_year < self.SEASON_START_DAYS["winter"]:
            return "autumn"
        else:
            return "winter"

    def _apply_season_effects(self, env: EnvironmentComponent, season: str, day_of_year: int) -> None:
        """应用季节对环境参数的影响"""
        effects = self.SEASON_EFFECTS.get(season, {})
        if not effects:
            return

        # 计算过渡因子（季节开始时效果最强，季节中间稳定）
        transition_factor = self._calculate_transition_factor(season, day_of_year)

        # 应用温度偏移
        temp_offset = effects.get("temp_offset", 0.0)
        env.air_temperature += temp_offset * transition_factor * 0.01
        env.soil_temperature += temp_offset * transition_factor * 0.005

        # 应用降雨偏移
        rain_offset = effects.get("rain_offset", 0.0)
        env.rainfall += rain_offset * transition_factor * 0.01
        env.rainfall = max(0.0, env.rainfall)

        # 应用湿度偏移
        humidity_offset = effects.get("humidity_offset", 0.0)
        env.air_humidity += humidity_offset * transition_factor * 0.01
        env.air_humidity = max(0.0, min(1.0, env.air_humidity))

        # 应用光照偏移
        par_offset = effects.get("par_offset", 0.0)
        env.par += par_offset * transition_factor * 0.01
        env.par = max(0.0, env.par)

    def _calculate_transition_factor(self, season: str, day_of_year: int) -> float:
        """计算季节过渡因子（0.0-1.0）"""
        season_start = self.SEASON_START_DAYS.get(season, 0)
        season_length = 90  # 约90天一个季节

        # 当前季节已过去的天数
        days_into_season = day_of_year - season_start
        if days_into_season < 0:
            days_into_season += 365

        # 过渡期间：季节开始和结束时效果渐变
        if days_into_season < 15:
            # 季节开始，逐渐增强
            return days_into_season / 15.0
        elif days_into_season > season_length - 15:
            # 季节结束，逐渐减弱
            return (season_length - days_into_season) / 15.0
        else:
            # 季节中期，效果稳定
            return 1.0

    def _calculate_astronomical_day(self, world: World, day_of_year: int) -> int:
        """
        根据天文参数计算有效天数
        考虑地球轨道偏心率（近日点/远日点）
        """
        # 查找天体（太阳）
        for entity, (body,) in world.get_components(CelestialBodyComponent):
            if body is None or body.body_name != "sun":
                continue
            
            # 轨道偏心率影响：近日点（约1月3日）接收更多辐射
            # 远日点（约7月4日）接收更少辐射
            # 简化为：根据当前距离调整有效天数
            distance_factor = TidalSystem.current_distance(body) / body.distance
            
            # 距离越近，季节推进越快（北半球冬季更短）
            if distance_factor < 1.0:
                # 近日点附近，季节变化加速
                return int(day_of_year * (1.0 + (1.0 - distance_factor) * 0.03))
            else:
                # 远日点附近，季节变化减速
                return int(day_of_year * (1.0 - (distance_factor - 1.0) * 0.03))
        
        # 没有太阳数据，使用原始天数
        return day_of_year

    def get_season_info(self, day_of_year: int) -> Dict:
        """获取指定日期的季节信息"""
        season = self._calculate_season(day_of_year)
        effects = self.SEASON_EFFECTS.get(season, {})
        return {
            "season": season,
            "day_of_year": day_of_year,
            "effects": effects,
            "is_northern": self.northern_hemisphere,
        }