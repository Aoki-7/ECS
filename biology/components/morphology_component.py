



# biology/components/morphology.py

from core.component import Component
from dataclasses import dataclass


@dataclass
class MorphologyComponent(Component):
    """
    仅负责最终可视外观
    """

    # ===== 基础结构 =====
    height: float = 0.5
    leaf_size: float = 0.5
    leaf_count: int = 2
    stem_thickness: float = 0.1

    # ===== 根系 =====
    root_depth: float = 0.5

    # ===== 颜色 =====
    green_intensity: float = 1.0   # 0~2
    yellowing: float = 0.0         # 0~1 枯黄

    # ===== 状态 =====
    wilting: float = 0.0           # 0~1