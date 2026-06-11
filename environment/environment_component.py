# simulation/environment/environment_component.py

from dataclasses import dataclass, field
from typing import Dict
from core.component import Component
from environment.config.environment_constants import (
    DEFAULT_PAR, DEFAULT_PHOTOPERIOD, DAYTIME_PAR_THRESHOLD,
    DEFAULT_AIR_TEMP, DEFAULT_SOIL_TEMP, DEFAULT_TEMP_DIFF,
    DEFAULT_SOIL_MOISTURE, DEFAULT_FIELD_CAPACITY, DEFAULT_WILTING_POINT,
    DEFAULT_AIR_HUMIDITY, DEFAULT_VPD,
    DEFAULT_CO2, DEFAULT_O2,
    DEFAULT_SOIL_PH, DEFAULT_SOIL_EC,
    DEFAULT_NITROGEN, DEFAULT_PHOSPHORUS, DEFAULT_POTASSIUM,
    DEFAULT_WIND_SPEED, DEFAULT_RAINFALL,
)


@dataclass(slots=True)
class EnvironmentComponent(Component):
    """
    真实生态环境参数
    所有单位接近现实单位，方便做生理建模
    """

    # =
    # 光环境
    # =

    par: float = DEFAULT_PAR
    photoperiod: float = DEFAULT_PHOTOPERIOD
    dli: float = 0.0

    # =
    # 温度系统
    # =

    air_temperature: float = DEFAULT_AIR_TEMP
    soil_temperature: float = DEFAULT_SOIL_TEMP
    day_night_temp_diff: float = DEFAULT_TEMP_DIFF

    # =
    # 水分系统
    # =

    soil_moisture: float = DEFAULT_SOIL_MOISTURE
    field_capacity: float = DEFAULT_FIELD_CAPACITY
    wilting_point: float = DEFAULT_WILTING_POINT
    air_humidity: float = DEFAULT_AIR_HUMIDITY
    vpd: float = DEFAULT_VPD

    # =
    # 气体系统
    # =

    co2: float = DEFAULT_CO2
    o2: float = DEFAULT_O2

    # =
    # 土壤与养分
    # =

    soil_ph: float = DEFAULT_SOIL_PH
    soil_ec: float = DEFAULT_SOIL_EC
    nitrogen: float = DEFAULT_NITROGEN
    phosphorus: float = DEFAULT_PHOSPHORUS
    potassium: float = DEFAULT_POTASSIUM

    # =
    # 物理扰动
    # =

    wind_speed: float = DEFAULT_WIND_SPEED
    rainfall: float = DEFAULT_RAINFALL

    # 扩展容器
    extra: Dict[str, float] = field(default_factory=dict)

    # =
    # 派生属性
    # =

    @property
    def is_daytime(self) -> bool:
        return self.par > DAYTIME_PAR_THRESHOLD

    @property
    def water_stress_index(self) -> float:
        """0~1 水分胁迫指数"""
        if self.soil_moisture <= self.wilting_point:
            return 1.0
        if self.soil_moisture >= self.field_capacity:
            return 0.0
        return (
            (self.field_capacity - self.soil_moisture)
            / (self.field_capacity - self.wilting_point)
        )

    def snapshot(self) -> dict:
        return {
            k: getattr(self, k)
            for k in self.__dataclass_fields__
        }