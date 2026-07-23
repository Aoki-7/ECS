#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渗透计算器

职责：
    - 计算土壤水分渗透到地下水的速率
    - 基于达西定律简化
"""

import logging

from environment.soil.components.soil_component import SoilComponent

logger = logging.getLogger(__name__)


class InfiltrationCalculator:
    """渗透计算器"""

    def __init__(self, base_rate: float = 0.01):
        self.base_rate = base_rate

    def calculate(self, soil: SoilComponent, world, entity, dt: float) -> None:
        """
        计算渗透量

        Args:
            soil: 土壤组件
            world: ECS 世界
            entity: 土壤实体
            dt: 时间步长
        """
        from environment.hydrology.components.groundwater_component import GroundwaterComponent

        # 检查是否有地下水组件
        groundwater = world.get_component(entity, GroundwaterComponent)
        if groundwater is None:
            return

        # 计算饱和度
        saturation = soil.moisture / soil.max_moisture if soil.max_moisture > 0 else 0.0

        # 饱和度越高，渗透越快
        saturation_factor = saturation ** 2  # 非线性关系

        # 计算渗透量
        infiltration = self.base_rate * saturation_factor * soil.permeability * dt
        infiltration = min(infiltration, soil.moisture)  # 不能超过现有水分

        # 更新土壤和地下水
        soil.moisture -= infiltration
        groundwater.level += infiltration / groundwater.aquifer_area if groundwater.aquifer_area > 0 else 0.0

        # 限制地下水水位
        groundwater.level = min(groundwater.level, groundwater.max_level)