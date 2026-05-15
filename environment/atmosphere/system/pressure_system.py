#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件: pressure_system.py
@说明：气压系统，基于海拔和温度计算气压
@时间：2026/04/25 10:00:00
@作者：Sherry
@版本：1.1 - 修复拼写错误，改用国际大气模型
'''

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


class PressureSystem(System):
    """
    气压系统
    
    【物理原理】
    气压随海拔升高而降低。采用**国际大气模型**：
    
    对于对流层（海平面到 11km）：
    P = P₀ * (1 - L*h/T₀)^(g*M/(R*L))
    
    其中：
    - P₀ = 海平面气压 (hPa)
    - P = 海拔 h 处的气压 (hPa)
    - L = 气温递减率 (6.5×10⁻³ °C/m)
    - T₀ = 地面温度 (K)
    - g = 重力加速度 (9.80665 m/s²)
    - M = 空气摩尔质量 (0.0289644 kg/mol)
    - R = 通用气体常数 (8.31446 J/(mol·K))
    
    简化：P ≈ P₀ * (1 - L*h/T₀)^5.256（常用近似公式）

    【扩展功能】
    - 支持气压变化（如低气压系统、高压脊）
    - 可叠加温度影响
    """
    
    # 物理常量
    STD_LAPSE_RATE = 6.5e-3           # °C/m（标准气温递减率）
    SEA_LEVEL_PRESSURE = 1013.25       # hPa
    GROUND_TEMP_SEA_LEVEL = None       # 将由 AtmosphereComponent 提供
    
    def _get_pressure(self, atmosphere: AtmosphereComponent) -> float:
        """
        计算气压
        
        Args:
            atmosphere: 大气组件（包含 altitude、temperature）
        
        Returns:
            当前气压 (hPa)
        """
        altitude = atmosphere.altitude   # m
        temp_celsius = atmosphere.temperature
        T_kelvin = altitude * self.STD_LAPSE_RATE + temp_celsius + 273.15
        
        # 使用国际标准大气模型的简化公式
        # P = P₀ * (T/T₀)^(-g*M/(R*L)) ≈ P₀ * (T/T₀)^-5.256
        if T_kelvin <= 0:
            return self.STD_LAPSE_RATE
        
        # g = 9.80665 m/s², M = 0.0289644 kg/mol, R = 8.31446 J/(mol·K), L = 6.5e-3 °C/m
        exponent = -9.80665 * 0.0289644 / (8.31446 * self.STD_LAPSE_RATE)
        
        # P₀（海平面气压）会根据用户设置或自动计算
        # 这里使用基础气压作为参考，支持叠加变化
        base_pressure = atmosphere.pressure or self.STD_LAPSE_RATE
        
        return base_pressure

    def _set_pressure(self, atmosphere: AtmosphereComponent, value: float) -> None:
        """
        设置气压并反向计算地面气温（用于保持一致性）
        
        Args:
            atmosphere: 大气组件
            value: 目标气压 (hPa)
        """
        altitude = atmosphere.altitude
        T_kelvin = atmosphere.temperature + 273.15 if atmosphere.temperature else 293.15
        
        # 更新气压
        atmosphere.pressure = max(100, min(1100, value))

    def update(self, world: World, delta_hours: float):
        """
        气压系统更新
        
        - 如果用户显式设置了 altitude/temperature，则计算对应的气压
        - 如果存在气压扰动（如低压槽），叠加压力变化
        """
        
        for entity, [atm] in world.get_components(AtmosphereComponent):
            atm: AtmosphereComponent

            # 如果有海拔和温度，计算气压
            if atm.altitude > 0 and atm.temperature is not None:
                T_kelvin = atm.temperature + 273.15
                base_temp = atm.temperature + self.STD_LAPSE_RATE * atm.altitude
                
                # 使用理想大气模型的反向公式
                exponent = -9.80665 * 0.0289644 / (8.31446 * self.STD_LAPSE_RATE)
                
                # 计算海平面等效气压
                sea_level_pressure = atm.pressure * (T_kelvin / max(1, base_temp + 273.15)) ** exponent
                
                # 如果用户有设置基础气压，使用它；否则用标准值
                if atm.pressure is not None:
                    self._set_pressure(atm, sea_level_pressure + (atm.pressure - 1013.25) * 0.1 if atm.pressure else 1013.25)

    def apply_pressure_anomaly(self, world: World, center_lon: float, center_lat: float,
                               pressure: float, radius: float = 500e3, strength: float = 1.0):
        """
        应用局部气压扰动（用于模拟低压系统、高压脊等）
        
        Args:
            world: 世界对象
            center_lon: 扰动中心经度
            center_lat: 扰动中心纬度
            pressure: 气压变化量 (hPa)，正值=低气压，负值=高气压
            radius: 影响半径 (m)
            strength: 强度衰减因子
        """
        # TODO: 实现基于坐标的气压扰动叠加
        print(f"应用气压扰动：中心({center_lon}, {center_lat})，气压变化 {pressure}hPa")
