# simulation/environment/environment_component.py

from dataclasses import dataclass, field
from typing import Dict
from core.component import Component


@dataclass(slots=True)
class EnvironmentComponent(Component):
    """
    真实生态环境参数
    所有单位接近现实单位，方便做生理建模
    """

    # ======================
    # 光环境
    # ======================

    # 光合有效辐射 μmol/m²/s
    par: float = 300.0

    # 光周期（小时）
    photoperiod: float = 12.0

    # 日累计光量 DLI mol/m²/day（可由系统计算）
    dli: float = 0.0


    # ======================
    # 温度系统
    # ======================

    air_temperature: float = 25.0        # 大气温度 ℃
    soil_temperature: float = 22.0       # 地面温度 ℃
    day_night_temp_diff: float = 5.0     # 昼夜温差 ℃


    # ======================
    # 水分系统
    # ======================

    soil_moisture: float = 0.35          # 土壤湿度 0~1
    field_capacity: float = 0.45         # 田间持水量
    wilting_point: float = 0.15          # 凋萎点

    air_humidity: float = 0.6            # 相对湿度 0~1
    vpd: float = 1.2                     # kPa 蒸汽压亏缺


    # ======================
    # 气体系统
    # ======================

    co2: float = 420.0                   # ppm
    o2: float = 21.0                     # %


    # ======================
    # 土壤与养分
    # ======================

    soil_ph: float = 6.5                 # 土壤PH值
    soil_ec: float = 1.5                 # 土壤EC值（可溶性离子浓度） mS/cm

    nitrogen: float = 50.0               # 氮含量 mg/kg
    phosphorus: float = 20.0             # 磷含量 mg/kg
    potassium: float = 60.0              # 钾含量 mg/kg


    # ======================
    # 物理扰动
    # ======================

    wind_speed: float = 0.5              # m/s
    rainfall: float = 0.0                # mm/day


    # 扩展容器
    extra: Dict[str, float] = field(default_factory=dict)


    # ======================
    # 派生属性
    # ======================

    @property
    def is_daytime(self) -> bool:
        return self.par > 50

    @property
    def water_stress_index(self) -> float:
        """
        0~1 水分胁迫指数
        """
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