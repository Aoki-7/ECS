#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
地质系统

管理地形地质组件的动态演化：
- 板块移动（PlateComponent）
- 沉积物积累（SedimentComponent）
- 地表物质风化（SurfaceMaterialComponent）
"""

from core.system import System
from core.world import World

from environment.terrain.components.plate_component import PlateComponent
from environment.terrain.components.sediment_component import SedimentComponent
from environment.terrain.components.surface_material_component import SurfaceMaterialComponent


class GeologySystem(System):
    """地质演化系统"""

    tick_interval = 100  # 地质过程极慢
    priority = 10

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)

        # 板块移动
        for entity, (plate) in world.get_components(PlateComponent):
            plate.vx *= 0.999
            plate.vy *= 0.999

        # 沉积物积累
        for entity, (sediment) in world.get_components(SedimentComponent):
            sediment.sediment += 0.001 * dt

        # 地表物质风化（硬度下降，渗透率上升）
        for entity, (material) in world.get_components(SurfaceMaterialComponent):
            material.hardness = max(0.0, material.hardness - 0.0001 * dt)
            material.permeability = min(1.0, material.permeability + 0.0001 * dt)