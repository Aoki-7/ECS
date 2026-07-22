#!/usr/bin/env python3
"""
风场系统 v4.16.0
实现风场的动态生成、变化，以及大气输送过程
"""

import random
import logging
from typing import Tuple, Dict

from core.system import System
from core.world import World
from core.entity import Entity
from environment.environment_component import EnvironmentComponent
from environment.atmosphere.components.wind_component import WindComponent
from environment.temperature_component import TemperatureComponent
from environment.terrain.components.terrain_component import TerrainComponent
from plant.components.seed_component import SeedComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class WindSystem(System):
    """
    风场系统
    处理风场动态变化与大气输送过程
    """

    tick_interval = 10  # 每10tick执行一次
    priority = 95  # 在温度系统之后，水循环系统之前运行

    # 风场参数
    WIND_CHANGE_RATE = 0.1  # 风速风向每小时最大变化比例
    MIN_WIND_SPEED = 0.1  # 最小风速
    MAX_WIND_SPEED = 30.0  # 最大风速（11级风）
    # 地形影响因子
    OROGRAPHIC_FACTOR = 0.5  # 地形对风速的增强因子，山坡迎风面风速增加
    FRICTION_VELOCITY = 0.3  # 地面摩擦速度
    
    # 输送参数
    SEED_TRANSPORT_PROB = 0.05  # 每小时种子被风吹走的概率
    SPORE_TRANSPORT_PROB = 0.2  # 孢子/花粉输送概率
    HEAT_TRANSPORT_COEFF = 0.01  # 热量输送系数
    VAPOR_TRANSPORT_COEFF = 0.02  # 水汽输送系数

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        if not world_env:
            return
        
        global_temp = world_env.temperature
        pressure_gradient = world_env.pressure_gradient if hasattr(world_env, 'pressure_gradient') else 0.01  # 气压梯度
        
        # 第一步：更新所有网格的风场
        all_grids = list(world.query(WindComponent, TemperatureComponent, TerrainComponent, SpaceComponent))
        pos_map: Dict[Tuple[int, int], Tuple[WindComponent, TemperatureComponent, TerrainComponent]] = {}
        
        for entity, wind, temp, terrain, space in all_grids:
            x, y = round(space.x), round(space.y)
            pos_map[(x, y)] = (wind, temp, terrain)
            
            # 1. 气压梯度力驱动的风
            base_speed = 5.0 * pressure_gradient * (1 + abs(global_temp - 15.0) * 0.05)
            # 温度梯度产生的局地风（海陆风/山谷风）
            temp_gradient = self._get_local_temp_gradient(x, y, pos_map)
            base_speed += temp_gradient * 2.0
            
            # 2. 地形影响
            # 山坡地形风速增强
            if terrain.slope > 0.2:
                base_speed *= 1 + terrain.slope * self.OROGRAPHIC_FACTOR
            # 地形粗糙度影响，植被/建筑多的地方风速降低
            roughness_factor = max(0.3, 1.0 - terrain.roughness * 0.7)
            base_speed *= roughness_factor
            
            # 3. 平滑更新风速，避免突变
            speed_change = random.uniform(-self.WIND_CHANGE_RATE, self.WIND_CHANGE_RATE) * base_speed * dt / 3600.0
            wind.speed = max(self.MIN_WIND_SPEED, min(self.MAX_WIND_SPEED, wind.speed + speed_change))
            
            # 4. 平滑更新风向
            dir_change = random.uniform(-10.0, 10.0) * dt / 3600.0  # 每小时最多变10度
            wind.direction = (wind.direction + dir_change) % 360.0
            
            # 5. 阵风波动
            wind.speed *= 1 + random.uniform(-wind.gust_factor, wind.gust_factor) * 0.1
        
        # 第二步：处理大气输送过程
        # 1. 热量输送
        self._transport_heat(pos_map, dt)
        # 2. 水汽输送
        self._transport_water_vapor(pos_map, dt)
        # 3. 种子/孢子传播
        self._transport_seeds(world, dt)
        # 4. 污染物/气溶胶输送（暂时省略）

    def _get_local_temp_gradient(self, x: int, y: int, pos_map: Dict[Tuple[int, int], Tuple]) -> float:
        """计算局地温度梯度，驱动局地环流"""
        total_diff = 0.0
        count = 0
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if (x, y) in pos_map and (nx, ny) in pos_map:
                _, temp, _ = pos_map[(x, y)]
                _, neighbor_temp, _ = pos_map[(nx, ny)]
                total_diff += temp.surface_temperature - neighbor_temp.surface_temperature
                count += 1
        return total_diff / count if count > 0 else 0.0

    def _transport_heat(self, pos_map: Dict[Tuple[int, int], Tuple], dt: float) -> None:
        """热量平流输送"""
        # 计算每个网格的热量输送
        new_temps = {}
        for (x, y), (wind, temp, terrain) in pos_map.items():
            # 计算上风方向的温度
            u, v = wind.u_component, wind.v_component
            # 上风方向网格
            upwind_x = x - int(round(u * dt / 3600.0 / 100.0))  # 100m/网格
            upwind_y = y - int(round(v * dt / 3600.0 / 100.0))
            
            if (upwind_x, upwind_y) in pos_map:
                _, upwind_temp, _ = pos_map[(upwind_x, upwind_y)]
                # 温度平流：上风温度影响当前温度
                temp_change = (upwind_temp.surface_temperature - temp.surface_temperature) * self.HEAT_TRANSPORT_COEFF * dt / 3600.0
                new_temps[(x, y)] = temp.surface_temperature + temp_change
        
        # 应用温度变化
        for (x, y), new_temp in new_temps.items():
            if (x, y) in pos_map:
                _, temp, _ = pos_map[(x, y)]
                current_temps = temp.temperatures.copy()
                current_temps[0] = new_temp
                temp.update_temperatures(current_temps)

    def _transport_water_vapor(self, pos_map: Dict[Tuple[int, int], Tuple], dt: float) -> None:
        """水汽平流输送，影响降水分布"""
        # 简化处理，后续可扩展到湿度组件
        pass

    def _transport_seeds(self, world: World, dt: float) -> None:
        """输送植物种子和孢子"""
        for entity, seed, space in world.query(SeedComponent, SpaceComponent):
            x, y = round(space.x), round(space.y)
            
            # 查询当前位置的风
            wind = None
            for e, w, s in world.query(WindComponent, SpaceComponent):
                if round(s.x) == x and round(s.y) == y:
                    wind = w
                    break
            if not wind or wind.speed < 2.0:  # 风速小于2m/s不输送种子
                continue
            
            # 小种子更容易被吹走
            transport_prob = self.SEED_TRANSPORT_PROB * (1 - min(1.0, seed.mass / 0.01)) * wind.speed / 5.0 * dt / 3600.0
            if random.random() < transport_prob:
                # 计算输送距离和方向
                transport_dist = wind.get_transport_distance(dt, height=1.0)
                # 转换为网格坐标变化
                dx = wind.u_component * transport_dist / 100.0  # 100m/网格
                dy = wind.v_component * transport_dist / 100.0
                
                # 随机扩散偏移
                dx += random.uniform(-abs(dx)*0.3, abs(dx)*0.3)
                dy += random.uniform(-abs(dy)*0.3, abs(dy)*0.3)
                
                # 更新种子位置
                space.x += dx
                space.y += dy
                seed.dispersed = True
                logger.debug(f"[WindSystem] 种子E{entity.id}被风吹到({space.x:.1f}, {space.y:.1f})")
