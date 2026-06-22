#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:environment_component.py
@说明:环境组件 v3.1 - 精简聚合视图

v3.1 变更:
- 从 ~230 字段精简至 ~25 个高频使用字段
- 移除土壤化学元素周期表、大量未使用派生字段
- 保留时间、天气、光照、土壤、大气的核心聚合字段
- 所有删除字段仍可通过 __getattr__ 获取默认值 0.0，保持向后兼容
- 明确职责：作为各子模块环境参数的单元格级聚合视图，
  详细物理过程参数由 atmosphere/、soil/、light_field/、physics_weather/ 等子模块实现
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass(slots=False)
class EnvironmentComponent(Component):
    """
    环境组件 - 精简聚合视图

    该组件仅保存其他系统高频读取的单元格级环境聚合状态，
    不重复实现各子模块的物理/化学细节参数。

    权威数据来源：
        - 大气物理：environment/physics_weather/components/physical_weather_component.py
        - 大气层：environment/atmosphere/components/atmosphere_component.py
        - 光照：environment/light_field/components/*.py
        - 季节：environment/season/season_component.py
        - 土壤：environment/soil/components/*.py
        - 污染：environment/pollution/components/pollution_component.py

    向后兼容：
        访问任何已删除字段时，__getattr__ 返回 0.0，避免旧代码崩溃。
    """

    # === 时间 (3) ===
    time_of_day: float = 0.0            # 一天中的时间 0-24
    is_daytime: bool = True             # 是否白天（由 PAR/太阳高度角推导）
    year_progress: float = 0.0          # 年进度 0-1

    # === 天气 (8) ===
    temperature: float = 25.0           # 气温 °C（兼容/前端）
    air_temperature: float = 25.0       # 气温 °C（生物/连续统/人类使用）
    humidity: float = 0.5               # 相对湿度 0-1（水文/兼容）
    air_humidity: float = 0.5           # 相对湿度 0-1（生物/连续统使用）
    precipitation: float = 0.0          # 降水量 mm
    rainfall: float = 0.0               # 日降雨量 mm/day
    wind_speed: float = 0.0             # 风速 m/s
    wind_direction: float = 0.0         # 风向 °

    # === 季节语义 (1) ===
    season: str = "spring"              # 季节名称（由 year_progress 推导）

    # === 光照 (4) ===
    light_level: float = 1.0            # 光照水平 0-1
    par: float = 300.0                  # 光合有效辐射 µmol/m²/s
    photoperiod: float = 12.0           # 光周期 h
    dli: float = 0.0                    # 日光照积分 mol/m²/day

    # === 土壤 (5) ===
    soil_moisture: float = 0.35         # 土壤湿度 0-1
    soil_temperature: float = 20.0      # 土壤温度 °C
    field_capacity: float = 0.3         # 田间持水量 0-1
    wilting_point: float = 0.1          # 萎蔫点 0-1
    water_stress_index: float = 0.0     # 水分胁迫指数 0-1

    # === 大气化学/派生 (4) ===
    co2: float = 0.0                    # CO₂ 浓度（ppm，由气体扩散系统维护）
    o2: float = 21.0                    # O₂ 浓度（%）
    vpd: float = 0.0                    # 蒸汽压差 kPa
    day_night_temp_diff: float = 5.0    # 昼夜温差 °C

    # === 历史记录 ===
    weather_history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        """根据初始化参数计算派生字段"""
        # 白天判断：PAR > 50 视为白天
        self.is_daytime = self.par > 50.0
        self._recalc_water_stress()

    def _recalc_water_stress(self):
        """根据土壤水分、田间持水量和萎蔫点重新计算水分胁迫指数"""
        fc = self.field_capacity
        wp = self.wilting_point
        if fc > wp:
            stress = (fc - self.soil_moisture) / (fc - wp)
            self.water_stress_index = float(max(0.0, min(1.0, stress)))
        else:
            self.water_stress_index = 0.0

    def snapshot(self) -> dict:
        """快照 - 返回高频使用字段"""
        return {
            'time_of_day': self.time_of_day,
            'is_daytime': self.is_daytime,
            'year_progress': self.year_progress,
            'season': self.season,
            'temperature': self.temperature,
            'air_temperature': self.air_temperature,
            'humidity': self.humidity,
            'air_humidity': self.air_humidity,
            'precipitation': self.precipitation,
            'rainfall': self.rainfall,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'light_level': self.light_level,
            'par': self.par,
            'photoperiod': self.photoperiod,
            'dli': self.dli,
            'soil_moisture': self.soil_moisture,
            'soil_temperature': self.soil_temperature,
            'water_stress_index': self.water_stress_index,
            'co2': self.co2,
            'o2': self.o2,
            'vpd': self.vpd,
            'day_night_temp_diff': self.day_night_temp_diff,
        }

    def __getattr__(self, name: str):
        """动态返回默认值，兼容任何缺失字段"""
        return 0.0
