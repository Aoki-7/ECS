

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:soil_fertility_system.py
@说明:肥力变化，肥力变化通常比较缓慢
@时间:2026/03/09 09:43:25
@作者:Sherry
@版本:1.0
'''

from environment.soil.components.soil_fertility_component import SoilFertilityComponent

from core.world import World
from core.system import System


class SoilFertilitySystem(System):
    tick_interval = 2  # 每2帧执行一次
    """
        土壤肥力系统
        负责：
        - 肥力变化
    """
    def update(self, world: World, delta_hours: float):

        soil = world.get_world_entity().get_component(SoilFertilityComponent)
        soil: SoilFertilityComponent

        # 自然恢复（非常缓慢）
        soil.fertility += 0.00001 * delta_hours

        soil.fertility = min(1.0, soil.fertility)