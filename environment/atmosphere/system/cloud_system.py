#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
云层系统 [适配版] — 已移除对旧版 WeatherComponent 离散状态的操作

【设计变更】
- 不再写 WeatherComponent.sky / precipitation_type（这些由 PhysicalWeatherSystem 的物理量推导）
- 仅维护 AtmosphereComponent 的 cloud_density / cloud_cover
- AtmosphereComponent.cloud_density 作为大气微观物理的独立层

【物理原理】
云的形成需要：
1. 水汽达到饱和状态（相对湿度 > 100%）
2. 凝结核（气溶胶）作为结晶核心
3. 足够的空气上升运动/对流
"""

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


class CloudSystem(System):
    """
    云层系统（大气微观物理层）

    维护 AtmosphereComponent.cloud_density / cloud_cover，
    不再写入任何天气离散状态枚举。
    宏观天气的云量降水由 PhysicalWeatherSystem 独立驱动。
    """

    # === 物理常量 ===
    REFRACTIVE_INDEX_CLOUD = 1.01   # 典型云层折射率

    # 降水触发阈值（仅用于大气层诊断，不写入天气状态）
    CLOUD_DENSITY_RAIN_THRESHOLD = 1.0
    CLOUD_DENSITY_SNOW_THRESHOLD = 1.2

    def _calculate_cloud_growth(self, atm: AtmosphereComponent) -> float:
        """
        计算云的增长速率

        Args:
            atm: 大气组件

        Returns:
            云量的增长率（0-1/小时）
        """
        # 相对湿度越接近饱和，增长越快
        humidity_factor = abs(atm.humidity - 100.0) / 5 if atm.humidity else 0

        # 气溶胶作为凝结核浓度
        aerosol_factor = atm.aerosol * 2 if atm.aerosol > 0 else 0

        # 对流强度促进云形成
        convection_factor = atm.convection_strength * 0.5 if atm.convection_strength > 0 else 0

        return humidity_factor + aerosol_factor + convection_factor

    def _estimate_precipitation(self, atm: AtmosphereComponent) -> dict:
        """
        估算降水状态（仅诊断，不再写入天气组件）

        Args:
            atm: 大气组件

        Returns:
            诊断用的降水信息字典
        """
        cloud_density = atm.cloud_density or 0
        convection = atm.convection_strength or 0
        temp = atm.temperature or 0
        altitude = atm.altitude or 0

        result = {
            'precipitation_type': 'none',
            'precipitation_intensity': 'none',
        }

        if cloud_density > self.CLOUD_DENSITY_RAIN_THRESHOLD:
            precipitation_type = 'none'
            intensity = 'light'

            if temp < 0:
                precipitation_type = 'snow'
            elif temp < 5:
                precipitation_type = 'sleet'
            else:
                precipitation_type = 'rain'

            if convection > 0.3 and cloud_density > self.CLOUD_DENSITY_SNOW_THRESHOLD:
                intensity = 'heavy'
            elif cloud_density > self.CLOUD_DENSITY_RAIN_THRESHOLD * 1.5:
                intensity = 'moderate'

            result['precipitation_type'] = precipitation_type
            result['precipitation_intensity'] = intensity

        return result

    def update(self, world: World, delta_hours: float):

        for entity, [atm] in world.get_components(AtmosphereComponent):
            atm: AtmosphereComponent

            # === 1. 饱和判断 ===
            if not self._is_saturated(atm):
                continue

            # === 2. 云的增长 ===
            growth_rate = self._calculate_cloud_growth(atm) * delta_hours
            current_density = atm.cloud_density or 0

            new_density = min(1.5, max(0, current_density + growth_rate))
            atm.cloud_density = round(new_density, 4)
            atm.cloud_cover = atm.cloud_density

            # === 3. 降水诊断（仅日志/调试用途） ===
            precip_info = self._estimate_precipitation(atm)
            if precip_info['precipitation_type'] != 'none':
                # 可在此触发日志或事件
                pass

    def _is_saturated(self, atm: AtmosphereComponent) -> bool:
        """判断大气是否达到过饱和状态"""
        if not atm or not hasattr(atm, 'humidity'):
            return False
        humidity = atm.humidity or 0
        return humidity > 90.0
