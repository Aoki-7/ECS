#!/usr/bin/env python3
"""
水循环系统 v4.16.0
实现完整的自然水循环：降雨→下渗→土壤水→地下水→蒸发→径流
"""

import logging
from typing import Tuple, Dict

from core.system import System
from core.world import World
from core.entity import Entity
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from environment.hydrology.components.groundwater_component import GroundwaterComponent
from environment.terrain.components.terrain_component import TerrainComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class WaterCycleSystem(System):
    """
    水循环系统
    处理全局与网格级别的水循环过程
    """

    tick_interval = 10  # 每10tick执行一次
    priority = 100  # 在所有环境相关系统最先运行，为后续系统提供水数据

    # 水循环参数
    MAX_INFILTRATION_RATE = {  # 不同土壤下渗速率（mm/h）
        "sand": 50.0,
        "loam": 10.0,
        "clay": 2.0,
        "peat": 15.0,
        "chalk": 8.0,
    }
    EVAPORATION_FACTOR = 0.05  # 蒸发系数，温度每升高1°C蒸发增加5%
    RUNOFF_THRESHOLD = 0.9  # 土壤饱和度超过此值产生地表径流
    GROUNDWATER_FLOW_RATE = 0.1  # 地下水横向流动速率系数

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        if not world_env:
            return
        
        rainfall = world_env.rainfall  # 降雨强度 mm/h
        temperature = world_env.temperature  # 气温 °C
        solar_radiation = world_env.solar_radiation if hasattr(world_env, 'solar_radiation') else 500.0  # W/m²
        
        # 先处理所有网格的下渗、蒸发
        grid_water: Dict[Tuple[int, int], float] = {}  # 存储每个网格的地表径流量
        all_grids = list(world.query(SoilComponent, GroundwaterComponent, SpaceComponent, TerrainComponent))
        
        for entity, soil, groundwater, space, terrain in all_grids:
            x, y = round(space.x), round(space.y)
            
            # 1. 降雨阶段
            total_water = rainfall * dt / 3600.0  # 转换为当前时间步的降雨量 mm
            
            # 2. 下渗阶段
            infiltration_rate = self.MAX_INFILTRATION_RATE.get(soil.soil_type, 10.0)
            max_infiltration = infiltration_rate * dt / 3600.0
            
            # 先填充土壤水分
            soil_available_space = (soil.saturation - soil.moisture) * 1000  # 转换为mm（1体积含水量=1mm水深）
            actual_infiltration_soil = min(total_water, max_infiltration, soil_available_space)
            soil.moisture += actual_infiltration_soil / 1000.0  # 转换回体积含水量
            remaining_water = total_water - actual_infiltration_soil
            
            # 剩余下渗补给地下水
            if remaining_water > 0:
                max_infiltration_gw = max_infiltration - actual_infiltration_soil
                actual_infiltration_gw = min(remaining_water, max_infiltration_gw)
                gw_overflow = groundwater.add_water(actual_infiltration_gw)
                remaining_water = remaining_water - actual_infiltration_gw + gw_overflow
            
            # 3. 地表径流
            if remaining_water > 0 or soil.moisture >= self.RUNOFF_THRESHOLD:
                runoff_amount = remaining_water + max(0.0, (soil.moisture - self.RUNOFF_THRESHOLD) * 1000)
                grid_water[(x, y)] = runoff_amount
                # 径流多的地方生成临时水源
                if runoff_amount > 5.0:
                    from resource.water.water_factory import WaterFactory
                    if not hasattr(self, '_water_factory'):
                        self._water_factory = WaterFactory()
                    # 10%概率生成水坑
                    import random
                    if random.random() < 0.1:
                        self._water_factory.create_water(world, x=x, y=y, amount=min(runoff_amount / 2, 10.0))
            
            # 4. 蒸发阶段
            # 潜在蒸发量（mm/h），基于彭曼公式简化
            potential_evap = (0.002 * (temperature + 17.8) * solar_radiation / 1000.0) * self.EVAPORATION_FACTOR
            actual_evap = potential_evap * dt / 3600.0
            
            # 先蒸发土壤水分
            evap_from_soil = min(actual_evap, soil.moisture * 1000.0 * 0.5)
            soil.moisture -= evap_from_soil / 1000.0
            remaining_evap = actual_evap - evap_from_soil
            
            # 剩余蒸发消耗地下水（毛管上升）
            if remaining_evap > 0 and groundwater.water_table_depth < 2.0:
                evap_from_gw = min(remaining_evap, groundwater.get_available_water() * 0.1)
                groundwater.remove_water(evap_from_gw)
        
        # 5. 地下水横向流动（从高水位流向低水位）
        self._process_groundwater_flow(all_grids, dt)
        
        # 6. 地表径流流动（从高海拔流向低海拔）
        self._process_surface_runoff(grid_water, all_grids, dt)

    def _process_groundwater_flow(self, grids, dt: float) -> None:
        """处理地下水横向流动"""
        # 构建位置到组件的映射
        pos_map = {}
        for entity, soil, gw, space, terrain in grids:
            x, y = round(space.x), round(space.y)
            pos_map[(x, y)] = (gw, terrain.elevation)
        
        # 遍历每个网格，与四个邻居比较水位
        for (x, y), (gw, elev) in pos_map.items():
            total_outflow = 0.0
            # 检查四个方向邻居
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in pos_map:
                    continue
                neighbor_gw, neighbor_elev = pos_map[(nx, ny)]
                # 水位 = 海拔 - 地下水埋深
                water_level = elev - gw.water_table_depth
                neighbor_water_level = neighbor_elev - neighbor_gw.water_table_depth
                
                # 水位差大于0.1m时流动
                if water_level - neighbor_water_level > 0.1:
                    flow_amount = (water_level - neighbor_water_level) * gw.hydraulic_conductivity * self.GROUNDWATER_FLOW_RATE * dt / 3600.0
                    flow_amount = min(flow_amount, gw.get_available_water() * 0.1)
                    
                    # 转移水量
                    gw.remove_water(flow_amount)
                    neighbor_gw.add_water(flow_amount)
                    total_outflow += flow_amount

    def _process_surface_runoff(self, grid_water: Dict[Tuple[int, int], float], grids, dt: float) -> None:
        """处理地表径流流动"""
        # 构建海拔映射
        elev_map = {}
        for entity, soil, gw, space, terrain in grids:
            x, y = round(space.x), round(space.y)
            elev_map[(x, y)] = terrain.elevation
        
        # 径流迭代流动
        new_grid_water = grid_water.copy()
        for (x, y), amount in grid_water.items():
            if amount <= 0:
                continue
            if (x, y) not in elev_map:
                continue
            
            current_elev = elev_map[(x, y)]
            # 寻找最低海拔的邻居
            min_elev = current_elev
            min_pos = None
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in elev_map and elev_map[(nx, ny)] < min_elev:
                    min_elev = elev_map[(nx, ny)]
                    min_pos = (nx, ny)
            
            # 有更低的邻居则流动30%的水量
            if min_pos is not None and current_elev - min_elev > 0.5:
                flow_amount = amount * 0.3
                new_grid_water[(x, y)] -= flow_amount
                new_grid_water[min_pos] = new_grid_water.get(min_pos, 0.0) + flow_amount
        
        # 最终剩余的径流补充到低洼处的地下水或形成水坑
        for (x, y), amount in new_grid_water.items():
            if amount < 1.0:
                continue
            # 查找对应网格
            for entity, soil, gw, space, terrain in grids:
                if round(space.x) == x and round(space.y) == y:
                    # 50%下渗到土壤，50%下渗到地下水
                    soil.moisture = min(soil.saturation, soil.moisture + amount * 0.5 / 1000)
                    gw.add_water(amount * 0.5)
                    break
