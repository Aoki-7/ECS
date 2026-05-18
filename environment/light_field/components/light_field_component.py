# AI Generated
"""
光场组件
描述每个空间位置的光照状态
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class LightFieldComponent(Component):
    """
    光场组件

    存储光照相关的物理量
    """

    # ====
    # 光照强度
    # ====

    # 光合有效辐射 (μmol/m²/s)
    par: float = 300.0

    # 总辐射 (W/m²)
    total_radiation: float = 500.0

    # 直射辐射 (W/m²)
    direct_radiation: float = 350.0

    # 散射辐射 (W/m²)
    diffuse_radiation: float = 150.0

    # ====
    # 光照方向
    # ====

    # 太阳高度角 (0-90度)
    sun_elevation: float = 45.0

    # 太阳方位角 (0-360度)
    sun_azimuth: float = 180.0

    # ====
    # 光谱分布
    # ====

    # 红光比例 (0-1)
    red_ratio: float = 0.3

    # 蓝光比例 (0-1)
    blue_ratio: float = 0.2

    # 绿光比例 (0-1)
    green_ratio: float = 0.3

    # ====
    # 阴影信息
    # ====

    # 是否在阴影中
    in_shadow: bool = False

    # 阴影强度 (0-1)
    shadow_intensity: float = 0.0

    # 光照时长 (小时)
    light_duration: float = 12.0

    # ====
    # 光质
    # ====

    # 红蓝光比
    red_blue_ratio: float = 1.5

    # 光质因子 (影响植物形态)
    light_quality: float = 1.0

    def to_dict(self):
        """导出为字典"""
        return {
            "PAR": f"{self.par:.1f} μmol/m²/s",
            "总辐射": f"{self.total_radiation:.1f} W/m²",
            "直射辐射": f"{self.direct_radiation:.1f} W/m²",
            "散射辐射": f"{self.diffuse_radiation:.1f} W/m²",
            "太阳高度角": f"{self.sun_elevation:.1f}°",
            "太阳方位角": f"{self.sun_azimuth:.1f}°",
            "阴影": "是" if self.in_shadow else "否",
            "阴影强度": f"{self.shadow_intensity*100:.1f}%",
            "光照时长": f"{self.light_duration:.1f}h",
        }
