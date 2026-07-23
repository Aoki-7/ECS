#!/usr/bin/env python3
"""
微生物生长系统 v4.16.0
处理微生物的种群动态、功能发挥，包括分解、固氮、致病等
"""

import random
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from biology.organisms.microbe.components.microbe_component import MicrobeComponent, MicrobeFunction
from environment.soil.components.soil_component import SoilComponent
from environment.physics_weather.components.temperature_component import TemperatureComponent
from biology.organisms.plant.components.plant_component import PlantComponent

from human.components.health.disease_component import DiseaseComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class MicrobeGrowthSystem(System):
    """
    微生物生长与功能系统
    处理微生物种群动态与生态功能
    """

    tick_interval = 20  # 每20tick执行一次
    priority = 138  # 在养分循环系统之前运行

    # 微生物功能参数
    DECOMPOSITION_BOOST = 0.5  # 分解微生物最高可提升50%的有机质分解速率
    NITROGEN_FIXATION_BOOST = 0.3  # 固氮菌最高可提升30%的固氮速率
    PLANT_DISEASE_CHANCE_BASE = 0.01  # 植物致病菌基础致病概率
    ANIMAL_DISEASE_CHANCE_BASE = 0.005  # 动物致病菌基础致病概率
    MYCORRHIZA_NUTRIENT_BOOST = 0.4  # 菌根真菌可提升40%的植物养分吸收效率

    def update(self, world: World, dt: float):
        # 首先处理土壤中的微生物
        self._process_soil_microbes(world, dt)
        
        # 处理动植物相关的微生物（致病菌、共生菌）
        self._process_host_associated_microbes(world, dt)

    def _process_soil_microbes(self, world: World, dt: float):
        """处理土壤中的微生物种群与功能"""
        for entity, microbe, soil, temp, space in world.query(
            MicrobeComponent,
            SoilComponent,
            TemperatureComponent,
            SpaceComponent
        ):
            # 计算生长因子
            growth_factor = microbe.get_growth_factor(
                temperature=temp.get_average_soil_temperature(0.1),
                moisture=soil.moisture,
                ph=soil.ph
            )
            
            # 计算可利用资源（有机质含量作为碳源）
            resource_available = min(1.0, soil.organic_matter / 10.0)  # 有机质10%以上资源充足
            
            # 更新微生物种群
            microbe.update_population(growth_factor, dt, resource_available)
            
            # 发挥微生物功能
            if microbe.population_size < 1e4:  # 种群数量太少时无明显功能
                continue
            
            population_factor = min(1.0, microbe.population_size / 1e7)  # 种群规模因子
            
            # 1. 分解者功能：加速有机质分解
            if microbe.is_functional(MicrobeFunction.DECOMPOSER):
                decompose_boost = microbe.decomposition_efficiency * self.DECOMPOSITION_BOOST * population_factor
                # 临时提升养分循环系统的分解速率（后续可以通过事件总线通知）
                soil.microbial_activity = max(soil.microbial_activity, decompose_boost)
            
            # 2. 固氮菌功能：增加土壤氮素
            if microbe.is_functional(MicrobeFunction.NITROGEN_FIXER):
                fixation_amount = microbe.nitrogen_fixation_rate * population_factor * microbe.population_size / 1e6 * dt / 3600.0
                soil.nitrogen_ammonium += fixation_amount
                soil._sync_total_nutrients()
            
            # 3. 菌根真菌功能：帮助植物吸收养分
            if microbe.is_functional(MicrobeFunction.MYCORRHIZA):
                # 查找当前位置的植物，提升其养分吸收效率
                for e, plant, s in world.query(PlantComponent, SpaceComponent):
                    if round(s.x) == round(space.x) and round(s.y) == round(space.y):
                        if hasattr(plant, 'nutrient_uptake_efficiency'):
                            plant.nutrient_uptake_efficiency = min(1.0, plant.nutrient_uptake_efficiency + self.MYCORRHIZA_NUTRIENT_BOOST * population_factor)
                        break

    def _process_host_associated_microbes(self, world: World, dt: float):
        """处理与动植物宿主相关的微生物（共生菌、致病菌）"""
        for entity, microbe, space in world.query(MicrobeComponent, SpaceComponent):
            if not microbe.is_functional(MicrobeFunction.PATHOGEN) or microbe.pathogenicity < 0.2:
                continue
            if microbe.population_size < 1e5:
                continue
            
            # 致病菌尝试感染周围的宿主
            population_factor = min(1.0, microbe.population_size / 1e7)
            infection_chance = microbe.pathogenicity * population_factor
            
            # 感染植物
            if random.random() < infection_chance * self.PLANT_DISEASE_CHANCE_BASE * dt / 3600.0:
                for e, plant, s in world.query(PlantComponent, SpaceComponent):
                    distance = ((s.x - space.x)**2 + (s.y - space.y)**2)**0.5
                    if distance < 1.0 and hasattr(plant, 'infect'):
                        plant.infect(disease_type="fungal_blight", severity=0.2 * microbe.pathogenicity)
                        logger.debug(f"[MicrobeSystem] 植物E{e.id}被真菌感染")
                        break
            
            # 感染动物（后续扩展动物健康组件后放开）
            # if random.random() < infection_chance * self.ANIMAL_DISEASE_CHANCE_BASE * dt / 3600.0:
            #     for e, health, s in world.query(AnimalHealthComponent, SpaceComponent):
            #         distance = ((s.x - space.x)**2 + (s.y - space.y)**2)**0.5
            #         if distance < 1.0 and hasattr(health, 'infect'):
            #             health.infect(disease_type="bacterial_infection", severity=0.15 * microbe.pathogenicity)
            #             logger.debug(f"[MicrobeSystem] 动物E{e.id}被细菌感染")
            #             break
            
            # 感染人类
            if random.random() < infection_chance * 0.002 * dt / 3600.0:
                for e, health, s in world.query(DiseaseComponent, SpaceComponent):
                    distance = ((s.x - space.x)**2 + (s.y - space.y)**2)**0.5
                    if distance < 1.0:
                        health.infect("septicemia", severity=0.2 * microbe.pathogenicity)
                        logger.debug(f"[MicrobeSystem] 人类E{e.id}被致病菌感染")
                        break