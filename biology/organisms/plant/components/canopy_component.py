#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物冠层组件

描述植物冠层的光合作用结构与光照拦截特征。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class CanopyComponent(Component):
    """
    冠层组件

    属性:
        leaf_area_index: 叶面积指数 (LAI, m² 叶片 / m² 地表)
        canopy_radius: 冠层半径 (cm)
        shade_ratio: 遮光率 (0-1)，由 LightReceiveSystem 更新
        photosynthetic_efficiency: 光合效率 (默认 0.05)
    """
    leaf_area_index: float = 0.5
    canopy_radius: float = 5.0
    shade_ratio: float = 0.0
    photosynthetic_efficiency: float = 0.05