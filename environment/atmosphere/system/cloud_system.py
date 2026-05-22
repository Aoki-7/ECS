#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
云层系统 [v2.0] — 基于 PhysicalWeather 计算云层参数

【物理原理】
云的形成需要：
1. 水汽达到饱和状态（相对湿度 > 90%）
2. 凝结核（气溶胶）
3. 足够的空气上升运动/对流

【数据流】
PhysicalWeatherComponent (cloud_cover, relative_humidity, temperature)
    → CloudSystem
    → AtmosphereComponent (cloud_cover, cloud_density)
"""

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)


class CloudSystem(System):
    """
    云层系统

    从 PhysicalWeatherComponent 读取云量与湿度，
    计算云密度并同步到 AtmosphereComponent。
    """

    # 云密度阈值
    CLOUD_DENSITY_RAIN_THRESHOLD = 1.0
    CLOUD_DENSITY_SNOW_THRESHOLD = 1.2

    def _calculate_cloud_growth(self, rh: float, temp: float, aerosol: float) -> float:
        """
        计算云的增长速率

        Args:
            rh: 相对湿度 [0~1]
            temp: 温度 (°C)
            aerosol: 气溶胶浓度

        Returns:
            云密度增长率（0-1/小时）
        """
        # 相对湿度越接近饱和，增长越快
        humidity_factor = max(0, (rh - 0.8) / 0.2) if rh > 0.8 else 0

        # 气溶胶作为凝结核
        aerosol_factor = aerosol * 2 if aerosol > 0 else 0

        # 低温促进冰晶云形成
        temp_factor = 0.1 if temp < 0 else 0

        return humidity_factor * 0.5 + aerosol_factor + temp_factor

    def _estimate_cloud_density(self, cloud_cover: float, rh: float, temp: float) -> float:
        """
        估算云密度（0-1.5）

        云密度 = 云覆盖率 × 厚度因子
        厚度受湿度和温度影响。
        """
        if cloud_cover <= 0:
            return 0.0

        # 基础密度与云覆盖率成正比
        base_density = cloud_cover

        # 高湿度增加云厚
        humidity_boost = max(0, (rh - 0.7) / 0.3) * 0.3 if rh > 0.7 else 0

        # 低温增加云厚（冰晶云更厚）
        temp_boost = 0.2 if temp < 5 else 0

        return min(1.5, base_density + humidity_boost + temp_boost)

    def update(self, world: World, delta_hours: float):
        """
        云层系统更新

        数据流：PhysicalWeatherComponent → AtmosphereComponent
        """
        atm = world._world_entity.get_component(AtmosphereComponent)
        weather = world._world_entity.get_component(PhysicalWeatherComponent)

        if atm is None or weather is None:
            return

        cloud_cover = weather.cloud_cover
        rh = weather.relative_humidity
        temp = weather.temperature

        # 同步云覆盖率
        atm.cloud_cover = cloud_cover

        # 计算云密度
        cloud_density = self._estimate_cloud_density(cloud_cover, rh, temp)
        atm.cloud_density = round(cloud_density, 4)
