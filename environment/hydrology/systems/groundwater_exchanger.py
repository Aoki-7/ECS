#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地下水交换器

职责：
    - 计算地下水与水体之间的交换
    - 使用扩散模型
"""

import logging

from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.hydrology.components.water_body_component import WaterBodyComponent

logger = logging.getLogger(__name__)


class GroundwaterExchanger:
    """地下水交换器"""

    def __init__(self, discharge_rate: float = 0.005):
        self.discharge_rate = discharge_rate

    def exchange(self, world, dt: float) -> None:
        """
        执行地下水交换

        Args:
            world: ECS 世界
            dt: 时间步长
        """
        # 处理所有地下水组件
        for entity, (groundwater,) in world.get_components(GroundwaterComponent):
            # 检查是否有相邻水体
            from space.space_component import SpaceComponent
            from space.space_system import SpaceSystem

            space = world.get_component(entity, SpaceComponent)
            if space is None:
                continue

            space_system = world.get_system(SpaceSystem)
            if space_system is None:
                continue

            # 查询附近的实体
            nearby = space_system.query_radius(space.x, space.y, 10)
            for target_id in nearby:
                if target_id == entity.id:
                    continue
                target = world.query_entity(target_id)
                if target is None:
                    continue

                water = world.get_component(target, WaterBodyComponent)
                if water is None or water.is_dry:
                    continue

                # 计算交换量
                # 地下水水位高于水体时，地下水补给水体
                # 反之，水体补给地下水
                water_level = water.volume / water.max_volume if water.max_volume > 0 else 0.0
                groundwater_level = groundwater.level / groundwater.max_level if groundwater.max_level > 0 else 0.0

                level_diff = groundwater_level - water_level

                if abs(level_diff) < 0.1:
                    continue  # 差异太小，不交换

                # 计算交换量
                exchange_amount = self.discharge_rate * abs(level_diff) * dt

                if level_diff > 0:
                    # 地下水补给水体
                    exchange_amount = min(exchange_amount, groundwater.level * groundwater.aquifer_area)
                    exchange_amount = min(exchange_amount, water.max_volume - water.volume)
                    groundwater.level -= exchange_amount / groundwater.aquifer_area if groundwater.aquifer_area > 0 else 0.0
                    water.volume += exchange_amount
                else:
                    # 水体补给地下水
                    exchange_amount = min(exchange_amount, water.volume)
                    exchange_amount = min(exchange_amount, (groundwater.max_level - groundwater.level) * groundwater.aquifer_area)
                    water.volume -= exchange_amount
                    groundwater.level += exchange_amount / groundwater.aquifer_area if groundwater.aquifer_area > 0 else 0.0

                break  # 只处理最近的一个水体