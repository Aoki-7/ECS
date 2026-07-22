#!/usr/bin/env python3
"""
土壤侵蚀系统 v4.16.0
实现通用土壤流失方程（USLE）的简化版本，模拟降雨冲刷导致的土壤侵蚀与养分流失
"""

import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from environment.terrain.components.terrain_component import TerrainComponent
from plant.components.plant_component import PlantComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class SoilErosionSystem(System):
    """
    土壤侵蚀系统
    模拟降雨导致的土壤侵蚀、泥沙搬运、养分流失过程
    """

    tick_interval = 50  # 每50tick执行一次，侵蚀是慢过程
    priority = 140  # 在水循环系统之后运行

    # USLE（通用土壤流失方程）参数
    RAINFALL_EROSIVITY_BASE = 0.01  # 降雨侵蚀力基准值
    SOIL_ERODIBILITY = {  # 不同土壤可蚀性因子 K（t·ha·h/(ha·MJ·mm)）
        "sand": 0.05,      # 沙土最不易被侵蚀
        "loam": 0.25,      # 壤土中等
        "clay": 0.3,       # 黏土较高
        "peat": 0.15,      # 泥炭土较低
        "chalk": 0.2,      # 白垩土中等
    }
    # 植被覆盖因子 C：0=完全覆盖（无侵蚀），1=无覆盖（完全侵蚀）
    MAX_C_FACTOR = 1.0
    MIN_C_FACTOR = 0.01
    # 地形因子 LS = (坡度因子) × (坡长因子)，坡度越陡、坡越长侵蚀越严重
    LS_EXPONENT = 0.5  # 坡长指数
    SLOPE_EXPONENT = 1.4  # 坡度指数
    # 侵蚀阈值：每mm降雨最多侵蚀0.1kg土壤
    MAX_EROSION_RATE = 0.1

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        if not world_env:
            return
        
        rainfall = world_env.rainfall  # 降雨强度 mm/h
        if rainfall < 1.0:  # 降雨量小于1mm/h不产生明显侵蚀
            return
        
        # 计算降雨侵蚀力 R = 降雨量 × 动能
        rainfall_amount = rainfall * dt / 3600.0  # 当前时间步降雨量 mm
        R = self.RAINFALL_EROSIVITY_BASE * rainfall_amount * (rainfall * 0.1 + 1.0)  # 降雨强度越大，动能越高
        
        # 存储每个网格的侵蚀泥沙量
        sediment_transport: dict[Tuple[int, int], float] = {}
        
        # 遍历所有网格
        all_grids = list(world.query(SoilComponent, TerrainComponent, SpaceComponent))
        for entity, soil, terrain, space in all_grids:
            x, y = round(space.x), round(space.y)
            
            # 1. 获取土壤可蚀性因子K
            K = self.SOIL_ERODIBILITY.get(soil.soil_type, 0.2)
            
            # 2. 计算地形因子LS
            slope = terrain.slope  # 坡度 0-1（0=水平，1=90度）
            slope_percent = slope * 100  # 转换为百分比坡度
            # 坡长简化为20m（相邻网格距离）
            LS = (20 / 22.13)**self.LS_EXPONENT * (0.065 + 0.045 * slope_percent + 0.0065 * slope_percent**2)**self.SLOPE_EXPONENT
            LS = max(0.1, LS)
            
            # 3. 计算植被覆盖因子C
            C = self._calculate_vegetation_factor(world, x, y)
            
            # 4. 计算支持措施因子P（暂时简化为1，无水土保持措施）
            P = 1.0
            
            # 5. 计算土壤流失量 A = R × K × LS × C × P（USLE方程）
            # 单位转换为 kg/m² 每时间步
            A = R * K * LS * C * P * 0.1  # 转换系数
            A = min(A, self.MAX_EROSION_RATE * rainfall_amount)  # 限制最大侵蚀量
            
            if A > 0.01:  # 侵蚀量大于0.01kg/m²才处理
                # 减少土壤厚度
                soil.thickness = max(0.0, soil.thickness - A * 0.001)  # 1kg土壤≈0.001m厚度（假设容重1t/m³）
                
                # 土壤养分流失
                nutrient_loss_ratio = A / 10.0  # 侵蚀10kg土壤流失1%养分
                soil.nitrogen *= (1 - nutrient_loss_ratio)
                soil.phosphorus *= (1 - nutrient_loss_ratio)
                soil.potassium *= (1 - nutrient_loss_ratio)
                soil.organic_matter *= (1 - nutrient_loss_ratio)
                
                # 记录泥沙量，后续搬运
                sediment_transport[(x, y)] = A * 1.0  # 全部泥沙被径流搬运
            
            # 无侵蚀的网格可能沉积上游的泥沙
            else:
                sediment_transport[(x, y)] = 0.0
        
        # 处理泥沙搬运：从高海拔流向低海拔
        self._process_sediment_transport(sediment_transport, all_grids)

    def _calculate_vegetation_factor(self, world: World, x: float, y: float) -> float:
        """计算指定位置的植被覆盖因子C"""
        # 查询当前位置及周围1格的植物覆盖率
        total_vegetation_cover = 0.0
        count = 0
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # 查找该位置的植物
                for e, plant, s in world.query(PlantComponent, SpaceComponent):
                    if round(s.x) == x + dx and round(s.y) == y + dy:
                        # 植物覆盖率 = 植物大小/最大大小 × 叶面积系数（简化为1）
                        cover = min(1.0, plant.size / plant.max_size) if hasattr(plant, 'size') and hasattr(plant, 'max_size') else 0.3
                        total_vegetation_cover += cover
                        count += 1
        
        if count == 0:
            return self.MAX_C_FACTOR  # 无植被，完全侵蚀
        
        average_cover = total_vegetation_cover / count
        # C因子与覆盖度负相关：覆盖度100%时C=MIN_C_FACTOR，0%时C=MAX_C_FACTOR
        C = self.MAX_C_FACTOR - (self.MAX_C_FACTOR - self.MIN_C_FACTOR) * average_cover
        return max(self.MIN_C_FACTOR, min(self.MAX_C_FACTOR, C))

    def _process_sediment_transport(self, sediment_transport: dict[Tuple[int, int], float], grids) -> None:
        """处理泥沙搬运与沉积"""
        # 构建海拔映射
        elev_map = {}
        pos_map = {}
        for entity, soil, terrain, space in grids:
            x, y = round(space.x), round(space.y)
            elev_map[(x, y)] = terrain.elevation
            pos_map[(x, y)] = soil
        
        # 泥沙搬运迭代
        new_sediment = sediment_transport.copy()
        for (x, y), sediment in sediment_transport.items():
            if sediment <= 0.01:
                continue
            if (x, y) not in elev_map:
                continue
            
            current_elev = elev_map[(x, y)]
            # 寻找最低海拔的邻居（泥沙流向低处）
            min_elev = current_elev
            min_pos = None
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in elev_map and elev_map[(nx, ny)] < min_elev:
                    min_elev = elev_map[(nx, ny)]
                    min_pos = (nx, ny)
            
            # 有更低的邻居则搬运80%的泥沙
            if min_pos is not None and current_elev - min_elev > 0.3:
                transport_amount = sediment * 0.8
                new_sediment[(x, y)] -= transport_amount
                new_sediment[min_pos] = new_sediment.get(min_pos, 0.0) + transport_amount
        
        # 剩余泥沙沉积到当前位置
        for (x, y), sediment in new_sediment.items():
            if sediment <= 0.001:
                continue
            if (x, y) not in pos_map:
                continue
            soil = pos_map[(x, y)]
            # 泥沙沉积增加土壤厚度和养分
            soil.thickness += sediment * 0.001
            soil.nitrogen += sediment * 0.002  # 泥沙携带养分
            soil.phosphorus += sediment * 0.001
            soil.potassium += sediment * 0.0015
            soil.organic_matter += sediment * 0.0005
