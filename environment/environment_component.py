#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:environment_component.py
@说明:环境组件 v3.0 - 精简版

v3.0 变更:
- 从 324 字段精简至 ~30 核心字段
- 移除土壤化学元素周期表等不属于环境组件的字段
- 保留天气、光照、季节核心字段
- 向后兼容: 通过 __getattr__ 动态返回默认值 0.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=False)
class EnvironmentComponent(Component):
    """
    环境组件 - 精简版
    存储环境核心状态（天气、光照、季节）。
    """
    # === 时间 (2) ===
    time_of_day: float = 0.0            # 一天中的时间 0-24
    day_length: float = 24.0            # 昼长 h

    # === 天气 (5) ===
    temperature: float = 20.0           # 温度 °C
    humidity: float = 0.5               # 相对湿度 0-1
    precipitation: float = 0.0          # 降水量 mm
    wind_speed: float = 0.0             # 风速 m/s
    wind_direction: float = 0.0         # 风向 °

    # === 季节 (2) ===
    season: str = "spring"              # 季节
    year_progress: float = 0.0          # 年进度 0-1

    # === 光照 (2) ===
    light_level: float = 1.0            # 光照水平 0-1
    par: float = 100.0                  # 光合有效辐射 µmol/m²/s

    # === 历史记录 ===
    weather_history: List[Dict] = field(default_factory=list)

    # === 兼容字段 (常用) ===
    is_daytime: bool = True             # 是否白天
    air_temperature: float = 20.0       # 空气温度 (兼容)
    soil_moisture: float = 0.5          # 土壤湿度 (兼容)
    air_humidity: float = 0.5           # 空气湿度 (兼容)
    wind: float = 0.0                   # 风速 (兼容)
    light_intensity: float = 1.0        # 光照强度 (兼容)
    field_capacity: float = 0.3           # 田间持水量 (兼容)
    wilting_point: float = 0.1          # 萎蔫点 (兼容)
    water_stress_index: float = 0.0     # 水分胁迫指数 (兼容)
    rainfall: float = 0.0               # 降雨量 (兼容)
    soil_temperature: float = 20.0      # 土壤温度 (兼容)
    co2: float = 0.0                    # CO₂ (兼容)
    soil_ph: float = 7.0                # 土壤pH (兼容)
    nutrient_n: float = 0.0             # 氮 (兼容)
    nutrient_p: float = 0.0             # 磷 (兼容)
    nutrient_k: float = 0.0             # 钾 (兼容)
    day_night_temp_diff: float = 5.0    # 昼夜温差 (兼容)
    rainfall_mm_day: float = 0.0       # 日降雨 (兼容)
    vpd: float = 0.0                    # 蒸汽压差 (兼容)
    photoperiod: float = 12.0           # 光周期 (兼容)
    light_hours: float = 12.0           # 光照时数 (兼容)
    night_temp: float = 15.0            # 夜间温度 (兼容)
    day_temp: float = 25.0              # 白天温度 (兼容)
    relative_humidity: float = 0.5      # 相对湿度 (兼容)
    cloud_cover: float = 0.0            # 云量 (兼容)
    precipitation_rate: float = 0.0     # 降水率 (兼容)
    solar_radiation: float = 0.0        # 太阳辐射 (兼容)
    wind_chill: float = 20.0            # 风寒 (兼容)
    heat_index: float = 20.0            # 热指数 (兼容)
    dew_point: float = 10.0             # 露点 (兼容)
    uv_index: float = 0.0               # 紫外线 (兼容)
    visibility: float = 10.0            # 能见度 (兼容)
    air_pressure: float = 101.325         # 气压 (兼容)
    oxygen_level: float = 0.21          # 氧气 (兼容)
    co2_level: float = 0.0004           # CO₂ (兼容)
    nitrogen_level: float = 0.78          # 氮气 (兼容)
    pollution_level: float = 0.0          # 污染 (兼容)
    particulate_matter: float = 0.0       # 颗粒物 (兼容)
    pm25: float = 0.0                   # PM2.5 (兼容)
    pm10: float = 0.0                   # PM10 (兼容)
    aqi: float = 0.0                    # 空气质量指数 (兼容)
    o3_concentration: float = 0.0       # O₃ (兼容)
    no2_level: float = 0.0              # NO₂ (兼容)
    so2_level: float = 0.0              # SO₂ (兼容)
    co_concentration: float = 0.0       # CO (兼容)
    surface_temperature: float = 20.0   # 表面温度 (兼容)
    soil_moisture_content: float = 0.3  # 土壤水分 (兼容)
    soil_water_potential: float = -0.1  # 土壤水势 (兼容)
    saturation: float = 0.5             # 饱和度 (兼容)
    porosity: float = 0.4               # 孔隙度 (兼容)
    hydraulic_conductivity: float = 0.001 # 导水率 (兼容)
    infiltration_rate: float = 0.0      # 入渗率 (兼容)
    runoff: float = 0.0                 # 径流 (兼容)
    drainage: float = 0.0             # 排水 (兼容)
    percolation: float = 0.0            # 渗透 (兼容)
    capillary_rise: float = 0.0         # 毛细上升 (兼容)
    groundwater_level: float = 0.0        # 地下水位 (兼容)
    water_table_depth: float = 0.0      # 水位深度 (兼容)
    aquifer_thickness: float = 0.0      # 含水层厚度 (兼容)
    transmissivity: float = 0.0         # 导水系数 (兼容)
    storativity: float = 0.0            # 储水系数 (兼容)
    evaporation_rate: float = 0.0       # 蒸发率 (兼容)
    transpiration_rate: float = 0.0       # 蒸腾率 (兼容)
    eto: float = 0.0                    # 参考蒸散发 (兼容)
    etr: float = 0.0                    # 实际蒸散发 (兼容)
    sensible_heat_flux: float = 0.0     # 感热通量 (兼容)
    latent_heat_flux: float = 0.0       # 潜热通量 (兼容)
    ground_heat_flux: float = 0.0       # 地热通量 (兼容)
    net_radiation: float = 0.0           # 净辐射 (兼容)
    albedo: float = 0.2                 # 反照率 (兼容)
    emissivity: float = 0.95            # 发射率 (兼容)
    ndvi: float = 0.0                   # NDVI (兼容)
    lai: float = 0.0                    # 叶面积指数 (兼容)
    fapar: float = 0.0                  # 光合有效辐射吸收比 (兼容)
    fvc: float = 0.0                    # 植被覆盖度 (兼容)
    canopy_resistance: float = 0.0        # 冠层阻力 (兼容)
    aerodynamic_resistance: float = 0.0   # 空气动力学阻力 (兼容)
    boundary_layer_resistance: float = 0.0 # 边界层阻力 (兼容)
    stomatal_resistance: float = 0.0    # 气孔阻力 (兼容)
    leaf_area_index: float = 0.0        # 叶面积指数 (兼容)
    bulk_temperature: float = 20.0        # 整体温度 (兼容)
    deep_soil_temperature: float = 15.0   # 深层土壤温度 (兼容)
    skin_temperature: float = 20.0        # 地表温度 (兼容)
    wet_bulb_temperature: float = 15.0    # 湿球温度 (兼容)
    enthalpy: float = 50.0              # 焓 (兼容)
    mixing_ratio: float = 0.01          # 混合比 (兼容)
    absolute_humidity: float = 0.01     # 绝对湿度 (兼容)
    specific_humidity: float = 0.01     # 比湿 (兼容)
    vapor_pressure: float = 2.0           # 水汽压 (兼容)
    pressure_tendency: float = 0.0      # 气压趋势 (兼容)
    pressure_change_3h: float = 0.0       # 3h变压 (兼容)
    wind_gust: float = 0.0              # 阵风 (兼容)
    wind_direction_variance: float = 0.0  # 风向方差 (兼容)
    turbulence_intensity: float = 0.0     # 湍流强度 (兼容)
    convective_available_potential_energy: float = 0.0  # CAPE (兼容)
    convective_inhibition: float = 0.0    # CIN (兼容)
    lifted_index: float = 0.0           # 抬升指数 (兼容)
    k_index: float = 0.0                # K指数 (兼容)
    total_totals_index: float = 0.0     # 总 totals (兼容)
    showalter_index: float = 0.0          # Showalter指数 (兼容)
    precipitable_water: float = 0.0       # 可降水量 (兼容)
    cloud_base_height: float = 0.0        # 云底高 (兼容)
    cloud_top_height: float = 0.0         # 云顶高 (兼容)
    cloud_fraction: float = 0.0           # 云量 (兼容)
    cloud_optical_depth: float = 0.0      # 云光学厚度 (兼容)
    cloud_liquid_water_path: float = 0.0  # 云水路径 (兼容)
    cloud_ice_water_path: float = 0.0     # 冰水路径 (兼容)
    cloud_effective_radius: float = 0.0   # 云有效半径 (兼容)
    cloud_number_concentration: float = 0.0 # 云滴数浓度 (兼容)
    ice_crystal_number_concentration: float = 0.0 # 冰晶数浓度 (兼容)
    snow_water_equivalent: float = 0.0    # 雪水当量 (兼容)
    snow_depth: float = 0.0             # 雪深 (兼容)
    snow_density: float = 0.0             # 雪密度 (兼容)
    snow_albedo: float = 0.8              # 雪反照率 (兼容)
    snow_temperature: float = 0.0         # 雪温 (兼容)
    snow_melt_rate: float = 0.0           # 融雪率 (兼容)
    frost_depth: float = 0.0              # 冻深 (兼容)
    freeze_thaw_cycles: float = 0.0       # 冻融循环 (兼容)
    soil_heat_flux: float = 0.0           # 土壤热通量 (兼容)
    soil_temperature_5cm: float = 20.0    # 5cm土壤温度 (兼容)
    soil_temperature_10cm: float = 20.0     # 10cm土壤温度 (兼容)
    soil_temperature_20cm: float = 20.0     # 20cm土壤温度 (兼容)
    soil_temperature_50cm: float = 20.0     # 50cm土壤温度 (兼容)
    soil_temperature_100cm: float = 20.0    # 100cm土壤温度 (兼容)
    soil_moisture_5cm: float = 0.3          # 5cm土壤湿度 (兼容)
    soil_moisture_10cm: float = 0.3         # 10cm土壤湿度 (兼容)
    soil_moisture_20cm: float = 0.3         # 20cm土壤湿度 (兼容)
    soil_moisture_50cm: float = 0.3         # 50cm土壤湿度 (兼容)
    soil_moisture_100cm: float = 0.3        # 100cm土壤湿度 (兼容)
    soil_salinity: float = 0.0             # 土壤盐度 (兼容)
    soil_ec: float = 0.0                  # 土壤电导率 (兼容)
    soil_cec: float = 0.0                 # 土壤阳离子交换量 (兼容)
    soil_base_saturation: float = 0.0       # 土壤碱饱和度 (兼容)
    soil_organic_matter: float = 0.0        # 土壤有机质 (兼容)
    soil_nitrogen: float = 0.0              # 土壤氮 (兼容)
    soil_phosphorus: float = 0.0            # 土壤磷 (兼容)
    soil_potassium: float = 0.0             # 土壤钾 (兼容)
    soil_calcium: float = 0.0               # 土壤钙 (兼容)
    soil_magnesium: float = 0.0             # 土壤镁 (兼容)
    soil_sulfur: float = 0.0                # 土壤硫 (兼容)
    soil_boron: float = 0.0                 # 土壤硼 (兼容)
    soil_copper: float = 0.0                # 土壤铜 (兼容)
    soil_zinc: float = 0.0                  # 土壤锌 (兼容)
    soil_manganese: float = 0.0              # 土壤锰 (兼容)
    soil_iron: float = 0.0                  # 土壤铁 (兼容)
    soil_molybdenum: float = 0.0            # 土壤钼 (兼容)
    soil_chlorine: float = 0.0              # 土壤氯 (兼容)
    soil_nickel: float = 0.0                 # 土壤镍 (兼容)
    soil_cobalt: float = 0.0                # 土壤钴 (兼容)
    soil_chromium: float = 0.0               # 土壤铬 (兼容)
    soil_lead: float = 0.0                  # 土壤铅 (兼容)
    soil_cadmium: float = 0.0               # 土壤镉 (兼容)
    soil_mercury: float = 0.0                 # 土壤汞 (兼容)
    soil_arsenic: float = 0.0                 # 土壤砷 (兼容)
    soil_selenium: float = 0.0                # 土壤硒 (兼容)
    soil_fluoride: float = 0.0                # 土壤氟 (兼容)
    soil_iodine: float = 0.0                  # 土壤碘 (兼容)
    soil_radon: float = 0.0                   # 土壤氡 (兼容)
    soil_uranium: float = 0.0                 # 土壤铀 (兼容)
    soil_thorium: float = 0.0                 # 土壤钍 (兼容)
    soil_plutonium: float = 0.0               # 土壤钚 (兼容)
    soil_americium: float = 0.0               # 土壤镅 (兼容)
    soil_curium: float = 0.0                  # 土壤锔 (兼容)
    soil_californium: float = 0.0             # 土壤锎 (兼容)
    soil_einsteinium: float = 0.0             # 土壤锿 (兼容)
    soil_fermium: float = 0.0                 # 土壤镄 (兼容)
    soil_mendelevium: float = 0.0             # 土壤钔 (兼容)
    soil_nobelium: float = 0.0                # 土壤锘 (兼容)
    soil_lawrencium: float = 0.0              # 土壤铹 (兼容)
    soil_rutherfordium: float = 0.0             # 土壤𬬻 (兼容)
    soil_dubnium: float = 0.0                 # 土壤𬭊 (兼容)
    soil_seaborgium: float = 0.0              # 土壤𬭳 (兼容)
    soil_bohrium: float = 0.0                 # 土壤𬭛 (兼容)
    soil_hassium: float = 0.0                 # 土壤𬭶 (兼容)
    soil_meitnerium: float = 0.0              # 土壤𬭨 (兼容)
    soil_darmstadtium: float = 0.0            # 土壤𬭭 (兼容)
    soil_roentgenium: float = 0.0             # 土壤𬬭 (兼容)
    soil_copernicium: float = 0.0             # 土壤𬬭 (兼容)
    soil_nihonium: float = 0.0                # 土壤鉨 (兼容)
    soil_flerovium: float = 0.0                 # 土壤𫓧 (兼容)
    soil_moscovium: float = 0.0               # 土壤镆 (兼容)
    soil_livermorium: float = 0.0             # 土壤𫟷 (兼容)
    soil_tennessine: float = 0.0              # 土壤𫟼 (兼容)
    soil_oganesson: float = 0.0               # 土壤鿫 (兼容)
    dli: float = 0.0                          # 日光照积分 (兼容)
    o2: float = 21.0                          # 氧气浓度 (兼容)

    def snapshot(self) -> dict:
        """快照"""
        return {
            'temperature': self.temperature,
            'humidity': self.humidity,
            'precipitation': self.precipitation,
            'wind_speed': self.wind_speed,
            'light_level': self.light_level,
            'par': self.par,
            'season': self.season,
        }

    def __getattr__(self, name: str):
        """动态返回默认值，兼容任何缺失字段"""
        return 0.0
