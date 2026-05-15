#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
风场系统 [扩展版]

【物理原理】
风速主要来源于气压梯度力，同时受地转偏向力、摩擦力等影响。简化模型：

1. 气压梯度力驱动风
   - 气压差越大，风速越快
   - 风向从高压指向低压（北半球逆时针旋转）

2. 温度差异产生热风
   - 暖空气上升，冷空气下沉形成环流
   - 海陆温差产生海陆风

3. 地球自转影响风向（科里奥利力）
"""


from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


class WindSystem(System):
    """
    风场系统
    
    【扩展功能】
    - 基于气压梯度计算风速
    - 支持温度差异产生的热对流风
    - 科里奥利力影响风向（北半球向右偏转）
    """
    
    # 物理常量
    GROUND_TEMPERATURE = 15.0  # °C，用于计算温差
    
    @staticmethod
    def calculate_pressure_gradient_force(pressure_change: float, distance: int) -> float:
        """
        计算气压梯度力
        
        Args:
            pressure_change: 气压差 (hPa)
            distance: 距离 (km)
        
        Returns:
            气压梯度力（简化模型）: N/m²
        """
        # 简化公式：气压每单位距离的变化
        grad = pressure_change / distance if distance > 0 else 0
        return grad

    @staticmethod
    def calculate_coriolis_deflection(wind_speed: float, latitude: float) -> float:
        """
        计算科里奥利力导致的偏转（北半球向右）
        
        Args:
            wind_speed: 风速 (m/s)
            latitude: 纬度
        
        Returns:
            偏转角度（度）
        """
        # 科里奥利参数 f = 2Ωsin(φ)，简化模型
        f = 0.0001 * 2 * wind_speed * abs(latitude)
        return f

    def update(self, world: World, delta_hours: float):
        """
        风场系统更新
        
        【计算顺序】
        1. 气压梯度 → 基础风速 + 风向
        2. 温度差异 → 补充热风
        3. 科里奥利力 → 偏转风向
        """
        
        for entity, [atm] in world.get_components(AtmosphereComponent):
            atm: AtmosphereComponent
            
            # === 1. 气压梯度驱动的风 ===
            pressure_diff = atm.pressure - 1013.25 if atm.pressure else 0
            pressure_wind_speed = abs(pressure_diff) * 0.4  # hPa → m/s，简化系数
            
            # === 2. 温度差异产生的热对流风 ===
            temp_diff = atm.temperature - self.GROUND_TEMPERATURE
            thermal_wind_speed = max(0, temp_diff) * 0.15 if temp_diff > 0 else 0
            
            # === 3. 风速合成 ===
            total_wind_speed = min(25, pressure_wind_speed + thermal_wind_speed)
            
            # === 4. 风向计算 ===
            # 基础风向：气压最低方向（简化为从高压向低压）
            base_direction = atm.wind_direction or random.uniform(0, 360)
            
            # 受热对流影响，风向会偏向低压中心
            thermal_deflection = thermal_wind_speed * 0.5 if thermal_wind_speed > 0 else 0
            
            # === 5. 科里奥利偏转（北半球简化） ===
            coriolis_deflection = self.calculate_coriolis_deflection(
                total_wind_speed, 30  # 假设纬度 30°
            )
            
            atm.wind_speed = round(total_wind_speed, 2)
            atm.wind_direction = (base_direction + thermal_deflection + coriolis_deflection) % 360
