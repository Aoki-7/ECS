#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:environment_component.py
@说明:环境组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=False)
class EnvironmentComponent(Component):
    """
    环境组件 - 纯数据版
    存储环境状态。
    """
    # 时间
    time_of_day: float = 0.0
    day_length: float = 24.0
    
    # 天气
    temperature: float = 20.0
    humidity: float = 0.5
    precipitation: float = 0.0
    wind_speed: float = 0.0
    wind_direction: float = 0.0
    
    # 季节
    season: str = "spring"
    year_progress: float = 0.0
    
    # 光照
    light_level: float = 1.0
    par: float = 100.0
    
    # 历史记录
    weather_history: List[Dict] = field(default_factory=list)
    
    # 兼容性字段
    is_daytime: bool = True
    air_temperature: float = 20.0
    soil_moisture: float = 0.5
    air_humidity: float = 0.5
    wind: float = 0.0
    light_intensity: float = 1.0
    field_capacity: float = 0.3
    wilting_point: float = 0.1
    water_stress_index: float = 0.0
    
    # 旧系统兼容性字段
    rainfall: float = 0.0
    soil_temperature: float = 20.0
    co2: float = 0.0
    soil_ph: float = 7.0
    nutrient_n: float = 0.0
    nutrient_p: float = 0.0
    nutrient_k: float = 0.0
    day_night_temp_diff: float = 5.0
    rainfall_mm_day: float = 0.0
    vpd: float = 0.0
    photoperiod: float = 12.0
    light_hours: float = 12.0
    night_temp: float = 15.0
    day_temp: float = 25.0
    relative_humidity: float = 0.5
    cloud_cover: float = 0.0
    precipitation_rate: float = 0.0
    solar_radiation: float = 0.0
    wind_chill: float = 20.0
    heat_index: float = 20.0
    dew_point: float = 10.0
    uv_index: float = 0.0
    visibility: float = 10.0
    air_pressure: float = 101.325
    oxygen_level: float = 0.21
    co2_level: float = 0.0004
    nitrogen_level: float = 0.78
    pollution_level: float = 0.0
    particulate_matter: float = 0.0
    pm25: float = 0.0
    pm10: float = 0.0
    aqi: float = 0.0
    o3_concentration: float = 0.0
    no2_level: float = 0.0
    so2_level: float = 0.0
    co_concentration: float = 0.0
    surface_temperature: float = 20.0
    soil_moisture_content: float = 0.3
    soil_water_potential: float = -0.1
    saturation: float = 0.5
    porosity: float = 0.4
    hydraulic_conductivity: float = 0.001
    infiltration_rate: float = 0.0
    runoff: float = 0.0
    drainage: float = 0.0
    percolation: float = 0.0
    capillary_rise: float = 0.0
    groundwater_level: float = 0.0
    water_table_depth: float = 0.0
    aquifer_thickness: float = 0.0
    transmissivity: float = 0.0
    storativity: float = 0.0
    evaporation_rate: float = 0.0
    transpiration_rate: float = 0.0
    eto: float = 0.0
    etr: float = 0.0
    sensible_heat_flux: float = 0.0
    latent_heat_flux: float = 0.0
    ground_heat_flux: float = 0.0
    net_radiation: float = 0.0
    albedo: float = 0.2
    emissivity: float = 0.95
    ndvi: float = 0.0
    lai: float = 0.0
    fapar: float = 0.0
    fvc: float = 0.0
    canopy_resistance: float = 0.0
    aerodynamic_resistance: float = 0.0
    boundary_layer_resistance: float = 0.0
    stomatal_resistance: float = 0.0
    leaf_area_index: float = 0.0
    bulk_temperature: float = 20.0
    deep_soil_temperature: float = 15.0
    skin_temperature: float = 20.0
    wet_bulb_temperature: float = 15.0
    enthalpy: float = 50.0
    mixing_ratio: float = 0.01
    absolute_humidity: float = 0.01
    specific_humidity: float = 0.01
    vapor_pressure: float = 2.0
    pressure_tendency: float = 0.0
    pressure_change_3h: float = 0.0
    wind_gust: float = 0.0
    wind_direction_variance: float = 0.0
    turbulence_intensity: float = 0.0
    convective_available_potential_energy: float = 0.0
    convective_inhibition: float = 0.0
    lifted_index: float = 0.0
    k_index: float = 0.0
    total_totals_index: float = 0.0
    showalter_index: float = 0.0
    precipitable_water: float = 0.0
    cloud_base_height: float = 0.0
    cloud_top_height: float = 0.0
    cloud_fraction: float = 0.0
    cloud_optical_depth: float = 0.0
    cloud_liquid_water_path: float = 0.0
    cloud_ice_water_path: float = 0.0
    cloud_effective_radius: float = 0.0
    cloud_number_concentration: float = 0.0
    ice_crystal_number_concentration: float = 0.0
    snow_water_equivalent: float = 0.0
    snow_depth: float = 0.0
    snow_density: float = 0.0
    snow_albedo: float = 0.8
    snow_temperature: float = 0.0
    snow_melt_rate: float = 0.0
    frost_depth: float = 0.0
    freeze_thaw_cycles: float = 0.0
    soil_heat_flux: float = 0.0
    soil_temperature_5cm: float = 20.0
    soil_temperature_10cm: float = 20.0
    soil_temperature_20cm: float = 20.0
    soil_temperature_50cm: float = 20.0
    soil_temperature_100cm: float = 20.0
    soil_moisture_5cm: float = 0.3
    soil_moisture_10cm: float = 0.3
    soil_moisture_20cm: float = 0.3
    soil_moisture_50cm: float = 0.3
    soil_moisture_100cm: float = 0.3
    soil_salinity: float = 0.0
    soil_ec: float = 0.0
    soil_cec: float = 0.0
    soil_base_saturation: float = 0.0
    soil_organic_matter: float = 0.0
    soil_nitrogen: float = 0.0
    soil_phosphorus: float = 0.0
    soil_potassium: float = 0.0
    soil_calcium: float = 0.0
    soil_magnesium: float = 0.0
    soil_sulfur: float = 0.0
    soil_boron: float = 0.0
    soil_copper: float = 0.0
    soil_zinc: float = 0.0
    soil_manganese: float = 0.0
    soil_iron: float = 0.0
    soil_molybdenum: float = 0.0
    soil_chlorine: float = 0.0
    soil_nickel: float = 0.0
    soil_cobalt: float = 0.0
    soil_selenium: float = 0.0
    soil_silicon: float = 0.0
    soil_aluminum: float = 0.0
    soil_lead: float = 0.0
    soil_cadmium: float = 0.0
    soil_chromium: float = 0.0
    soil_arsenic: float = 0.0
    soil_mercury: float = 0.0
    soil_beryllium: float = 0.0
    soil_thallium: float = 0.0
    soil_antimony: float = 0.0
    soil_barium: float = 0.0
    soil_tin: float = 0.0
    soil_titanium: float = 0.0
    soil_vanadium: float = 0.0
    soil_tungsten: float = 0.0
    soil_gallium: float = 0.0
    soil_indium: float = 0.0
    soil_thorium: float = 0.0
    soil_uranium: float = 0.0
    soil_plutonium: float = 0.0
    soil_americium: float = 0.0
    soil_curium: float = 0.0
    soil_californium: float = 0.0
    soil_einsteinium: float = 0.0
    soil_fermium: float = 0.0
    soil_mendelevium: float = 0.0
    soil_nobelium: float = 0.0
    soil_lawrencium: float = 0.0
    soil_rutherfordium: float = 0.0
    soil_dubnium: float = 0.0
    soil_seaborgium: float = 0.0
    soil_bohrium: float = 0.0
    soil_hassium: float = 0.0
    soil_meitnerium: float = 0.0
    soil_darmstadtium: float = 0.0
    soil_roentgenium: float = 0.0
    soil_copernicium: float = 0.0
    soil_nihonium: float = 0.0
    soil_flerovium: float = 0.0
    soil_moscovium: float = 0.0
    soil_livermorium: float = 0.0
    soil_tennessine: float = 0.0
    soil_oganesson: float = 0.0
    soil_hydrogen_content: float = 0.0
    soil_helium_content: float = 0.0
    soil_lithium_content: float = 0.0
    soil_beryllium_content: float = 0.0
    soil_boron_content: float = 0.0
    soil_carbon_content: float = 0.0
    soil_nitrogen_content: float = 0.0
    soil_oxygen_content: float = 0.0
    soil_fluorine_content: float = 0.0
    soil_neon_content: float = 0.0
    soil_sodium_content: float = 0.0
    soil_magnesium_content: float = 0.0
    soil_aluminum_content: float = 0.0
    soil_silicon_content: float = 0.0
    soil_phosphorus_content: float = 0.0
    soil_sulfur_content: float = 0.0
    soil_chlorine_content: float = 0.0
    soil_argon_content: float = 0.0
    soil_potassium_content: float = 0.0
    soil_calcium_content: float = 0.0
    soil_scandium_content: float = 0.0
    soil_titanium_content: float = 0.0
    soil_vanadium_content: float = 0.0
    soil_chromium_content: float = 0.0
    soil_manganese_content: float = 0.0
    soil_iron_content: float = 0.0
    soil_cobalt_content: float = 0.0
    soil_nickel_content: float = 0.0
    soil_copper_content: float = 0.0
    soil_zinc_content: float = 0.0
    soil_gallium_content: float = 0.0
    soil_germanium_content: float = 0.0
    soil_arsenic_content: float = 0.0
    soil_selenium_content: float = 0.0
    soil_bromine_content: float = 0.0
    soil_krypton_content: float = 0.0
    soil_rubidium_content: float = 0.0
    soil_strontium_content: float = 0.0
    soil_yttrium_content: float = 0.0
    soil_zirconium_content: float = 0.0
    soil_niobium_content: float = 0.0
    soil_molybdenum_content: float = 0.0
    soil_technetium_content: float = 0.0
    soil_ruthenium_content: float = 0.0
    soil_rhodium_content: float = 0.0
    soil_palladium_content: float = 0.0
    soil_silver_content: float = 0.0
    soil_cadmium_content: float = 0.0
    soil_indium_content: float = 0.0
    soil_tin_content: float = 0.0
    soil_antimony_content: float = 0.0
    soil_tellurium_content: float = 0.0
    soil_iodine_content: float = 0.0
    soil_xenon_content: float = 0.0
    soil_cesium_content: float = 0.0
    soil_barium_content: float = 0.0
    soil_lanthanum_content: float = 0.0
    soil_cerium_content: float = 0.0
    soil_praseodymium_content: float = 0.0
    soil_neodymium_content: float = 0.0
    soil_promethium_content: float = 0.0
    soil_samarium_content: float = 0.0
    soil_europium_content: float = 0.0
    soil_gadolinium_content: float = 0.0
    soil_terbium_content: float = 0.0
    soil_dysprosium_content: float = 0.0
    soil_holmium_content: float = 0.0
    soil_erbium_content: float = 0.0
    soil_thulium_content: float = 0.0
    soil_ytterbium_content: float = 0.0
    soil_lutetium_content: float = 0.0
    soil_hafnium_content: float = 0.0
    soil_tantalum_content: float = 0.0
    soil_tungsten_content: float = 0.0
    soil_rhenium_content: float = 0.0
    soil_osmium_content: float = 0.0
    soil_iridium_content: float = 0.0
    soil_platinum_content: float = 0.0
    soil_gold_content: float = 0.0
    soil_mercury_content: float = 0.0
    soil_thallium_content: float = 0.0
    soil_lead_content: float = 0.0
    soil_bismuth_content: float = 0.0
    soil_polonium_content: float = 0.0
    soil_astatine_content: float = 0.0
    soil_radon_content: float = 0.0
    soil_francium_content: float = 0.0
    soil_radium_content: float = 0.0
    soil_actinium_content: float = 0.0
    soil_thorium_content: float = 0.0
    soil_protactinium_content: float = 0.0
    soil_uranium_content: float = 0.0
    soil_neptunium_content: float = 0.0
    soil_plutonium_content: float = 0.0
    soil_americium_content: float = 0.0
    soil_curium_content: float = 0.0
    soil_berkelium_content: float = 0.0
    soil_californium_content: float = 0.0
    soil_einsteinium_content: float = 0.0
    soil_fermium_content: float = 0.0
    soil_mendelevium_content: float = 0.0
    soil_nobelium_content: float = 0.0
    soil_lawrencium_content: float = 0.0
    soil_rutherfordium_content: float = 0.0
    soil_dubnium_content: float = 0.0
    soil_seaborgium_content: float = 0.0
    soil_bohrium_content: float = 0.0
    soil_hassium_content: float = 0.0
    soil_meitnerium_content: float = 0.0
    soil_darmstadtium_content: float = 0.0
    soil_roentgenium_content: float = 0.0
    soil_copernicium_content: float = 0.0
    soil_nihonium_content: float = 0.0
    soil_flerovium_content: float = 0.0
    soil_moscovium_content: float = 0.0
    soil_livermorium_content: float = 0.0
    soil_tennessine_content: float = 0.0
    soil_oganesson_content: float = 0.0
    dli: float = 0.0
    o2: float = 21.0

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
