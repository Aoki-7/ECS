#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
河流流动计算器

职责：
    - 计算河流从上游到下游的流动
    - 使用连通图模型
"""

import logging
from typing import Dict, List, Optional, Set

from environment.hydrology.components.water_body_component import WaterBodyComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class RiverFlowCalculator:
    """河流流动计算器"""

    def __init__(self, flow_rate: float = 0.1):
        self.flow_rate = flow_rate

    def calculate(self, world, dt: float) -> None:
        """
        计算河流流动

        Args:
            world: ECS 世界
            dt: 时间步长
        """
        # 构建河流连通图
        river_graph = self._build_river_graph(world)

        # 计算流动
        for river_id, downstream_id in river_graph.items():
            if downstream_id is None:
                continue

            river = world.query_entity(river_id)
            downstream = world.query_entity(downstream_id)

            if river is None or downstream is None:
                continue

            river_water = world.get_component(river, WaterBodyComponent)
            downstream_water = world.get_component(downstream, WaterBodyComponent)

            if river_water is None or downstream_water is None:
                continue

            # 计算流动量
            flow_amount = self.flow_rate * river_water.volume * dt
            flow_amount = min(flow_amount, river_water.volume * 0.1)  # 最多流动 10%

            # 更新水量
            river_water.volume -= flow_amount
            downstream_water.volume += flow_amount
            downstream_water.volume = min(downstream_water.volume, downstream_water.max_volume)

    def _build_river_graph(self, world) -> Dict[int, Optional[int]]:
        """
        构建河流连通图

        Returns:
            {river_id: downstream_id} 映射
        """
        river_graph = {}
        rivers = []

        # 收集所有河流
        for entity, (water, space) in world.get_components(WaterBodyComponent, SpaceComponent):
            if getattr(water, 'is_river', False):
                rivers.append((entity.id, space))

        # 按 y 坐标排序（假设 y 向下，y 大的在下游）
        rivers.sort(key=lambda x: x[1].y)

        # 构建连通图
        for i, (river_id, river_space) in enumerate(rivers):
            # 查找下游河流
            downstream = None
            min_dist = float('inf')

            for j in range(i + 1, len(rivers)):
                downstream_id, downstream_space = rivers[j]
                dist = ((river_space.x - downstream_space.x) ** 2 +
                        (river_space.y - downstream_space.y) ** 2) ** 0.5

                if dist < 20 and dist < min_dist:  # 20 格范围内的最近河流
                    min_dist = dist
                    downstream = downstream_id

            river_graph[river_id] = downstream

        return river_graph