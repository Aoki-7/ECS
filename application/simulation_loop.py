#!/usr/bin/env python3
"""
统一模拟主循环

该脚本整合所有系统：
- 时间系统：驱动时间推进
- 空间系统：同步实体位置
- 环境系统：天气、季节、气候等
- 人类系统：生理、认知、社交、生存等
- 生物学系统：生长、死亡、繁衍等
- 规则系统：文明演进规则

运行方式：
    python main.py
"""

from __future__ import annotations

import time
import random
import sys
import logging

# 修复 Windows 终端中文乱码
sys.stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from core.world import World

# 空间系统
from space.space_system import SpaceSystem
from space.collision_system import CollisionSystem

# 时间系统
from time_module.time_system import TimeSystem

# 环境系统
from environment.config.environment_builder import EnvironmentBuilder

# 人类系统
from human.systems.social.social_system import SocialSystem
from human.systems.social.pairing_system import PairingSystem
from human.systems.social.reproduction_system import ReproductionSystem
from human.systems.social.birth_system import BirthSystem
from human.systems.social.tribe_system import TribeSystem
from human.systems.social.territory_system import TerritorySystem
from human.systems.social.leadership_system import LeadershipSystem
from human.systems.social.loyalty_system import LoyaltySystem
from human.systems.social.recruit_system import RecruitSystem
from human.systems.cognitive.decision_system import DecisionSystem
from human.systems.cognitive.perception_system import PerceptionSystem
from human.systems.cognitive.emotion_system import EmotionSystem
from human.systems.cognitive.thought_system import ThoughtSystem
from human.systems.cognitive.goal_system import GoalSystem
from human.systems.core.intent_system import IntentSystem
from human.systems.core.planning_system import PlanningSystem
from human.systems.core.action_system import ActionSystem
from human.systems.action.movement_system import MovementSystem
from human.systems.action.eat_system import EatSystem
from human.systems.action.drink_system import DrinkSystem
from human.systems.action.sleep_system import SleepSystem
from human.systems.action.pickup_system import PickupSystem
from human.systems.action.search_system import SearchSystem
from human.systems.action.socialize_system import SocializeSystem
from human.systems.action.harvest_system import HarvestSystem
from human.systems.action.planting_system import PlantingSystem

# 环境效果系统（已拆分为5个独立系统）
from human.systems.environment.heat_effect_system import HeatEffectSystem
from human.systems.environment.cold_effect_system import ColdEffectSystem
from human.systems.environment.rain_effect_system import RainEffectSystem
from human.systems.environment.wind_effect_system import WindEffectSystem
from human.systems.environment.humidity_effect_system import HumidityEffectSystem

# 导航与认知
from human.systems.navigation.pathfinding_system import PathfindingSystem
from human.systems.cognitive.memory_decay_system import MemoryDecaySystem

# 社交扩展
from human.systems.social.reputation_system import ReputationSystem

# 冲突管理（已拆分）
from human.systems.interaction.conflict_detection_system import ConflictDetectionSystem
from human.systems.interaction.conflict_resolution_system import ConflictResolutionSystem

# 生理系统（拆分后）
from human.systems.physiological.physiology_needs_system import PhysiologyNeedsSystem
from human.systems.physiological.health_system import HealthSystem
from biology.lifecycle.death.systems.human_death_trigger_system import HumanDeathTriggerSystem

# 疾病与医疗
from human.systems.health.disease_spread_system import DiseaseSpreadSystem
from human.systems.health.healthcare_system import HealthcareSystem

# 战斗系统
from human.systems.combat.combat_system import CombatSystem
from human.systems.combat.combat_ai_system import CombatAISystem

# 对话与冲突
from human.systems.interaction.dialogue_system import DialogueSystem

# 生物学系统
from biology.systems.gene_expression_system import GeneExpressionSystem
from biology.lifecycle.growth.systems.growth_system import GrowthSystem
from biology.lifecycle.growth.systems.morphology_system import MorphologySystem
from biology.lifecycle.death.systems.creature_death_trigger_system import CreatureDeathTriggerSystem
from biology.lifecycle.death.systems.death_system import DeathSystem
from biology.lifecycle.death.systems.death_event_system import DeathEventSystem
from biology.lifecycle.corpse.systems.corpse_system import CorpseSystem
from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
from biology.lifecycle.aging.systems.senescence_system import SenescenceSystem
from biology.systems.mutation_system import MutationSystem
from biology.lifecycle.birth.systems.reproduction_system import BiologyReproductionSystem
from biology.systems.immune_system import ImmuneSystem
from biology.systems.damage_repair_system import DamageRepairSystem
from biology.systems.nutrient_system import NutrientSystem
from biology.systems.competition_system import CompetitionSystem
from animal.systems.grazing_system import GrazingSystem
from animal.systems.predation_system import PredationSystem
from animal.systems.animal_reproduction_system import AnimalReproductionSystem
from animal.systems.animal_needs_system import AnimalNeedsSystem
from animal.systems.animal_social_system import AnimalSocialSystem
from animal.systems.animal_memory_system import AnimalMemorySystem
from animal.systems.animal_territory_system import AnimalTerritorySystem
from animal.systems.animal_migration_system import AnimalMigrationSystem
from animal.systems.animal_perception_system import AnimalPerceptionSystem
from animal.systems.animal_learning_system import AnimalLearningSystem

from decomposer.systems.decomposer_system import DecomposerSystem
from environment.soil.systems.soil_to_environment_sync_system import SoilToEnvironmentSyncSystem
from biology.ecology.trophic_level_system import TrophicLevelSystem
from biology.ecology.population_dynamics_system import PopulationDynamicsSystem
from biology.ecology.ecology_balance_system import EcologyBalanceSystem
from biology.ecology.speciation_system import SpeciationSystem

# 植物专用系统
from plant.systems.photosynthesis_system import PlantPhotosynthesisSystem
from plant.systems.water_uptake_system import PlantWaterUptakeSystem
from plant.systems.seed_dispersal_system import SeedDispersalSystem
from plant.systems.terrain_adaptation_system import TerrainAdaptationSystem

# 地府系统
from death_archive.systems.death_archive_system import DeathArchiveSystem
from save_load.systems.save_load_system import SaveLoadSystem

# 配置常量
from config.system_priorities import SystemPriority

# 规则系统
from rules.transformation_system import TransformationSystem
from rules.transformation_rule import TransformationRule
from rules.rules_config import spoiled_food_condition, spoiled_food_transform
from resource.food.components.food_component import FoodComponent

# 文明系统
from civilization import CivilizationSystem
from presentation.human_panel import HumanStatePanel
from presentation.human_observation_system import HumanObservationSystem
from core.systems.event_log_system import EventLogSystem
from environment.atmosphere.system.atmosphere_physics_system import AtmospherePhysicsSystem
from human.systems.social.role_system import RoleSystem
from human.systems.economy.economy_system import EconomySystem

# 工厂
from human.human_factory import HumanFactory
from plant.plant_factory import PlantFactory
from resource.food.food_factory import FoodFactory
from resource.water.water_factory import WaterFactory
from environment.environment_factory import EnvironmentFactory



class SimulationLoop:
    """
    统一模拟循环

    执行顺序（按优先级）：
    1. 时间系统 - 推进时间
    2. 空间系统 - 同步实体位置
    3. 环境系统 - 更新天气、季节等
    4. 人类系统 - 生理、认知、社交、生存等
    5. 生物学系统 - 生长、死亡、繁衍等
    6. 规则系统 - 文明演进规则
    """

    def __init__(self, world: World):
        self.world = world

        # === 初始化世界实体（此前由 core.world 自动创建，现由 application 层负责）===
        from world.world_entity import WorldEntity
        from time_module.time_component import TimeComponent
        from space.space_system import SpaceSystem
        from space.collision_system import CollisionSystem
        from core.components.world_config_component import WorldConfigComponent

        world_entity = WorldEntity()
        world_entity.add_component(TimeComponent())
        world_entity.add_component(WorldConfigComponent(map_width=100, map_height=100))
        self.world.set_world_entity(world_entity)

        # 注册空间系统
        space_system = SpaceSystem()
        self.world.add_system(space_system)

        # 获取空间系统引用
        self.space_system = self.world.get_system(SpaceSystem)

        # 初始化所有系统
        self._init_systems()

        # 初始化工厂
        self.human_factory = HumanFactory()
        self.plant_factory = PlantFactory()
        self.food_factory = FoodFactory()
        self.water_factory = WaterFactory()

        # 初始化环境网格（10×10 低分辨率网格，供 Continuum 系统使用）
        self._init_environment_grid()

        # 统计信息
        self.step_count = 0
        self.start_time = time.time()

    def _init_systems(self):
        """初始化所有系统，按执行顺序分组并注册到 world"""
        self._init_infrastructure_systems()
        self._init_environment_systems()
        self._init_human_systems()
        self._init_physiology_and_animal_systems()
        self._init_plant_systems()
        self._init_biology_systems()
        self._init_ecology_systems()
        self._init_rule_and_civilization_systems()

    def _init_infrastructure_systems(self):
        """基础设施层：存档、时间、事件日志"""
        self.save_load_system = SaveLoadSystem()
        self.save_load_system.priority = 1
        self.world.add_system(self.save_load_system)

        self.time_system = TimeSystem()
        self.time_system.priority = SystemPriority.TIME
        self.world.add_system(self.time_system)

        self.event_log_system = EventLogSystem()
        self.event_log_system.priority = SystemPriority.EVENT_LOG
        self.world.add_system(self.event_log_system)

    def _init_environment_systems(self):
        """环境层：环境管线、大气物理、天气效果、碰撞检测、路径规划"""
        self.env_pipeline = EnvironmentBuilder.build(self.world)
        self.env_pipeline.priority = SystemPriority.ENVIRONMENT
        self.world.add_system(self.env_pipeline)

        self.atmosphere_physics_system = AtmospherePhysicsSystem()
        self.atmosphere_physics_system.priority = SystemPriority.ATMOSPHERE
        self.world.add_system(self.atmosphere_physics_system)

        self.weather_subsystems = [
            HeatEffectSystem(),
            ColdEffectSystem(),
            RainEffectSystem(),
            WindEffectSystem(),
            HumidityEffectSystem(),
        ]
        for system in self.weather_subsystems:
            system.priority = SystemPriority.WEATHER_EFFECT
            self.world.add_system(system)

        self.pathfinding_system = PathfindingSystem()
        self.pathfinding_system.priority = SystemPriority.PATHFINDING
        self.world.add_system(self.pathfinding_system)

        # 碰撞检测系统（v3.0.1 新增）
        self.collision_system = CollisionSystem(auto_resolve=True)
        self.collision_system.priority = SystemPriority.COLLISION
        self.world.add_system(self.collision_system)

    def _init_human_systems(self):
        """人类核心层：感知→情绪→思维→目标→意图→决策→规划→动作→社交"""
        self.human_systems = [
            RoleSystem(),
            PerceptionSystem(),
            EmotionSystem(),
            ThoughtSystem(),
            GoalSystem(),
            IntentSystem(),
            DecisionSystem(),
            PlanningSystem(),
            ActionSystem(),
            SearchSystem(),
            MovementSystem(),
            EatSystem(),
            DrinkSystem(),
            SleepSystem(),
            PickupSystem(),
            HarvestSystem(),
            SocializeSystem(),
            CombatSystem(),
            SocialSystem(),
            PairingSystem(),
            ReproductionSystem(),
            BirthSystem(),
            DialogueSystem(),
            PlantingSystem(),
        ]
        for system in self.human_systems:
            system.priority = SystemPriority.HUMAN_COGNITIVE
            self.world.add_system(system)

        self.combat_ai_system = CombatAISystem()
        self.combat_ai_system.priority = SystemPriority.COMBAT_AI
        self.world.add_system(self.combat_ai_system)

        self.conflict_detection_system = ConflictDetectionSystem()
        self.conflict_detection_system.priority = SystemPriority.CONFLICT_DETECTION
        self.world.add_system(self.conflict_detection_system)

        self.conflict_resolution_system = ConflictResolutionSystem()
        self.conflict_resolution_system.priority = SystemPriority.CONFLICT_RESOLUTION
        self.world.add_system(self.conflict_resolution_system)

        self.reputation_system = ReputationSystem()
        self.reputation_system.priority = SystemPriority.REPUTATION
        self.world.add_system(self.reputation_system)

        self.economy_system = EconomySystem()
        self.economy_system.priority = SystemPriority.ECONOMY
        self.world.add_system(self.economy_system)

        self.territory_system = TerritorySystem()
        self.territory_system.priority = SystemPriority.TERRITORY
        self.world.add_system(self.territory_system)

        self.leadership_system = LeadershipSystem()
        self.leadership_system.priority = SystemPriority.LEADERSHIP
        self.world.add_system(self.leadership_system)

        self.loyalty_system = LoyaltySystem()
        self.loyalty_system.priority = SystemPriority.LOYALTY
        self.world.add_system(self.loyalty_system)

        self.recruit_system = RecruitSystem()
        self.recruit_system.priority = SystemPriority.RECRUIT
        self.world.add_system(self.recruit_system)

        self.tribe_system = TribeSystem()
        self.tribe_system.priority = SystemPriority.TRIBE
        self.world.add_system(self.tribe_system)
        self.human_systems.append(self.tribe_system)

    def _init_physiology_and_animal_systems(self):
        """生理系统、疾病传播、动物行为、医疗保健"""
        self.physiology_systems = [
            PhysiologyNeedsSystem(),
            HealthSystem(),
            HumanDeathTriggerSystem(),
        ]
        for system in self.physiology_systems:
            system.priority = SystemPriority.PHYSIOLOGY
            self.world.add_system(system)

        self.disease_spread_system = DiseaseSpreadSystem()
        self.disease_spread_system.priority = SystemPriority.DISEASE_SPREAD
        self.world.add_system(self.disease_spread_system)

        self.grazing_system = GrazingSystem()
        self.grazing_system.priority = SystemPriority.GRAZING
        self.world.add_system(self.grazing_system)

        self.animal_reproduction_system = AnimalReproductionSystem()
        self.animal_reproduction_system.priority = SystemPriority.REPRODUCTION
        self.world.add_system(self.animal_reproduction_system)

        self.predation_system = PredationSystem()
        self.predation_system.priority = SystemPriority.PREDATION
        self.world.add_system(self.predation_system)

        # 新增动物生态系统
        self.animal_needs_system = AnimalNeedsSystem()
        self.animal_needs_system.priority = SystemPriority.ANIMAL_NEEDS
        self.world.add_system(self.animal_needs_system)

        self.animal_social_system = AnimalSocialSystem()
        self.animal_social_system.priority = SystemPriority.ANIMAL_SOCIAL
        self.world.add_system(self.animal_social_system)

        self.animal_memory_system = AnimalMemorySystem()
        self.animal_memory_system.priority = SystemPriority.ANIMAL_MEMORY
        self.world.add_system(self.animal_memory_system)

        self.animal_territory_system = AnimalTerritorySystem()
        self.animal_territory_system.priority = SystemPriority.ANIMAL_TERRITORY
        self.world.add_system(self.animal_territory_system)

        self.animal_migration_system = AnimalMigrationSystem()
        self.animal_migration_system.priority = SystemPriority.ANIMAL_MIGRATION
        self.world.add_system(self.animal_migration_system)

        self.animal_perception_system = AnimalPerceptionSystem()
        self.animal_perception_system.priority = SystemPriority.ANIMAL_PERCEPTION
        self.world.add_system(self.animal_perception_system)

        self.animal_learning_system = AnimalLearningSystem()
        self.animal_learning_system.priority = SystemPriority.ANIMAL_LEARNING
        self.world.add_system(self.animal_learning_system)

        self.healthcare_system = HealthcareSystem()
        self.healthcare_system.priority = SystemPriority.HEALTHCARE
        self.world.add_system(self.healthcare_system)

        self.memory_decay_system = MemoryDecaySystem()
        self.memory_decay_system.priority = SystemPriority.MEMORY_DECAY
        self.world.add_system(self.memory_decay_system)

    def _init_plant_systems(self):
        """植物专用系统（在 GrowthSystem 之前准备光照/水分数据）"""
        self.plant_systems = [
            PlantPhotosynthesisSystem(),
            PlantWaterUptakeSystem(),
            TerrainAdaptationSystem(),
        ]
        for system in self.plant_systems:
            system.priority = SystemPriority.PLANT_GROWTH
            self.world.add_system(system)

    def _init_biology_systems(self):
        """生物学核心系统"""
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
            system.priority = SystemPriority.BIOLOGY
            self.world.add_system(system)

    def _init_ecology_systems(self):
        """生态监控层：死亡档案、分解者、土壤同步、生态平衡"""
        self.death_archive_system = DeathArchiveSystem()
        self.death_archive_system.priority = SystemPriority.DEATH_ARCHIVE
        self.world.add_system(self.death_archive_system)

        self.decomposer_system = DecomposerSystem()
        self.decomposer_system.priority = SystemPriority.DEATH_ARCHIVE
        self.world.add_system(self.decomposer_system)

        self.soil_sync_system = SoilToEnvironmentSyncSystem()
        self.soil_sync_system.priority = SystemPriority.DEATH_ARCHIVE
        self.world.add_system(self.soil_sync_system)

        self.trophic_level_system = TrophicLevelSystem()
        self.trophic_level_system.priority = SystemPriority.BIOLOGY
        self.world.add_system(self.trophic_level_system)

        self.population_dynamics_system = PopulationDynamicsSystem()
        self.population_dynamics_system.priority = SystemPriority.BIOLOGY
        self.world.add_system(self.population_dynamics_system)

        self.ecology_balance_system = EcologyBalanceSystem()
        self.ecology_balance_system.priority = SystemPriority.RULES
        self.world.add_system(self.ecology_balance_system)

        self.speciation_system = SpeciationSystem()
        self.speciation_system.priority = SystemPriority.CIVILIZATION
        self.world.add_system(self.speciation_system)

    def _init_rule_and_civilization_systems(self):
        """规则系统与文明系统（最高层级）"""
        self.transformation_rules = [
            TransformationRule(
                source_component=FoodComponent,
                condition=spoiled_food_condition,
                transform=spoiled_food_transform
            ),
        ]
        self.rule_systems = [
            TransformationSystem(self.transformation_rules),
        ]
        for system in self.rule_systems:
            system.priority = SystemPriority.RULES
            self.world.add_system(system)

        self.civilization_system = CivilizationSystem()
        self.civilization_system.priority = SystemPriority.CIVILIZATION
        self.world.add_system(self.civilization_system)

        self.human_panel = HumanStatePanel()
        self.human_observation_system = HumanObservationSystem()
        self.human_observation_system.priority = SystemPriority.HUMAN_OBSERVATION
        self.world.add_system(self.human_observation_system)

    def update(self, delta_hours: float = 1.0):
        """
        执行一个时间步的更新

        Args:
            delta_hours: 时间增量（小时）
        """
        # 同步步数到 world，供 EventLog 使用
        self.world._step_count = self.step_count

        # 所有 ECS System 由 world 统一调度（按 priority 排序执行）
        self.world.update(delta_hours)

        # 资源再生（非 System，手动调用）
        self._regenerate_resources(delta_hours)

        self.step_count += 1

    def create_initial_resources(self, food_count: int = 80, water_count: int = 80):
        """
        创建初始资源（食物和水源）

        Args:
            food_count: 食物实体数量
            water_count: 水源实体数量
        """
        from core.components.world_config_component import WorldConfigComponent
        world_config = self.world.get_world_component(WorldConfigComponent)
        logger.info(f"[Init] 资源: {food_count} 食物, {water_count} 水源")

        for i in range(food_count):
            x = random.randint(0, world_config.map_width - 1)
            y = random.randint(0, world_config.map_height - 1)
            food = self.food_factory.create_food(
                self.world, x=x, y=y,
                food_type="berry",
                amount=random.uniform(10, 50)
            )

        # 水源聚落化分布：创建5-8个聚落中心，每个中心附近生成多个水源
        import math
        num_clusters = random.randint(5, 8)
        margin = 10
        max_cx = world_config.map_width - 1 - margin
        max_cy = world_config.map_height - 1 - margin
        cluster_centers = [(random.randint(margin, max_cx), random.randint(margin, max_cy)) for _ in range(num_clusters)]
        for i in range(water_count):
            # 随机选择一个聚落中心
            cx, cy = random.choice(cluster_centers)
            # 在中心附近生成水源（正态分布，sigma=8）
            x = int(random.gauss(cx, 8))
            y = int(random.gauss(cy, 8))
            x, y = world_config.clamp_position(x, y)
            water = self.water_factory.create_water(
                self.world, x=x, y=y,
                amount=random.uniform(100, 300)
            )

    def _regenerate_resources(self, delta_hours: float):
        """
        资源再生机制

        当食物/水源实体数低于阈值时，在随机位置刷新新资源，
        防止系统因资源耗尽而全体死亡。
        """
        # 统计当前食物和水源实体（仅限地面上的，不含背包内）
        import random
        food_count = 0
        water_count = 0

        from resource.food.components.food_component import FoodComponent
        from resource.water.components.water_component import WaterComponent
        from space.space_component import SpaceComponent

        for entity, [food, space] in self.world.get_components(FoodComponent, SpaceComponent):
            food_count += 1

        for entity, [water, space] in self.world.get_components(WaterComponent, SpaceComponent):
            water_count += 1
            # 水源量缓慢恢复
            if water.amount < water.max_amount:
                water.amount = min(water.max_amount, water.amount + 1.0 * delta_hours)

        # 食物低于阈值时补充（阈值与人口挂钩，每人保底3份食物）
        human_count = 0
        from human.components.basic.human_component import HumanComponent
        for _ in self.world.get_components(HumanComponent):
            human_count += 1
        FOOD_MIN = max(20, human_count * 3)
        if food_count < FOOD_MIN:
            need = FOOD_MIN - food_count
            # 收集现有地面食物位置，用于聚落化生成
            existing_food_positions = []
            for e, [f, s] in self.world.get_components(FoodComponent, SpaceComponent):
                existing_food_positions.append((s.x, s.y))
            from core.components.world_config_component import WorldConfigComponent
            world_config = self.world.get_world_component(WorldConfigComponent)
            for _ in range(need):
                if existing_food_positions and random.random() < 0.7:
                    # 70% 概率在已有食物附近生成（聚落化）
                    fx, fy = random.choice(existing_food_positions)
                    x = int(random.gauss(fx, 5))
                    y = int(random.gauss(fy, 5))
                else:
                    # 30% 概率完全随机（探索新区域）
                    x = random.randint(0, world_config.map_width - 1)
                    y = random.randint(0, world_config.map_height - 1)
                x, y = world_config.clamp_position(x, y)
                self.food_factory.create_food(
                    self.world, x=x, y=y,
                    food_type="berry",
                    amount=random.uniform(20, 60)
                )
            logger.info(f"[Regen] 补充 {need} 食物 ({food_count}+{need})，人口:{human_count}")

        # 水源低于阈值时补充（阈值与人口挂钩，同时设置上限避免无限积累）
        WATER_MIN = max(30, human_count * 4)
        WATER_MAX = max(80, human_count * 10)
        if water_count < WATER_MIN:
            need = min(WATER_MAX - water_count, WATER_MIN - water_count)
            # 收集现有水源位置，用于聚落化生成
            existing_water_positions = []
            for e, [w, s] in self.world.get_components(WaterComponent, SpaceComponent):
                existing_water_positions.append((s.x, s.y))
            for _ in range(need):
                if existing_water_positions and random.random() < 0.7:
                    wx, wy = random.choice(existing_water_positions)
                    x = int(random.gauss(wx, 8))
                    y = int(random.gauss(wy, 8))
                else:
                    x = random.randint(0, world_config.map_width - 1)
                    y = random.randint(0, world_config.map_height - 1)
                x, y = world_config.clamp_position(x, y)
                self.water_factory.create_water(
                    self.world, x=x, y=y,
                    amount=random.uniform(80, 150)
                )
            logger.info(f"[Regen] 补充 {need} 水源 ({water_count}+{need})")

    def create_initial_population(self, human_count: int = 10):
        """
        创建初始人口

        Args:
            human_count: 初始人类数量
        """
        logger.info(f"[Init] 人口: {human_count} 人类")

        # 让人类初始位置分布在地图中央区域，避免边缘（提高早期找到资源的概率）
        for i in range(human_count):
            name = f"Human_{i+1}"
            x, y = random.randint(20, 79), random.randint(20, 79)
            self.human_factory.create_human(self.world, name, x, y)

    def create_initial_plants(self, plant_count: int = 30):
        """
        创建初始植物，部分直接设为成熟状态以便人类收获

        Args:
            plant_count: 初始植物数量
        """
        from plant.components.plant_component import PlantComponent
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
        from biology.lifecycle.components.morphology_component import MorphologyComponent

        species_list = list(self.plant_factory.SPECIES_PRESETS.keys())
        mature_count = 0

        for i in range(plant_count):
            x, y = random.randint(10, 89), random.randint(10, 89)
            species = random.choice(species_list)
            plant = self.plant_factory.create_plant(
                self.world, species=species, x=x, y=y, variation=0.15
            )

            # 让 60% 的植物初始即为成熟状态（可收获）
            if random.random() < 0.6:
                lifecycle = self.world.get_component(plant, LifeCycleComponent)
                plant_comp = self.world.get_component(plant, PlantComponent)
                morph = self.world.get_component(plant, MorphologyComponent)

                if lifecycle is not None:
                    lifecycle.stage = LifeCycleComponent.MATURE
                    lifecycle.current_age = lifecycle.stage_durations[0] + lifecycle.stage_durations[1] + lifecycle.stage_durations[2]

                if plant_comp is not None:
                    plant_comp.harvestable_yield = random.uniform(8.0, 20.0)
                    plant_comp.max_yield = plant_comp.harvestable_yield * 1.5
                    # 乔木类植物产出木材
                    if species == "tree":
                        plant_comp.produces_wood = True
                        plant_comp.wood_amount = random.uniform(2.0, 8.0)

                # 外观由 MorphologySystem 从生物量动态推导，不硬编码
                if morph is not None:
                    if species == "tree":
                        # 乔木需要大生物量才能支撑高大外观
                        morph.weight = random.uniform(150.0, 400.0)
                    else:
                        morph.weight = plant_comp.harvestable_yield * 2.0 if plant_comp else 20.0

                mature_count += 1

        logger.info(f"[Init] 植物: {plant_count} 株（{mature_count} 株成熟可收获）")

    def _init_environment_grid(self, grid_size: int = 10):
        """
        初始化环境网格实体，供 EnvironmentalContinuumSystem 使用。
        使用低分辨率网格（默认 10×10），每个单元格代表 10×10 地图区域。
        """
        env_factory = EnvironmentFactory(self.world)
        count = 0
        for gx in range(grid_size):
            for gy in range(grid_size):
                env_factory.create_environment_cell(gx, gy)
                count += 1
        logger.info(f"[Init] 环境网格: {grid_size}×{grid_size}={count} 单元")

    def get_stats(self) -> dict:
        """获取当前统计信息"""
        current_time = time.time()
        elapsed = current_time - self.start_time

        total_entities = len(self.world.entities)

        # 统计数据 —— 使用 get_components() 避免 O(E) 全量遍历
        from resource.water.components.water_component import WaterComponent
        from human.components.basic.human_component import HumanComponent
        from plant.components.plant_component import PlantComponent

        human_count = sum(1 for _ in self.world.query_components(HumanComponent))
        food_count = sum(1 for _ in self.world.get_components(FoodComponent))
        water_count = sum(1 for _ in self.world.get_components(WaterComponent))
        plant_count = sum(1 for _ in self.world.get_components(PlantComponent))

        try:
            civilization_status = self.civilization_system.get_civilization_status()
        except AttributeError:
            civilization_status = {'stage': 'unknown', 'metrics': {}, 'discovered_technologies': []}

        return {
            'step_count': self.step_count,
            'elapsed_time': elapsed,
            'steps_per_second': self.step_count / elapsed if elapsed > 0 else 0,
            'total_entities': total_entities,
            'human_count': human_count,
            'food_count': food_count,
            'water_count': water_count,
            'plant_count': plant_count,
            'civilization_stage': civilization_status['stage'],
            'civilization_metrics': civilization_status.get('metrics', {}),
            'discovered_technologies': civilization_status.get('discovered_technologies', [])
        }

    def run_simulation(self, steps: int = 100, delta_hours: float = 1.0, 
                        verbose: bool = True, show_panel: bool = False, 
                        panel_interval: int = 50):
        """
        运行模拟

        Args:
            steps: 运行步数
            delta_hours: 每步时间增量
            verbose: 是否打印简要统计
            show_panel: 是否定期打印人类状态面板
            panel_interval: 面板刷新间隔（步数）
        """
        logger.info(f"[Run] 模拟: {steps} 步 × {delta_hours}h")

        for step in range(steps):
            if verbose and step % 50 == 0:
                stats = self.get_stats()
                logger.info(f"  Step {step:>4}/{steps} | 实体:{stats['total_entities']:>3} "
                            f"人口:{stats['human_count']:>2} 食物:{stats['food_count']:>2} "
                            f"水源:{stats['water_count']:>2} 植物:{stats['plant_count']:>2} "
                            f"{stats['steps_per_second']:>6.1f}步/s")
            
            if show_panel and step % panel_interval == 0 and step > 0:
                self.human_panel.print_panel(self.world, step)

            self.update(delta_hours)

        final_stats = self.get_stats()
        logger.info(f"[Done] 实体:{final_stats['total_entities']} 人口:{final_stats['human_count']} "
                    f"食物:{final_stats['food_count']} 水源:{final_stats['water_count']} 植物:{final_stats['plant_count']} "
                    f"文明:{final_stats['civilization_stage']} "
                    f"{final_stats['steps_per_second']:.0f}步/s")

    def _debug_human_status(self):
        """打印所有人类的完整状态（调试用）"""
        pass  # 默认关闭，避免输出过多


