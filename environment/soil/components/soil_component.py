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


@dataclass(slots=True)
class SoilComponent(Component):
    """
    土壤组件

    存储土壤的物理和化学属性
    """

    # ====
    # 物理属性
    # ====

    # 土壤类型
    soil_type: str = SoilType.LOAM

    # 土壤深度 (m)
    depth: float = 1.0

    # 土壤湿度 (0-1)
    moisture: float = 0.5

    # 土壤温度 (°C)
    temperature: float = 20.0

    # ====
    # 化学属性
    # ====

    # 土壤pH值 (0-14)
    ph: float = 6.5

    # 土壤EC值 (mS/cm)
    ec: float = 1.5

    # 总养分含量 (mg/kg) - 兼容旧API
    nitrogen: float = 50.0
    phosphorus: float = 20.0
    potassium: float = 60.0

    # 有机质含量 (%)
    organic_matter: float = 2.0
    
    # === 氮素形态分区 (mg/kg) ===
    nitrogen_organic: float = 40.0  # 有机氮，占总氮80%
    nitrogen_ammonium: float = 7.0  # 铵态氮，可被植物直接吸收
    nitrogen_nitrate: float = 3.0   # 硝态氮，可被植物直接吸收
    
    # === 磷素形态分区 (mg/kg) ===
    phosphorus_organic: float = 8.0  # 有机磷
    phosphorus_available: float = 12.0  # 有效磷，可被植物吸收
    
    # === 微生物参数 ===
    microbial_biomass: float = 0.1  # 微生物生物量碳 (mg/g)
    microbial_activity: float = 0.5  # 微生物活性 0-1，受温度/湿度/氧气影响
    
    def __post_init__(self):
        # 自动同步总氮/总磷值
        self._sync_total_nutrients()
    
    def _sync_total_nutrients(self) -> None:
        """同步总养分值，保持旧API兼容"""
        self.nitrogen = self.nitrogen_organic + self.nitrogen_ammonium + self.nitrogen_nitrate
        self.phosphorus = self.phosphorus_organic + self.phosphorus_available

    # ====
    # 水分特性
    # ====

    # 田间持水量 (0-1)
    field_capacity: float = 0.45

    # 凋萎点 (0-1)
    wilting_point: float = 0.15

    # 饱和含水量 (0-1)
    saturation: float = 0.55

    # 渗透率 (mm/h)
    permeability: float = 10.0

    # 土壤厚度 (m)，供侵蚀/沉积系统使用
    thickness: float = 1.0

    # 泥沙负荷 (kg/m²)，供侵蚀/沉积系统使用
    sediment_load: float = 0.0

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