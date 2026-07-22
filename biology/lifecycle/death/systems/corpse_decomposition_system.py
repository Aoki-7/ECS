#!/usr/bin/env python3
"""
尸体分解系统 v4.16.0
处理尸体的自然分解过程，释放养分到土壤，完善生态物质循环
"""

import random
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from biology.components.corpse_component import CorpseComponent, DecompositionStage
from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent

logger = logging.getLogger(__name__)


class CorpseDecompositionSystem(System):
    """
    尸体分解系统
    处理所有尸体实体的分解过程，释放养分到对应位置的土壤
    """

    tick_interval = 10  # 每10tick执行一次
    priority = 130  # 在死亡系统之后，植物生长系统之前运行

    # 环境影响系数
    TEMPERATURE_OPTIMAL = 25.0  # 最适分解温度（°C）
    MOISTURE_OPTIMAL = 0.6  # 最适分解湿度（0-1）
    MAX_TEMPERATURE_EFFECT = 2.0  # 温度最大影响系数
    MAX_MOISTURE_EFFECT = 2.0  # 湿度最大影响系数

    def update(self, world: World, dt: float):
        # 获取全局环境参数
        world_env = world.get_world_component(EnvironmentComponent)
        global_temp = world_env.temperature if world_env else 20.0
        global_rain = world_env.rainfall if world_env else 0.0

        # 遍历所有尸体实体
        for entity, corpse, space in world.query(CorpseComponent, SpaceComponent):
            # 获取尸体所在位置的土壤
            soil = self._get_soil_at_position(world, space.x, space.y)
            if not soil:
                # 没有土壤的位置（如水面、岩石）分解速率减半
                env_factor = 0.5
            else:
                # 计算环境综合因子
                temp_factor = self._calculate_temperature_factor(global_temp)
                moisture_factor = self._calculate_moisture_factor(soil.moisture + global_rain * 0.01)
                env_factor = temp_factor * moisture_factor
            
            # 执行分解
            released_nutrients = corpse.decompose(dt, env_factor)
            
            # 将养分添加到土壤
            if soil:
                soil.nitrogen += released_nutrients.get("nitrogen", 0) * 1000  # 转换为mg/kg
                soil.phosphorus += released_nutrients.get("phosphorus", 0) * 1000
                soil.potassium += released_nutrients.get("potassium", 0) * 1000
                soil.organic_matter = min(100.0, soil.organic_matter + released_nutrients.get("carbon", 0) * 0.1)
            
            # 完全分解后销毁尸体实体
            if corpse.is_fully_decomposed():
                world.remove_entity(entity)
                logger.debug(f"[CorpseDecomposition] 尸体E{entity.id}已完全分解")
                continue
            
            # 活跃腐烂阶段有概率传播疾病
            if corpse.decomposition_stage == DecompositionStage.ACTIVE_DECAY and corpse.toxic_level > 0.3:
                self._spread_disease(world, entity, space, corpse)

    def _get_soil_at_position(self, world: World, x: float, y: float) -> SoilComponent:
        """获取指定位置的土壤组件"""
        # 空间查询当前位置的土壤实体
        for e, soil, s in world.query(SoilComponent, SpaceComponent):
            if round(s.x) == round(x) and round(s.y) == round(y):
                return soil
        return None

    def _calculate_temperature_factor(self, temperature: float) -> float:
        """计算温度对分解速率的影响"""
        # 温度响应曲线：0°C以下几乎不分解，25°C最优，超过40°C开始下降
        if temperature <= 0:
            return 0.01
        if temperature >= 40:
            return max(0.1, 1.0 - (temperature - 40) * 0.05)
        
        # 0~25°C线性增长到最优值
        if temperature <= self.TEMPERATURE_OPTIMAL:
            return 0.01 + (self.MAX_TEMPERATURE_EFFECT - 0.01) * (temperature / self.TEMPERATURE_OPTIMAL)
        # 25~40°C线性下降
        else:
            return self.MAX_TEMPERATURE_EFFECT - (self.MAX_TEMPERATURE_EFFECT - 0.1) * ((temperature - self.TEMPERATURE_OPTIMAL) / (40 - self.TEMPERATURE_OPTIMAL))

    def _calculate_moisture_factor(self, moisture: float) -> float:
        """计算湿度对分解速率的影响"""
        moisture = max(0.0, min(1.0, moisture))
        # 湿度响应曲线：0湿度几乎不分解，0.6最优，超过0.8开始下降（缺氧）
        if moisture < 0.1:
            return 0.05 + moisture * 2
        
        if moisture <= self.MOISTURE_OPTIMAL:
            return 0.25 + (self.MAX_MOISTURE_EFFECT - 0.25) * ((moisture - 0.1) / (self.MOISTURE_OPTIMAL - 0.1))
        elif moisture <= 0.8:
            return self.MAX_MOISTURE_EFFECT
        else:
            return self.MAX_MOISTURE_EFFECT - (self.MAX_MOISTURE_EFFECT - 0.3) * ((moisture - 0.8) / 0.2)

    def _spread_disease(self, world: World, corpse_entity: Entity, space: SpaceComponent, corpse: CorpseComponent) -> None:
        """腐烂尸体传播疾病"""
        # 周围3格范围内的人类/动物有概率感染疾病
        from human.components.health.disease_component import DiseaseComponent
        from animal.components.animal_health_component import AnimalHealthComponent
        
        infection_radius = 3.0
        infection_chance = 0.05 * corpse.toxic_level
        
        for e, health, s in world.query(DiseaseComponent, SpaceComponent):
            distance = ((s.x - space.x)**2 + (s.y - space.y)**2)**0.5
            if distance <= infection_radius and hasattr(health, 'infect'):
                if random.random() < infection_chance:
                    health.infect("septicemia", severity=0.3 + corpse.toxic_level * 0.4)
                    logger.debug(f"[CorpseDecomposition] E{e.id}因接触腐烂尸体感染败血症")
        
        # 动物同理
        for e, health, s in world.query(AnimalHealthComponent, SpaceComponent):
            distance = ((s.x - space.x)**2 + (s.y - space.y)**2)**0.5
            if distance <= infection_radius and hasattr(health, 'infect'):
                if random.random() < infection_chance:
                    health.infect("septicemia", severity=0.3 + corpse.toxic_level * 0.4)
