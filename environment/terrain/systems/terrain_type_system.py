#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:terrain_system_new.py
@说明:只负责类型的推导和更新
@时间:2026/04/12 22:31:28
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

from environment.soil.components.soil_component import SoilComponent

class TerrainTypeSystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
    地形系统

    负责根据物理属性推导地形类型
    """
    def __init__(self):
        self.priority = 15 # 设置系统优先级，确保在土壤系统之后执行
        
    def update(self, world: World, dt: float):
        """
        更新所有地形组件

        推导每个位置的地形类型
        """
        # 遍历所有同时拥有 TerrainComponent 和 SoilComponent 的实体
        for _, (terrain, soil) in world.get_components(TerrainComponent, SoilComponent):
            terrain: TerrainComponent
            soil: SoilComponent

            soil_moisture = soil.moisture if soil else 0.5

            # 推导地形类型
            terrain_type = TerrainClassifier.classify(terrain, soil_moisture)

            # 存储推导结果
            terrain.terrain_type = terrain_type