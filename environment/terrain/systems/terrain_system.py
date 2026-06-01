#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:terrain_system.py
@说明:地形系统，随着时间变化而变化
@时间:2026/03/11 23:38:04
@作者:Sherry
@版本:1.0
'''


# AI Generated
"""
地形系统
负责地形类型的推导和更新
"""

from core.system import System
from core.world import World
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_classifier import TerrainClassifier


class TerrainSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    地形系统

    负责根据物理属性推导地形类型
    """

    def __init__(self):
        super().__init__()
        self.priority = 15

    def update(self, world: World, dt: float):
        """
        更新所有地形组件

        推导每个位置的地形类型
        """
        # 遍历所有拥有TerrainComponent的实体
        for entity, (terrain,) in world.get_components(TerrainComponent):
            # 获取土壤湿度（如果有）
            from environment.soil.components.soil_component import SoilComponent
            soil = world.get_component(entity, SoilComponent)

            soil_moisture = soil.moisture if soil else 0.5

            # 推导地形类型
            terrain_type = TerrainClassifier.classify(terrain, soil_moisture)

            # 可以在这里存储推导结果或触发相关事件
            # 当前版本仅作为演示