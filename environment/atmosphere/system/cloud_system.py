#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
云层系统 [扩展版] — 与 WeatherComponent 的降水联动完善

【物理原理】
云的形成需要：
1. 水汽达到饱和状态（相对湿度 > 100%）
2. 凝结核（气溶胶）作为结晶核心
3. 足够的空气上升运动/对流

【降水触发条件】
- 云量超过阈值
- 水滴/冰晶增长到足够大
- 重力 > 上升气流支撑力

【简化模型】
- 相对湿度接近或超过 100% → 过饱和，触发凝结
- 云量 + 对流强度决定降水概率
"""


from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.weather.components.weather_component import WeatherComponent


class CloudSystem(System):
    """
    云层系统
    
    【扩展功能】
    - 基于相对湿度和凝结核计算云量
    - 云量影响天气系统的降水和光照（联动 WeatherComponent）
    - 支持不同类型云上界高度估算
    
    【与 WeatherComponent 的联动】
    - 云密度 → 触发降水类型判断
    - 高海拔 + 低温 + 云厚 → 降雪
    - 中低海拔 + 高温 → 降雨
    """
    
    # === 物理常量 ===
    REFRACTIVE_INDEX_CLOUD = 1.01   # 典型云层折射率
    
    # 降水触发阈值
    CLOUD_DENSITY_RAIN_THRESHOLD = 1.0      # 云密度达到此值可能降雨
    CLOUD_DENSITY_SNOW_THRESHOLD = 1.2      # 更高云密度更易降雪（伴随强对流）

    def _calculate_cloud_growth(self, atm: AtmosphereComponent, weather: WeatherComponent) -> float:
        """
        计算云的增长速率
        
        Args:
            atm: 大气组件
            weather: 天气组件（提供降水状态信息）
        
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
    
    def _estimate_precipitation(self, atm: AtmosphereComponent, weather: WeatherComponent) -> dict:
        """
        估算降水状态（联动 WeatherComponent）
        
        Args:
            atm: 大气组件
            weather: 天气组件
        
        Returns:
            包含 precipitation_type, precipitation_intensity 的字典
        """
        cloud_density = atm.cloud_density or 0
        convection = atm.convection_strength or 0
        temp = atm.temperature or 0
        altitude = atm.altitude or 0
        
        result = {
            'precipitation_type': 'none',
            'precipitation_intensity': 'none',
        }
        
        # 云密度超过阈值，检查降水触发条件
        if cloud_density > self.CLOUD_DENSITY_RAIN_THRESHOLD:
            precipitation_type = 'none'
            intensity = 'light'
            
            # 温度决定类型：低温 → 雪，高温 → 雨
            if temp < 0:
                precipitation_type = 'snow'
            elif temp < 5:
                precipitation_type = 'sleet'
            else:
                precipitation_type = 'rain'
            
            # 高云密度 + 强对流 → 强度升级
            if convection > 0.3 and cloud_density > self.CLOUD_DENSITY_SNOW_THRESHOLD:
                intensity = 'heavy'
            elif cloud_density > self.CLOUD_DENSITY_RAIN_THRESHOLD * 1.5:
                intensity = 'moderate'
            
            result['precipitation_type'] = precipitation_type
            result['precupitation_intensity'] = intensity
            
        return result
    
    def update(self, world: World, delta_hours: float):
        """
        云层系统更新
        
        【计算顺序】
        1. 检查饱和状态（与 WeatherComponent 同步）
        2. 计算云的增长
        3. 更新云量和上界高度
        4. 触发降水判断 → 写入 WeatherComponent（联动逻辑）
        
        【数据流】
        CloudSystem ←→ AtmosphereComponent (双向) ←→ WeatherComponent
        """
        
        for entity, [atm, weather] in world.get_components(AtmosphereComponent, WeatherComponent):
            atm: AtmosphereComponent
            weather: WeatherComponent
            
            # === 1. 饱和判断（检查湿度是否接近或超过 100%）===
            if not self._is_saturated(atm):
                continue
            
            # === 2. 云的增长（基于湿度、气溶胶、对流）===
            growth_rate = self._calculate_cloud_growth(atm, weather) * delta_hours
            current_density = atm.cloud_density or 0
            
            new_density = min(1.5, max(0, current_density + growth_rate))
            atm.cloud_density = round(new_density, 4)
            atm.cloud_cover = atm.cloud_density
            
            # === 3. 更新云量到 WeatherComponent ===
            if weather:
                weather.sky = self._cloud_to_sky_state(atm.cloud_density or 0)
            
            # === 4. 估算云的上界高度 ===
            cloud_top = self._estimate_cloud_Top(atm, weather)
            if cloud_top and not hasattr(atm, '_cloud_Top'):
                atm._cloud_Top = cloud_top
            
            # === 5. 降水判断 → 写入 WeatherComponent ===
            precip_info = self._estimate_precipitation(atm, weather)
            if weather:
                weather.precipitation_type = precip_info['precipitation_type']
                weather.precipitation_intensity = precip_info['precipitation_intensity']

    def _is_saturated(self, atm: AtmosphereComponent) -> bool:
        """
        判断大气是否达到过饱和状态（触发云形成的条件）
        
        Args:
            atm: 大气组件
        
        Returns:
            bool: 是否过饱和（相对湿度接近 100%）
        """
        if not atm or not hasattr(atm, 'humidity'):
            return False
        
        # 相对湿度 > 90% 视为可能饱和，> 100% 为过饱和
        humidity = atm.humidity or 0
        return humidity > 90.0

    def _cloud_to_sky_state(self, cloud_density: float) -> str:
        """
        将云密度转换为天空状态
        
        Args:
            cloud_density: 云密度（0-1）
        
        Returns:
            SkyState 名称字符串
        """
        if cloud_density < 0.2:
            return "clear"
        elif cloud_density < 0.5:
            return "partly_cloudy"
        elif cloud_density < 0.9:
            return "cloudy"
        else:
            return "overcast"

    def _estimate_cloud_Top(self, atm: AtmosphereComponent, weather: WeatherComponent) -> float | None:
        """
        估算云的上界高度（简化模型）
        
        Args:
            atm: 大气组件
            weather: 天气组件
        
        Returns:
            float: 云顶高度（米），或 None
        """
        if not hasattr(atm, '_cloud_Top'):
            return None
        
        # 简化模型：云顶高度 = 当前海拔 + 云量比例 * 标准对流层厚度
        base_altitude = atm.altitude or 0
        cloud_fraction = atm.cloud_density or 0
        
        max_top = self._get_base_altitude() + 8000 * cloud_fraction
        
        return min(max(atm._cloud_Top, base_altitude), max_top)

    def on_add(self, world: World):
        """系统激活时确保 WeatherComponent 存在"""
        super().on_add(world)
        if not world.get_component_by_type(WeatherComponent):
            weather = WeatherComponent()
            world._world_entity.add_component(weather)