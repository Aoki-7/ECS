#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:solar_position_system.py
@说明:太阳位置系统 — 使用完整球面天文学模型
      支持昼夜区分、时角计算、精确太阳高度角和方位角
@时间:2026/05/17
@作者:Sherry
@版本:2.0
'''

import math

from core.system import System
from core.world import World

from environment.light_field.components.solar_position_component import (
    SolarPositionComponent,
)


class SolarPositionSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    太阳位置系统

    输入：
        Time (world.get_time): 当前时间（含 day_of_year, hour）
        SolarPositionComponent.latitude: 纬度（可配置）
    输出：
        SolarPositionComponent:
            - elevation:  太阳高度角 (°, 0=地平线, 90=天顶)
            - azimuth:    太阳方位角 (°, 0=北, 顺时针)
            - day_length: 昼长 (h)
            - is_night:   是否夜间

    物理模型：
        使用完整球面天文学公式，考虑：
        - 地球轴倾角 (23.44°)
        - 时角 (hour angle)：使太阳高度随一天中的小时变化
        - 纬度依赖
    """

    # 地球轴倾角 (度)
    AXIAL_TILT = 23.44

    def update(self, world: World, delta_hours: float):
        time = world.get_time()
        if time is None:
            return
        # 防御：使用 world.get_world_component 替代 entity.get_component
        solar_pos = world.get_world_component(SolarPositionComponent)

        if solar_pos is None:
            return

        # ── 从时间系统获取 ──
        day_of_year = time.day_of_year
        hour = time.hour
        latitude = getattr(solar_pos, 'latitude', 35.0)

        # ── 1. 太阳赤纬角 (declination) ──
        # 春分 (day 81) 为 0°，夏至 (day 173) 为 23.44°，冬至 (day 355) 为 -23.44°
        declination = self.AXIAL_TILT * math.sin(
            math.radians((360.0 / 365.0) * (day_of_year - 81))
        )

        # ── 2. 时角 (hour angle) ──
        # 正午 (12:00) 时角 = 0°，每小时 15°
        # 上午为正，下午为负（传统天文学定义）
        hour_angle = (hour - 12.0) * 15.0  # 度

        # ── 3. 太阳高度角 (solar elevation) ──
        # sin(α) = sin(φ)·sin(δ) + cos(φ)·cos(δ)·cos(h)
        # α = 高度角, φ = 纬度, δ = 赤纬, h = 时角
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        ha_rad = math.radians(hour_angle)

        sin_elev = (
            math.sin(lat_rad) * math.sin(dec_rad)
            + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
        )
        elevation = math.degrees(math.asin(max(-1.0, min(1.0, sin_elev))))

        # ── 4. 判断昼夜 ──
        # 高度角 > 0° → 白天，≤ 0° → 夜间
        # 民用晨昏蒙影：-6° < 高度角 ≤ 0° 为微光时段
        is_night = elevation <= 0.0

        # ── 5. 太阳方位角 (azimuth) ──
        # cos(A) = (sin(δ) - sin(φ)·sin(α)) / (cos(φ)·cos(α))
        # A = 方位角，从北顺时针，0° = 北
        if elevation > 0.0:
            elev_rad = math.radians(elevation)
            cos_az = (
                math.sin(dec_rad) - math.sin(lat_rad) * math.sin(elev_rad)
            ) / (math.cos(lat_rad) * math.cos(elev_rad))
            cos_az = max(-1.0, min(1.0, cos_az))
            azimuth = math.degrees(math.acos(cos_az))

            # 上午 (hour < 12) 太阳在东，下午在西方
            if hour_angle > 0:  # 上午（时角 > 0）
                azimuth = 360.0 - azimuth
        else:
            # 夜间无有效方位角，设为 0
            azimuth = 0.0

        # ── 6. 昼长 (day length) ──
        # cos(h_sunset) = -tan(φ)·tan(δ)
        cos_hour_sunset = -math.tan(lat_rad) * math.tan(dec_rad)
        if cos_hour_sunset > 1.0:
            day_length = 0.0    # 极夜
        elif cos_hour_sunset < -1.0:
            day_length = 24.0   # 极昼
        else:
            hour_sunset = math.degrees(math.acos(cos_hour_sunset))
            day_length = 2.0 * hour_sunset / 15.0  # 时角→小时

        # ── 写入组件 ──
        solar_pos.elevation = max(-90.0, min(90.0, elevation))
        solar_pos.azimuth = max(0.0, min(360.0, azimuth))
        solar_pos.day_length = day_length
        # is_night 由 elevation 自动推导，无需写入

    # ═══════════════════════════════════════════
    # 辅助方法（可供外部调用）
    # ═══════════════════════════════════════════

    @staticmethod
    def compute_solar_elevation(
        latitude: float, day_of_year: int, hour: float
    ) -> float:
        """
        静态方法：计算指定位置/时间的太阳高度角。
        便于外部物理系统独立调用而无需访问 ECS 组件。
        """
        declination = 23.44 * math.sin(
            math.radians((360.0 / 365.0) * (day_of_year - 81))
        )
        hour_angle = (hour - 12.0) * 15.0
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        ha_rad = math.radians(hour_angle)
        sin_elev = (
            math.sin(lat_rad) * math.sin(dec_rad)
            + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
        )
        return math.degrees(math.asin(max(-1.0, min(1.0, sin_elev))))

    @staticmethod
    def compute_day_length(latitude: float, day_of_year: int) -> float:
        """静态方法：计算昼长 (h)"""
        dec_rad = math.radians(
            23.44 * math.sin(math.radians((360.0 / 365.0) * (day_of_year - 81)))
        )
        lat_rad = math.radians(latitude)
        cos_h = -math.tan(lat_rad) * math.tan(dec_rad)
        if cos_h > 1.0:
            return 0.0
        elif cos_h < -1.0:
            return 24.0
        return 2.0 * math.degrees(math.acos(cos_h)) / 15.0