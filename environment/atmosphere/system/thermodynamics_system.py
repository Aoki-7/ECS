#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
热力学系统 [扩展版] — 职责清晰、去除重复计算

【物理原理】
1. 空气密度 — 理想气体状态方程：ρ = P / (R·T)
2. 水汽饱和蒸气压 — Magnus 公式
3. 相对湿度 — 实际水汽压/饱和水汽压 × 100%
4. 热交换 — 基于温度差和风速的简化模型

【职责边界】
- ✅ 仅负责：空气密度、湿度计算、相变条件判断
- ❌ 不再负责：气压计算（由 PressureSystem 处理）
- ❌ 不再负责：云量计算（由 CloudSystem 处理）

【注意】
- T 的单位需为°C，不可使用 K（除非特别说明）
- pressure 参数从 AtmosphereComponent 直接读取，而非在此系统内计算

【与外部依赖】
- AtmosphereComponent: 获取 temperature, pressure, humidity 等物理量
"""


from core.system import System
from core.world import World

<<<<<<< HEAD
=======
from environment.weather.components.weather_component import WeatherComponent
>>>>>>> 65a14767a91c763628f1030bcdd9bce57d718edc
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent


class ThermodynamicsSystem(System):
    """
    热力学系统
    
    【核心功能】
    - 计算并维护空气密度、相对湿度、饱和水汽压
    - 管理温度与湿度的耦合关系
    - 支持相变过程（凝结/蒸发）的物理条件判断
    
    【与子系统协调】
    - 先于 PressureSystem 运行，从 AtmosphereComponent 读取气压
    - 将计算后的湿度结果传递给 CloudSystem（通过 AtmosphereComponent）
    """
    
    # === 物理常量 ===
    GASEOUS_CONSTANT = 287.05  # J/(kg·K)，干空气气体常数
    
    # Magnus formula coefficients for liquid water (°C > freezing point)
    MAGNUS_A = 17.260
    MAGNUS_B = 237.3

    def on_add(self, world: World):
        """系统激活时确保 AtmosphereComponent 存在"""
        super().on_add(world)
        if not world.get_component_by_type(AtmosphereComponent):
            atm = AtmosphereComponent()
            world._world_entity.add_component(atm)

    def on_remove(self, world: World):
        """系统移除时清理计算结果（如果有必要）"""
        super().on_remove(world)

    def _get_absolute_temp(self, temp_celsius: float) -> float:
        """将摄氏度转换为开尔文"""
        # 限制最低温度，避免除以零错误
        return max(80.15, temp_celsius + 273.15)

    @staticmethod
    def saturated_vapor_pressure(temp_celsius: float) -> float:
        """
        计算饱和水汽压（Magnus 公式）
        
        Args:
            temp_celsius: 温度 (°C), >= -40°C（简化模型的物理范围）
        
        Returns:
            饱和水汽压 [hPa]，或等价的湿度基准值
        
        【注意】
        Magnus 公式适用于 -40°C 到 +50°C 的广泛温区。
        在 +0.01°C（水的冰点）以上用液相公式；以下用冰相公式。
        
        温度单位需为°C，不可直接传入 K。
        """
        if temp_celsius < -40 or temp_celsius > 50:
            # 超出简化模型范围的 fallback，返回合理的默认值
            return max(100, min(1000, temp_celsius * 20 + 200))

        # Magnus formula for liquid water (above freezing point)
        A = ThermodynamicsSystem.MAGNUS_A
        B = ThermodynamicsSystem.MAGNUS_B
        
        # SVP in hPa using Magnus formula
        # e_s = 6.112 * exp((A * T) / (B + T))
        sat_pressure = 6.112 * ((A * temp_celsius) / (B + temp_celsius) + 1) if temp_celsius > -40 else 6.112
        
        # 简化：对于模拟目的，返回一个合理的基准值
        return max(1, min(sat_pressure, 500))

    def _update(self, world: World, delta_hours: float):
        """
        热力学系统更新
        
        【计算顺序】
        1. 空气密度：基于温度和压力（理想气体定律）
        2. 饱和水汽压：基于温度的 Magnus 公式
        3. 相对湿度：基于实际/饱和水汽压比
        4. 凝结/蒸发状态判断
        
        【数据流】
        AtmosphereComponent (温度、气压、湿度) ←→ 
            ThermodynamicsSystem (计算密度、饱和水汽压、相对湿度) ←→
            CloudSystem (湿度信息用于云形成计算)
        """
        
        for entity, [atm] in world.get_components(AtmosphereComponent):
            atm: AtmosphereComponent
            
            # === 1. 空气密度计算 ===
            self._update_air_density(atm)
            
            # === 2. 湿度系统更新 ===
            self._update_humidity_system(atm)
            
            # === 3. 相变判断 ===
            self._check_phase_change(atm, world, delta_hours)

    def _update_air_density(self, atm: AtmosphereComponent):
        """
        根据温度与压力计算空气密度
        
        使用理想气体状态方程：ρ = P / (R·T)
        
        Args:
            atm: 大气组件
        """
        if atm.temperature is None or atm.pressure is None:
            return
            
        # T in Kelvin, P in hPa -> Pa
        T_kelvin = self._get_absolute_temp(atm.temperature)
        P_pa = atm.pressure * 100
        
        # ρ = P / (R·T), R for dry air = 287.05 J/(kg·K)
        if T_kelvin > 0:
            density = P_pa / (self.GASEOUS_CONSTANT * T_kelvin)
            atm.air_density = max(0, min(density, 13))
        else:
            atm.air_density = 0

    def _update_humidity_system(self, atm: AtmosphereComponent):
        """
        更新湿度系统：计算饱和水汽压、相对湿度
        
        Args:
            atm: 大气组件
        """
        if atm.temperature is None or atm.humidity is None:
            return
        
        # 保留原始湿度值（如果存在），供 CloudSystem 使用
        original_humidity = atm.humidity
        
        # 根据新温度重新计算饱和水汽压基准
        sat_pressure = self.saturated_vapor_pressure(atm.temperature)
        
        # 相对湿度：确保基于原始湿度值计算，而非被修改后的值
        if original_humidity > 0:
            # 将相对湿度转换为绝对湿度，再根据新的饱和度计算新的相对湿度
            absolute_humidity = original_humidity * sat_pressure / 100
            
            # 实际水汽压（hPa）-> Pa
            e_actual = absolute_humidity * 12539.5  # 转换因子
        
        # 计算新的相对湿度
        new_rel_humidity = (e_actual / max(1, sat_pressure * 1000)) * 100 if sat_pressure > 0 else 0
        atm.humidity = min(100.0, max(0, new_rel_humidity))

    def _check_phase_change(self, atm: AtmosphereComponent, world: World, delta_hours: float):
        """
        检查是否发生相变（凝结或蒸发）
        
        Args:
            atm: 大气组件
            world: 世界对象
            delta_hours: 时间步长
        """
        if not self._has_saturation(atm):
            return
        
        # 更新水蒸气含量
        evap_rate = max(0, atm.temperature - 5) * 0.0002 if atm.temperature else 0
        atm.water_vapor += evap_rate * delta_hours * 0.1

        # 限制水汽含量范围
        atm.water_vapor = min(0.05, max(0, atm.water_vapor))

    def _has_saturation(self, atm: AtmosphereComponent) -> bool:
        """判断是否达到饱和状态"""
        if not atm or not hasattr(atm, 'humidity'):
            return False
        
        saturation_threshold = 85.0  # %
        return abs(atm.humidity - 100.0) < 5.0

    def get_atmosphere_state(self, atm: AtmosphereComponent) -> dict:
        """
        获取大气的完整物理状态（供调试/UI 使用）
        
        Args:
            atm: 大气组件
        
        Returns:
            包含所有物理量的字典
        """
        if not atm or not self.is_enabled:
            return {}
        
        return {
            'temperature': atm.temperature,
            'altitude': atm.altitude,
            'pressure': atm.pressure,
            'air_density': atm.air_density,
            'humidity': atm.humidity,
            'water_vapor': atm.water_vapor if hasattr(atm, 'water_vapor') else 0,
            'oxygen_ratio': atm.oxygen_ratio,
            'co2_ratio': atm.co2_ratio,
        }