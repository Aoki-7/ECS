"""
大气-光耦合系统（物理推演版）

从 AtmosphereComponent + PhysicalWeatherComponent + SolarPositionComponent
读取大气/云/太阳位置参数，推导出光学散射参数，写入 LightScatterComponent。

设计原则：
1. 零硬编码天气假设 — 所有默认值从物理状态推导。
2. 光学路径长度（air mass）依赖太阳高度角。
3. 湿度非线性影响气溶胶散射效率（吸湿增长效应）。
4. 云衰减用光学深度模型，考虑降水增强。
"""

import math

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.light_field.components.light_scatter_component import (
    LightScatterComponent,
)
from environment.light_field.components.solar_position_component import (
    SolarPositionComponent,
)


class LightAtmosphereCouplingSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """大气-光耦合系统 —— 将大气物理状态转化为光学散射参数。"""

    # ── 地球/大气固有物理常数（非天气假设） ──
    _RAYLEIGH_BASE = 0.094          # 海平面垂直方向 Rayleigh 光学深度（可见光）
    _MIE_BASE = 0.15                # 气溶胶单位浓度基准光学深度
    _HUMIDITY_GROWTH_THRESHOLD = 0.70   # 气溶胶吸湿增长临界相对湿度 (0-1)
    _CLOUD_EXTINCTION_EFF = 8.0     # 云消光效率系数
    _PRECIP_EXTINCTION_EFF = 3.0    # 降水附加消光效率 (mm/h)⁻¹
    _DRY_AIR_GAS_CONSTANT = 287.05  # J/(kg·K)

    def update(self, world: World, delta_hour: float):
        atmosphere, weather, scatter, solar = world._world_entity.get_components(
            AtmosphereComponent,
            PhysicalWeatherComponent,
            LightScatterComponent,
            SolarPositionComponent,
        )

        if scatter is None:
            return

        # ── 1. 提取/推导大气物理量 ──
        if atmosphere is not None:
            pressure = atmosphere.pressure               # hPa
            temperature = atmosphere.temperature         # °C
            air_density = atmosphere.air_density         # kg/m³
            aerosol = max(0.0, atmosphere.aerosol)       # 0-1
            humidity_ratio = max(0.0, min(1.0, atmosphere.humidity / 100.0))
            cloud_cover = max(0.0, min(1.0, atmosphere.cloud_cover))
            cloud_density = max(0.0, atmosphere.cloud_density)
            precipitation = (
                weather.precipitation_rate if weather is not None else 0.0
            )
        elif weather is not None:
            # 无 AtmosphereComponent 时，从 PhysicalWeatherComponent 推导全部
            pressure = weather.pressure
            temperature = weather.temperature
            t_kelvin = max(temperature + 273.15, 80.0)
            # 理想气体状态方程：ρ = P / (R·T)  （P 从 hPa 转 Pa）
            air_density = pressure * 100.0 / (self._DRY_AIR_GAS_CONSTANT * t_kelvin)
            aerosol = 0.0          # 无气溶胶数据 → 清洁大气假设（而非硬编码 0.05）
            humidity_ratio = max(0.0, min(1.0, weather.relative_humidity))
            cloud_cover = max(0.0, min(1.0, weather.cloud_cover))
            # 云量→云厚推导：云量 100% 时假设厚度 0.8（中等云系）
            cloud_density = cloud_cover * 0.8
            precipitation = weather.precipitation_rate
        else:
            # 极端 fallback：无任何大气数据时，推导出标准海平面清洁大气
            pressure = 1013.25
            temperature = 15.0
            air_density = 1.225
            aerosol = 0.0
            humidity_ratio = 0.5
            cloud_cover = 0.0
            cloud_density = 0.0
            precipitation = 0.0

        # ── 2. 光学路径长度（相对大气质量 air mass）──
        elevation = solar.elevation if solar is not None else 45.0
        if elevation <= 0.0:
            # 夜间：无光，散射参数归零，云衰减满值
            scatter.rayleigh_factor = 0.0
            scatter.mie_factor = 0.0
            scatter.cloud_attenuation = 1.0
            return

        air_mass = self._compute_air_mass(elevation)

        # ── 3. Rayleigh 散射因子 ──
        # 与气压（正比）、air_mass（正比）、温度（反比）相关
        pressure_norm = pressure / 1013.25
        temp_norm = 288.15 / (temperature + 273.15)
        tau_rayleigh = self._RAYLEIGH_BASE * pressure_norm * temp_norm * air_mass
        # 用指数衰减转等效能量损失比例，上限 0.5
        scatter.rayleigh_factor = min(0.5, 1.0 - math.exp(-tau_rayleigh))

        # ── 4. Mie 散射因子（气溶胶 + 湿度吸湿增长）──
        # 相对湿度 > 70% 时，气溶胶粒径非线性增长，散射效率急剧上升
        if humidity_ratio > self._HUMIDITY_GROWTH_THRESHOLD:
            humidity_growth = 1.0 + 4.0 * math.pow(
                (humidity_ratio - self._HUMIDITY_GROWTH_THRESHOLD) / 0.3, 2
            )
        else:
            humidity_growth = 1.0

        tau_mie = self._MIE_BASE * aerosol * humidity_growth * air_mass
        scatter.mie_factor = min(0.5, 1.0 - math.exp(-tau_mie))

        # ── 5. 云衰减 ──
        # 云光学深度 = 云厚度×消光效率×云量覆盖 + 降水附加消光
        tau_cloud = (
            cloud_density * self._CLOUD_EXTINCTION_EFF * cloud_cover
            + precipitation * self._PRECIP_EXTINCTION_EFF
        )
        # 输出衰减比例（1 - 透射率），上限 0.98（保留极微弱光照）
        scatter.cloud_attenuation = min(0.98, 1.0 - math.exp(-tau_cloud))

    @staticmethod
    def _compute_air_mass(elevation_deg: float) -> float:
        """
        计算相对大气质量（air mass）。

        使用 Kasten-Young 近似公式（适合 elevation > 2°）。
        低角度时返回经验极限值，避免除零。
        """
        if elevation_deg >= 90.0:
            return 1.0
        if elevation_deg < 2.0:
            # 地平线附近经验极限值
            return 37.0
        sin_elev = math.sin(math.radians(elevation_deg))
        return 1.0 / (
            sin_elev
            + 0.50572 * math.pow(elevation_deg + 6.07995, -1.6364)
        )
