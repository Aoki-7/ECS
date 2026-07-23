# AI Generated
"""
地形组件
存储地形的物理属性
"""

from dataclasses import dataclass
from core.component import Component
from environment.terrain.config.terrain_types import TerrainType


@dataclass(slots=True)
class TerrainComponent(Component):
    """
    地形基础状态

    存储地形的物理属性，地形类型可以通过这些属性推导得出
    """

    # ====
    # 基础地形属性
    # ====

    elevation: float = 0.0      # 海拔高度 (m)
    slope: float = 0.0          # 坡度 (度)
    aspect: float = 0.0         # 坡向 (0-360度)
    roughness: float = 0.0      # 粗糙度 (0-1)
    curvature: float = 0.0      # 曲率

    # ====
    # 水文属性
    # ====

    water_depth: float = 0.0    # 地表水深 (m)
    water_table: float = -2.0   # 地下水位 (m, 负值表示在地下)

    # ====
    # 植被属性
    # ====

    vegetation_cover: float = 0.0    # 植被覆盖率 (0-1)
    vegetation_height: float = 0.0    # 植被高度 (m)
    vegetation_type: str = ""         # 植被类型

    # ====
    # 计算属性
    # ====
    terrain_type: TerrainType = None  # 地形类型（通过对应地形系统推导得出）

    def to_dict(self):
        """导出为字典"""
        return {
            "海拔": f"{self.elevation:.1f}m",
            "坡度": f"{self.slope:.1f}°",
            "坡向": f"{self.aspect:.1f}°",
            "粗糙度": f"{self.roughness:.2f}",
            "曲率": f"{self.curvature:.2f}",
            "地表水深": f"{self.water_depth:.2f}m",
            "地下水位": f"{self.water_table:.2f}m",
            "植被覆盖": f"{self.vegetation_cover*100:.1f}%",
            "植被高度": f"{self.vegetation_height:.1f}m",
        }