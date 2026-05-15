# AI Generated
"""
土壤组件
描述每个空间位置的土壤状态
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class SoilType:
    """土壤类型"""
    SAND = "sand"           # 沙土
    LOAM = "loam"           # 壤土
    CLAY = "clay"           # 黏土
    PEAT = "peat"           # 泥炭土
    CHALK = "chalk"         # 白垩土


@dataclass
class SoilComponent(Component):
    """
    土壤组件

    存储土壤的物理和化学属性
    """

    # =========================
    # 物理属性
    # =========================

    # 土壤类型
    soil_type: str = SoilType.LOAM

    # 土壤深度 (m)
    depth: float = 1.0

    # 土壤湿度 (0-1)
    moisture: float = 0.5

    # 土壤温度 (°C)
    temperature: float = 20.0

    # =========================
    # 化学属性
    # =========================

    # 土壤pH值 (0-14)
    ph: float = 6.5

    # 土壤EC值 (mS/cm)
    ec: float = 1.5

    # 养分含量 (mg/kg)
    nitrogen: float = 50.0
    phosphorus: float = 20.0
    potassium: float = 60.0

    # 有机质含量 (%)
    organic_matter: float = 2.0

    # =========================
    # 水分特性
    # =========================

    # 田间持水量 (0-1)
    field_capacity: float = 0.45

    # 凋萎点 (0-1)
    wilting_point: float = 0.15

    # 饱和含水量 (0-1)
    saturation: float = 0.55

    # 渗透率 (mm/h)
    permeability: float = 10.0

    def to_dict(self):
        """导出为字典"""
        return {
            "土壤类型": self.soil_type,
            "土壤深度": f"{self.depth}m",
            "土壤湿度": f"{self.moisture*100:.1f}%",
            "土壤温度": f"{self.temperature:.1f}°C",
            "pH值": self.ph,
            "EC值": f"{self.ec:.2f} mS/cm",
            "氮含量": f"{self.nitrogen:.1f} mg/kg",
            "磷含量": f"{self.phosphorus:.1f} mg/kg",
            "钾含量": f"{self.potassium:.1f} mg/kg",
            "有机质": f"{self.organic_matter:.1f}%",
        }
