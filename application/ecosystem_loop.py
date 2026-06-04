#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯生态系统模拟入口

构建一个仅包含植物、动物、微生物（分解者）的简化生态系统，
不含人类、文明、建筑等复杂元素。

生态闭环：
    植物（光合作用）→ 食草动物（啃食）→ 食肉动物（捕食）→ 尸体 → 分解者 → 土壤养分 → 植物
"""

import random
import sys
import logging

# 修复 Windows 终端中文乱码
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from core.world import World
from core.components.world_config_component import WorldConfigComponent
from world.world_entity import WorldEntity
from time_module.time_component import TimeComponent

from space.space_system import SpaceSystem
from time_module.time_system import TimeSystem
from core.systems.event_log_system import EventLogSystem

from environment.config.environment_builder import EnvironmentBuilder
from environment.atmosphere.system.atmosphere_physics_system import AtmospherePhysicsSystem



from plant.plant_factory import PlantFactory
from plant.systems.photosynthesis_system import PlantPhotosynthesisSystem
from plant.systems.water_uptake_system import PlantWaterUptakeSystem
from plant.systems.seed_dispersal_system import SeedDispersalSystem
from plant.systems.terrain_adaptation_system import TerrainAdaptationSystem

from animal.animal_factory import AnimalFactory
from animal.systems.grazing_system import GrazingSystem
from animal.systems.predation_system import PredationSystem
from animal.systems.animal_reproduction_system import AnimalReproductionSystem

from biology.systems.gene_expression_system import GeneExpressionSystem
from biology.systems.competition_system import CompetitionSystem
from biology.lifecycle.growth.systems.growth_system import GrowthSystem
from biology.lifecycle.growth.systems.morphology_system import MorphologySystem
from biology.systems.nutrient_system import NutrientSystem
from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
from biology.lifecycle.aging.systems.senescence_system import SenescenceSystem
from biology.systems.damage_repair_system import DamageRepairSystem
from biology.systems.mutation_system import MutationSystem
from biology.lifecycle.birth.systems.reproduction_system import BiologyReproductionSystem
from biology.systems.immune_system import ImmuneSystem
from biology.lifecycle.death.systems.creature_death_trigger_system import CreatureDeathTriggerSystem
from biology.lifecycle.death.systems.death_system import DeathSystem
from biology.lifecycle.death.systems.death_event_system import DeathEventSystem
from biology.lifecycle.corpse.systems.corpse_system import CorpseSystem

from biology.ecology.decomposer_system import DecomposerSystem
from biology.ecology.trophic_level_system import TrophicLevelSystem
from biology.ecology.population_dynamics_system import PopulationDynamicsSystem
from biology.ecology.ecology_balance_system import EcologyBalanceSystem

from environment.soil.components.soil_component import SoilComponent
from space.space_component import SpaceComponent
from plant.components.plant_component import PlantComponent
from animal.components.animal_component import AnimalComponent


class EcosystemLoop:
    """
    纯生态系统模拟循环

    职责：
        1. 初始化 World 和所有生态系统相关的 System
        2. 创建初始种群（植物 + 食草动物 + 食肉动物 + 土壤网格）
        3. 执行模拟循环并输出统计
    """

    def __init__(self, world: World):
        self.world = world

        # 初始化世界实体
        world_entity = WorldEntity()
        world_entity.add_component(TimeComponent())
        world_entity.add_component(WorldConfigComponent(map_width=100, map_height=100))
        self.world.set_world_entity(world_entity)

        # 注册空间系统
        self.space_system = SpaceSystem()
        self.world.add_system(self.space_system)

        self._init_systems()

        # 统计信息
        self.step_count = 0
        self.stats_history = []

    def _init_systems(self):
        """初始化所有生态系统相关的系统，按 priority 排序注册"""

        # 1. 时间系统（priority 5）
        self.time_system = TimeSystem()
        self.time_system.priority = 5
        self.world.add_system(self.time_system)

        # 1.5 事件日志系统（priority 5）
        self.event_log_system = EventLogSystem()
        self.event_log_system.priority = 5
        self.world.add_system(self.event_log_system)

        # 2. 环境管线（priority 20）
        self.env_pipeline = EnvironmentBuilder.build(self.world)
        self.env_pipeline.priority = 20
        self.world.add_system(self.env_pipeline)

        # 2.5 大气物理系统（priority 20）
        self.atmosphere_physics_system = AtmospherePhysicsSystem()
        self.atmosphere_physics_system.priority = 20
        self.world.add_system(self.atmosphere_physics_system)

        # 3. 动物行为系统（priority 40）
        self.grazing_system = GrazingSystem()
        self.grazing_system.priority = 40
        self.world.add_system(self.grazing_system)

        self.animal_reproduction_system = AnimalReproductionSystem(seed=123)
        self.animal_reproduction_system.priority = 40
        self.world.add_system(self.animal_reproduction_system)

        # 4. 捕食系统（priority 45）
        self.predation_system = PredationSystem(seed=456)
        self.predation_system.priority = 45
        self.world.add_system(self.predation_system)

        # 5. 植物准备系统（priority 48）
        self.plant_systems = [
            PlantPhotosynthesisSystem(),
            PlantWaterUptakeSystem(),
            TerrainAdaptationSystem(),
        ]
        for system in self.plant_systems:
            system.priority = 48
            self.world.add_system(system)

        # 6. 生物学核心系统（priority 50）
        self.biology_systems = [
            GeneExpressionSystem(),
            CompetitionSystem(),
            GrowthSystem(),
            MorphologySystem(),
            NutrientSystem(),
            LifeCycleSystem(),
            SenescenceSystem(),
            DamageRepairSystem(),
            MutationSystem(),
            BiologyReproductionSystem(),
            SeedDispersalSystem(),
            ImmuneSystem(),
            CreatureDeathTriggerSystem(),
            DeathSystem(),
            DeathEventSystem(),
            CorpseSystem(),
        ]
        for system in self.biology_systems:
            system.priority = 50
            self.world.add_system(system)

        # 7. 微生物分解系统（priority 55）
        self.decomposer_system = DecomposerSystem()
        self.decomposer_system.priority = 55
        self.world.add_system(self.decomposer_system)

        # 8. 食物链营养级系统（priority 58）
        self.trophic_level_system = TrophicLevelSystem()
        self.trophic_level_system.priority = 58
        self.world.add_system(self.trophic_level_system)

        # 9. 种群动态系统（priority 59）
        self.population_dynamics_system = PopulationDynamicsSystem()
        self.population_dynamics_system.priority = 59
        self.world.add_system(self.population_dynamics_system)

        # 10. 生态平衡监控系统（priority 60）
        self.ecology_balance_system = EcologyBalanceSystem()
        self.ecology_balance_system.priority = 60
        self.world.add_system(self.ecology_balance_system)

    def create_initial_population(
        self,
        plant_count: int = 80,
        herbivore_count: int = 15,
        carnivore_count: int = 5,
    ):
        """
        创建初始种群和土壤网格

        Args:
            plant_count: 初始植物数量
            herbivore_count: 初始食草动物数量
            carnivore_count: 初始食肉动物数量
        """
        logger.info(
            f"[Init] 创建初始种群: {plant_count} 植物, "
            f"{herbivore_count} 食草动物, {carnivore_count} 食肉动物"
        )

        # 1. 创建土壤网格（10x10 网格覆盖 100x100 地图）
        self._create_soil_grid()

        # 2. 创建植物（多物种混合，含新模板）
        plant_species = [
            "basic", "fast", "tree", "cold_resistant", "drought_resistant",
            "pine", "flower", "fern", "shade_tolerant", "succulent", "vine",
        ]
        for i in range(plant_count):
            species = random.choice(plant_species)
            x = random.randint(5, 95)
            y = random.randint(5, 95)
            PlantFactory.create_plant(self.world, species=species, x=x, y=y)

        # 3. 创建食草动物
        for i in range(herbivore_count):
            x = random.randint(5, 95)
            y = random.randint(5, 95)
            entity = AnimalFactory.create_animal(
                self.world, species="herbivore", x=x, y=y
            )
            # 强制推进到成年期，避免初始种群全是幼体
            from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
            lifecycle = self.world.get_component(entity, LifeCycleComponent)
            lifecycle.set_stage(LifeCycleComponent.MATURE)
            # 设置足够能量
            from biology.lifecycle.components.energy_component import EnergyComponent
            energy = self.world.get_component(entity, EnergyComponent)
            energy.value = 80.0

        # 4. 创建食肉动物
        for i in range(carnivore_count):
            x = random.randint(5, 95)
            y = random.randint(5, 95)
            entity = AnimalFactory.create_animal(
                self.world, species="predator", x=x, y=y
            )

            # 强制推进到成年期
            from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
            lifecycle = self.world.get_component(entity, LifeCycleComponent)
            lifecycle.set_stage(LifeCycleComponent.MATURE)
            # 设置足够能量
            from biology.lifecycle.components.energy_component import EnergyComponent
            energy = self.world.get_component(entity, EnergyComponent)
            energy.value = 80.0

        logger.info("[Init] 初始种群创建完成")

    def _create_soil_grid(self):
        """创建覆盖全地图的土壤网格（10x10 网格）"""
        for gx in range(10):
            for gy in range(10):
                soil_entity = self.world.create_entity()
                # 每个土壤实体位于网格中心
                x = gx * 10 + 5
                y = gy * 10 + 5
                self.world.add_component(soil_entity, SpaceComponent(x=x, y=y, layer=0))
                self.world.add_component(soil_entity, SoilComponent(
                    moisture=random.uniform(0.3, 0.6),
                    nitrogen=random.uniform(40.0, 60.0),
                    phosphorus=random.uniform(15.0, 25.0),
                    potassium=random.uniform(50.0, 70.0),
                    organic_matter=random.uniform(1.5, 3.0),
                ))

    def run_simulation(self, steps: int = 100, delta_hours: float = 1.0,
                       report_interval: int = 10):
        """
        运行模拟循环

        Args:
            steps: 总模拟步数
            delta_hours: 每步时间增量（小时）
            report_interval: 统计报告间隔（步数）
        """
        logger.info(f"[Run] 开始模拟: {steps} 步, dt={delta_hours}h")

        for step in range(steps):
            self.world.update(delta_hours)
            self.step_count += 1

            if (step + 1) % report_interval == 0:
                self._print_stats(step + 1)

        logger.info("[Run] 模拟结束")
        self._print_final_summary()

    def _print_stats(self, step: int):
        """打印当前步数的统计数据"""
        stats = self._collect_stats()
        self.stats_history.append(stats)

        logger.info(
            f"[Step {step:4d}] "
            f"植物={stats['plants']:3d} "
            f"食草动物={stats['herbivores']:2d} "
            f"食肉动物={stats['carnivores']:2d} "
            f"尸体={stats['corpses']:2d} "
            f"总实体={stats['total_entities']:3d} | "
            f"土壤氮={stats['soil_nitrogen']:6.1f} "
            f"磷={stats['soil_phosphorus']:5.1f} "
            f"钾={stats['soil_potassium']:5.1f}"
        )

    def _collect_stats(self) -> dict:
        """收集当前世界状态的统计信息"""
        plants = 0
        herbivores = 0
        carnivores = 0
        corpses = 0
        total_entities = len(self.world.entities)

        total_soil_n = 0.0
        total_soil_p = 0.0
        total_soil_k = 0.0
        soil_count = 0

        for entity_id in self.world.entities:
            entity = self.world.query_entity(entity_id)
            if entity is None:
                continue

            # 植物
            if self.world.get_component(entity, PlantComponent) is not None:
                plants += 1
                continue

            # 动物
            animal = self.world.get_component(entity, AnimalComponent)
            if animal is not None:
                if animal.diet == "carnivore":
                    carnivores += 1
                else:
                    herbivores += 1
                continue

            # 尸体（通过 CorpseComponent 判断）
            from biology.lifecycle.corpse.components.corpse_component import CorpseComponent
            if self.world.get_component(entity, CorpseComponent) is not None:
                corpses += 1
                continue

            # 土壤
            soil = self.world.get_component(entity, SoilComponent)
            if soil is not None:
                total_soil_n += soil.nitrogen
                total_soil_p += soil.phosphorus
                total_soil_k += soil.potassium
                soil_count += 1

        return {
            "plants": plants,
            "herbivores": herbivores,
            "carnivores": carnivores,
            "corpses": corpses,
            "total_entities": total_entities,
            "soil_nitrogen": total_soil_n / max(soil_count, 1),
            "soil_phosphorus": total_soil_p / max(soil_count, 1),
            "soil_potassium": total_soil_k / max(soil_count, 1),
        }

    def _print_final_summary(self):
        """打印模拟结束后的汇总统计"""
        if not self.stats_history:
            return

        first = self.stats_history[0]
        last = self.stats_history[-1]

        logger.info("=" * 60)
        logger.info("生态系统模拟汇总")
        logger.info("=" * 60)
        logger.info(f"植物:     {first['plants']:3d} → {last['plants']:3d} "
                    f"({'+' if last['plants'] >= first['plants'] else ''}{last['plants'] - first['plants']})")
        logger.info(f"食草动物: {first['herbivores']:3d} → {last['herbivores']:3d} "
                    f"({'+' if last['herbivores'] >= first['herbivores'] else ''}{last['herbivores'] - first['herbivores']})")
        logger.info(f"食肉动物: {first['carnivores']:3d} → {last['carnivores']:3d} "
                    f"({'+' if last['carnivores'] >= first['carnivores'] else ''}{last['carnivores'] - first['carnivores']})")
        logger.info(f"总实体:   {first['total_entities']:3d} → {last['total_entities']:3d}")
        logger.info("=" * 60)
