#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
径流计算器

职责：
    - 计算土壤饱和后的径流
    - 使用连续统重力水流模型
"""

import logging
from typing import Optional

from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class RunoffCalculator:
    """径流计算器"""

    def __init__(self, threshold: float = 0.9):
        self.threshold = threshold

    def calculate(self, soil: SoilComponent, world, entity, dt: float) -> None:
        """
        计算径流量

        Args:
            soil: 土壤组件
            world: ECS 世界
            entity: 土壤实体
            dt: 时间步长
        """
        # 检查是否饱和
        saturation = soil.moisture / soil.max_moisture if soil.max_moisture > 0 else 0.0
        if saturation < self.threshold:
            return

        # 计算超额水分
        excess = soil.moisture - soil.max_moisture * self.threshold

        # 查找下游位置
        space = world.get_component(entity, SpaceComponent)
        if space is None:
            return

        # 简化的径流：将超额水分转移到相邻低洼处
        runoff_amount = excess * 0.5 * dt  # 50% 超额水分形成径流
        soil.moisture -= runoff_amount

        # 尝试找到下游水体或土壤
        from space.space_system import SpaceSystem
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 查询附近的实体
        nearby = space_system.query_radius(space.x, space.y, 5)
        for target_id in nearby:
            if target_id == entity.id:
                continue
            target = world.query_entity(target_id)
            if target is None:
                continue

            # 检查是否是水体
            from environment.hydrology.components.water_body_component import WaterBodyComponent
            water = world.get_component(target, WaterBodyComponent)
            if water is not None and not water.is_dry:
                water.volume += runoff_amount * 0.3  # 30% 进入水体
                water.volume = min(water.volume, water.max_volume)
                runoff_amount *= 0.7
                break

            # 检查是否是低洼土壤
            target_soil = world.get_component(target, SoilComponent)
            target_space = world.get_component(target, SpaceComponent)
            if target_soil is not None and target_space is not None:
                # 简单判断：y 坐标更大的位置（假设 y 向下）
                if target_space.y > space.y:
                    target_soil.moisture += runoff_amount * 0.2
                    target_soil.moisture = min(target_soil.moisture, target_soil.max_moisture)
                    runoff_amount *= 0.8
                    break