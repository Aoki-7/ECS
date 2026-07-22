#!/usr/bin/env python3
"""
植物生长系统 v4.16.0
基于真实土壤参数（湿度、养分、温度）的植物生长逻辑，完善生态闭环
"""

import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from plant.components.plant_component import PlantComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from environment.soil.components.soil_component import SoilComponent
from environment.environment_component import EnvironmentComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class PlantGrowthSystem(System):
    """
    植物生长系统
    根据土壤条件、环境温度、光照计算植物真实生长速率
    """

    tick_interval = 5  # 每5tick执行一次
    priority = 125  # 在水分吸收、光合作用系统之后，掉落系统之前运行

    # 生长参数
    BASE_GROWTH_RATE = 0.01  # 基础生长速率每小时
    MIN_TEMP_FOR_GROWTH = 5.0  # 最低生长温度（°C）
    OPTIMAL_TEMP = 25.0  # 最适生长温度
    MAX_TEMP_FOR_GROWTH = 40.0  # 最高生长温度
    MIN_MOISTURE = 0.2  # 最低生长湿度
    OPTIMAL_MOISTURE = 0.6  # 最适生长湿度
    NUTRIENT_STRESS_THRESHOLD = 30.0  # 养分胁迫阈值（mg/kg 氮）

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        global_temp = world_env.temperature if world_env else 20.0
        global_light = world_env.sun_altitude if world_env else 0.5  # 太阳高度作为光照强度 0-1

        # 遍历所有生长中的植物
        for entity, plant, lc, space in world.query(PlantComponent, LifeCycleComponent, SpaceComponent):
            # 死亡植物不再生长
            if lc.stage == LifeCycleComponent.DEAD:
                continue
            
            # 获取植物所在位置的土壤
            soil = self._get_soil_at_position(world, space.x, space.y)
            if not soil:
                # 没有土壤的地方植物生长停滞
                continue
            
            # 计算各生长限制因子
            temp_factor = self._calculate_temperature_factor(global_temp)
            moisture_factor = self._calculate_moisture_factor(soil.moisture)
            nutrient_factor = self._calculate_nutrient_factor(soil.nitrogen, soil.phosphorus, soil.potassium)
            light_factor = max(0.0, global_light)  # 夜间光照为0，生长停滞
            
            # 总生长速率 = 基础速率 × 各因子乘积（最小因子定律：最低的因子决定上限）
            total_factor = min(temp_factor, moisture_factor, nutrient_factor, light_factor)
            actual_growth_rate = self.BASE_GROWTH_RATE * total_factor * dt
            
            # 应用生长到生命周期
            if hasattr(lc, 'growth_progress'):
                lc.growth_progress = min(1.0, lc.growth_progress + actual_growth_rate)
                # 更新植物大小
                if hasattr(plant, 'size'):
                    plant.size = max(0.1, lc.growth_progress * plant.max_size)
            
            # 消耗土壤养分和水分
            if total_factor > 0.1:  # 只有生长时才消耗
                # 消耗水分
                soil.moisture = max(0.0, soil.moisture - actual_growth_rate * 0.02)
                # 消耗养分
                soil.nitrogen = max(0.0, soil.nitrogen - actual_growth_rate * 2.0)
                soil.phosphorus = max(0.0, soil.phosphorus - actual_growth_rate * 0.8)
                soil.potassium = max(0.0, soil.potassium - actual_growth_rate * 1.2)
            
            # 生长到100%进入成熟期
            if lc.growth_progress >= 1.0 and lc.stage < 3:  # 3 = MATURE
                lc.stage = 3
                logger.debug(f"[PlantGrowth] 植物E{entity.id}成熟")

    def _get_soil_at_position(self, world: World, x: float, y: float) -> SoilComponent:
        """获取指定位置的土壤组件"""
        for e, soil, s in world.query(SoilComponent, SpaceComponent):
            if round(s.x) == round(x) and round(s.y) == round(y):
                return soil
        return None

    def _calculate_temperature_factor(self, temperature: float) -> float:
        """计算温度对生长的影响"""
        if temperature < self.MIN_TEMP_FOR_GROWTH or temperature > self.MAX_TEMP_FOR_GROWTH:
            return 0.0
        if temperature <= self.OPTIMAL_TEMP:
            return (temperature - self.MIN_TEMP_FOR_GROWTH) / (self.OPTIMAL_TEMP - self.MIN_TEMP_FOR_GROWTH)
        else:
            return 1.0 - (temperature - self.OPTIMAL_TEMP) / (self.MAX_TEMP_FOR_GROWTH - self.OPTIMAL_TEMP)

    def _calculate_moisture_factor(self, moisture: float) -> float:
        """计算湿度对生长的影响"""
        if moisture < self.MIN_MOISTURE:
            return 0.0
        if moisture <= self.OPTIMAL_MOISTURE:
            return (moisture - self.MIN_MOISTURE) / (self.OPTIMAL_MOISTURE - self.MIN_MOISTURE)
        else:
            # 水分过多会导致缺氧，生长下降
            return max(0.3, 1.0 - (moisture - self.OPTIMAL_MOISTURE) / (1.0 - self.OPTIMAL_MOISTURE) * 0.7)

    def _calculate_nutrient_factor(self, nitrogen: float, phosphorus: float, potassium: float) -> float:
        """计算养分对生长的影响（最小养分律）"""
        # 分别计算各养分的满足度
        n_factor = min(1.0, nitrogen / 100.0)  # 100mg/kg氮为充足
        p_factor = min(1.0, phosphorus / 50.0)  # 50mg/kg磷为充足
        k_factor = min(1.0, potassium / 80.0)  # 80mg/kg钾为充足
        
        # 最小的养分决定生长上限
        return min(n_factor, p_factor, k_factor)
