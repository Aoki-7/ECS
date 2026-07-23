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
        # 防御：使用 world.get_world_component 替代 entity.get_components
        atmosphere = world.get_world_component(AtmosphereComponent)
        weather = world.get_world_component(PhysicalWeatherComponent)
        scatter = world.get_world_component(LightScatterComponent)
        solar = world.get_world_component(SolarPositionComponent)

        if scatter is None:
            return

        params = self._extract_atmosphere_params(atmosphere, weather)

        elevation = solar.elevation if solar is not None else 45.0
        if elevation <= 0.0:
            scatter.rayleigh_factor = 0.0
            scatter.mie_factor = 0.0
            scatter.cloud_attenuation = 1.0
            return

        air_mass = self._compute_air_mass(elevation)
        self._compute_rayleigh(scatter, params, air_mass)
        self._compute_mie(scatter, params, air_mass)
        self._compute_cloud_attenuation(scatter, params)

    def _extract_atmosphere_params(self, atmosphere, weather) -> dict:
        """提取/推导大气物理量，统一返回字典"""
        if atmosphere is not None:
            return {
                "pressure": atmosphere.pressure,
                "temperature": atmosphere.temperature,
                "air_density": atmosphere.air_density,
                "aerosol": max(0.0, atmosphere.aerosol),
                "humidity_ratio": max(0.0, min(1.0, atmosphere.humidity / 100.0)),
                "cloud_cover": max(0.0, min(1.0, atmosphere.cloud_cover)),
                "cloud_density": max(0.0, atmosphere.cloud_density),
                "precipitation": weather.precipitation_rate if weather is not None else 0.0,
            }
        elif weather is not None:
            pressure = weather.pressure
            temperature = weather.temperature
            t_kelvin = max(temperature + 273.15, 80.0)
            air_density = pressure * 100.0 / (self._DRY_AIR_GAS_CONSTANT * t_kelvin)
            return {
                "pressure": pressure,
                "temperature": temperature,
                "air_density": air_density,
                "aerosol": 0.0,
                "humidity_ratio": max(0.0, min(1.0, weather.relative_humidity)),
                "cloud_cover": max(0.0, min(1.0, weather.cloud_cover)),
                "cloud_density": max(0.0, min(1.0, weather.cloud_cover)) * 0.8,
                "precipitation": weather.precipitation_rate,
            }
        else:
            return {
                "pressure": 1013.25,
                "temperature": 15.0,
                "air_density": 1.225,
                "aerosol": 0.0,
                "humidity_ratio": 0.5,
                "cloud_cover": 0.0,
                "cloud_density": 0.0,
                "precipitation": 0.0,
            }

    def _compute_rayleigh(self, scatter, params: dict, air_mass: float):
        """计算 Rayleigh 散射因子"""
        pressure_norm = params["pressure"] / 1013.25
        temp_norm = 288.15 / (params["temperature"] + 273.15)
        tau_rayleigh = self._RAYLEIGH_BASE * pressure_norm * temp_norm * air_mass
        scatter.rayleigh_factor = min(0.5, 1.0 - math.exp(-tau_rayleigh))

    def _compute_mie(self, scatter, params: dict, air_mass: float):
        """计算 Mie 散射因子（气溶胶 + 湿度吸湿增长）"""
        humidity_ratio = params["humidity_ratio"]
        if humidity_ratio > self._HUMIDITY_GROWTH_THRESHOLD:
            humidity_growth = 1.0 + 4.0 * math.pow(
                (humidity_ratio - self._HUMIDITY_GROWTH_THRESHOLD) / 0.3, 2
            )
        else:
            humidity_growth = 1.0

        tau_mie = self._MIE_BASE * params["aerosol"] * humidity_growth * air_mass
        scatter.mie_factor = min(0.5, 1.0 - math.exp(-tau_mie))

    def _compute_cloud_attenuation(self, scatter, params: dict):
        """计算云衰减"""
        tau_cloud = (
            params["cloud_density"] * self._CLOUD_EXTINCTION_EFF * params["cloud_cover"]
            + params["precipitation"] * self._PRECIP_EXTINCTION_EFF
        )
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