#!/usr/bin/env python3
"""
温度传导系统 v4.16.0
实现真实的温度传导过程：太阳辐射加热→地表温度变化→土壤分层传导→热量平衡
"""

import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from environment.environment_component import EnvironmentComponent
from environment.physics_weather.components.temperature_component import TemperatureComponent
from environment.soil.components.soil_component import SoilComponent
from plant.components.plant_component import PlantComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class TemperatureConductionSystem(System):
    """
    温度传导系统
    处理全局与网格级别的温度动态变化与传导
    """

    tick_interval = 5  # 每5tick执行一次
    priority = 90  # 比水循环系统更早运行，温度影响蒸发等过程

    # 物理常数
    STEFAN_BOLTZMANN = 5.67e-8  # 斯特藩-玻尔兹曼常数 W/(m²·K⁴)
    AIR_HEAT_TRANSFER_COEFF = 10.0  # 空气与地表热交换系数 W/(m²·K)
    SOIL_THERMAL_DIFFUSIVITY = 1e-6  # 土壤热扩散率 m²/s（典型值）

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        if not world_env:
            return
        
        air_temperature = world_env.temperature  # 气温 °C
        solar_altitude = world_env.sun_altitude if hasattr(world_env, 'sun_altitude') else 0.5  # 太阳高度 0-1，正午1，午夜0
        solar_constant = 1361.0  # 太阳常数 W/m²
        
        # 计算太阳辐射强度（W/m²）
        solar_radiation = solar_constant * max(0.0, solar_altitude) * 0.7  # 0.7是大气透射率
        
        # 遍历所有温度网格
        for entity, temp_comp, soil, space in world.query(
            TemperatureComponent,
            SoilComponent,
            SpaceComponent
        ):
            # 1. 计算地表净辐射
            net_radiation = self._calculate_net_radiation(
                solar_radiation,
                temp_comp.albedo,
                temp_comp.surface_temperature,
                air_temperature
            )
            
            # 2. 计算显热交换（与空气的热交换）
            sensible_heat = self.AIR_HEAT_TRANSFER_COEFF * (air_temperature - temp_comp.surface_temperature)
            
            # 3. 计算潜热交换（蒸发/凝结消耗/释放热量）
            latent_heat = 0.0
            if soil.moisture > 0.05:
                # 蒸发消耗热量，简化为与湿度和温度正相关
                evaporation_rate = 0.001 * soil.moisture * max(0.0, temp_comp.surface_temperature - 5.0)
                latent_heat = -2.45e6 * evaporation_rate  # 蒸发潜热 2.45 MJ/kg
            
            # 4. 地表能量平衡：净辐射 = 显热 + 潜热 + 土壤热通量
            soil_heat_flux = net_radiation - sensible_heat - latent_heat
            temp_comp.surface_heat_flux = soil_heat_flux
            
            # 5. 更新地表温度
            # 地表热容量（0-10cm层）
            surface_heat_capacity = soil.heat_capacity if hasattr(soil, 'heat_capacity') else 2.0e6
            surface_layer_thickness = 0.1  # 10cm
            temp_change = (soil_heat_flux * dt) / (surface_heat_capacity * surface_layer_thickness)
            new_surface_temp = temp_comp.temperatures[0] + temp_change
            
            # 6. 土壤层间热传导
            new_temps = self._calculate_layer_conduction(
                temp_comp.temperatures,
                temp_comp.thermal_conductivity,
                surface_heat_capacity,
                dt
            )
            new_temps[0] = new_surface_temp  # 应用地表温度变化
            
            # 7. 更新温度组件
            temp_comp.update_temperatures(new_temps)
            
            # 8. 更新全局气温（所有网格的平均地表温度加权平均）
            # 暂时简化，后续可加入大气对流

    def _calculate_net_radiation(self, solar_radiation: float, albedo: float, surface_temp: float, air_temp: float) -> float:
        """计算地表净辐射通量（W/m²）"""
        # 吸收的短波辐射
        absorbed_shortwave = solar_radiation * (1 - albedo)
        
        # 长波辐射收支：地面向上辐射 - 大气向下辐射（大气逆辐射）
        surface_longwave = self.STEFAN_BOLTZMANN * (surface_temp + 273.15)**4
        # 大气逆辐射简化：气温的黑体辐射×0.8（大气发射率）
        atmospheric_longwave = 0.8 * self.STEFAN_BOLTZMANN * (air_temp + 273.15)**4
        
        net_longwave = atmospheric_longwave - surface_longwave
        return absorbed_shortwave + net_longwave

    def _calculate_layer_conduction(self, temps: List[float], conductivity: float, heat_capacity: float, dt: float) -> List[float]:
        """
        计算土壤层之间的热传导
        使用显式有限差分法
        """
        n = len(temps)
        new_temps = temps.copy()
        # 层厚度（m）
        layer_thickness = [0.1, 0.4, 0.5, 1.0, 1.0]  # 0-10cm, 10-50cm, 50-100cm, 100-200cm, 200+cm
        
        for i in range(1, n-1):
            # 上层温度
            temp_above = temps[i-1]
            # 下层温度
            temp_below = temps[i+1]
            # 当前层温度
            current_temp = temps[i]
            
            # 计算上下层热流
            flux_above = conductivity * (temp_above - current_temp) / layer_thickness[i-1]
            flux_below = conductivity * (current_temp - temp_below) / layer_thickness[i]
            
            # 温度变化率
            temp_change = (flux_above - flux_below) * dt / (heat_capacity * layer_thickness[i])
            new_temps[i] += temp_change
        
        # 最底层温度变化很小，近似不变
        return new_temps
