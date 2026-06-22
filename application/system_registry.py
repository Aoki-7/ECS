#!/usr/bin/env python3
"""
系统注册中心

负责所有 ECS 系统的导入、分组和注册到 World。
将系统初始化逻辑从 SimulationLoop 中剥离。
"""

import logging
from typing import List, Dict, Any

from core.world import World
from config.system_priorities import SystemPriority

logger = logging.getLogger(__name__)


class SystemRegistry:
    """
    系统注册中心

    职责：
        1. 按层级分组管理系统
        2. 自动导入和注册系统
        3. 支持优先级配置
        4. 提供系统查询接口
    """

    def __init__(self, world: World):
        self.world = world
        self._systems: Dict[str, Any] = {}
        self._groups: Dict[str, List[Any]] = {
            'infrastructure': [],
            'environment': [],
            'human': [],
            'animal': [],
            'plant': [],
            'biology': [],
            'ecology': [],
            'civilization': [],
            'v35_v36': [],
        }

    def register(self, name: str, system: Any, group: str = 'default', priority: int = None) -> None:
        """注册单个系统"""
        if priority is not None:
            system.priority = priority
        self.world.add_system(system)
        self._systems[name] = system
        if group in self._groups:
            self._groups[group].append(system)
        logger.debug(f"[SystemRegistry] 注册 {name} -> {group}")

    def get(self, name: str) -> Any:
        """获取已注册的系统"""
        return self._systems.get(name)

    def get_group(self, group: str) -> List[Any]:
        """获取某组的所有系统"""
        return self._groups.get(group, [])

    def init_all(self) -> None:
        """初始化所有系统（按优先级排序）"""
        # 基础设施层
        self._init_infrastructure()
        # 环境层
        self._init_environment()
        # 人类层
        self._init_human()
        # 动物层
        self._init_animal()
        # 植物层
        self._init_plant()
        # 生物层
        self._init_biology()
        # 生态层
        self._init_ecology()
        # 文明层
        self._init_civilization()
        # v3.5-v3.6 新系统
        self._init_v35_v36()

    def _init_infrastructure(self) -> None:
        """基础设施：存档、时间、事件日志"""
        from save_load.systems.save_load_system import SaveLoadSystem
        from time_module.time_system import TimeSystem
        from identity.event_log_system import EventLogSystem

        self.register('save_load', SaveLoadSystem(), 'infrastructure', SystemPriority.TIME)
        self.register('time', TimeSystem(), 'infrastructure', SystemPriority.TIME)
        self.register('event_log', EventLogSystem(), 'infrastructure', SystemPriority.EVENT_LOG)

    def _init_environment(self) -> None:
        """环境层：环境管线、天气效果、碰撞检测、路径规划"""
        from environment.config.environment_builder import EnvironmentBuilder
        from human.systems.environment.heat_effect_system import HeatEffectSystem
        from human.systems.environment.cold_effect_system import ColdEffectSystem
        from human.systems.environment.rain_effect_system import RainEffectSystem
        from human.systems.environment.wind_effect_system import WindEffectSystem
        from human.systems.environment.humidity_effect_system import HumidityEffectSystem
        from human.systems.navigation.pathfinding_system import PathfindingSystem
        from space.collision_system import CollisionSystem

        env_pipeline = EnvironmentBuilder.build(self.world)
        self.register('env_pipeline', env_pipeline, 'environment', SystemPriority.ENVIRONMENT)

        for cls in [HeatEffectSystem, ColdEffectSystem, RainEffectSystem, WindEffectSystem, HumidityEffectSystem]:
            name = cls.__name__.replace('EffectSystem', '').lower()
            self.register(f'weather_{name}', cls(), 'environment', SystemPriority.WEATHER_EFFECT)

        # 新增：灾害检测系统
        from environment.systems.fire_detection_system import FireDetectionSystem
        from environment.systems.flood_detection_system import FloodDetectionSystem
        from environment.systems.drought_detection_system import DroughtDetectionSystem
        from environment.systems.disaster_impact_system import DisasterImpactSystem
        self.register('fire_detection', FireDetectionSystem(), 'environment', SystemPriority.WEATHER_EFFECT)
        self.register('flood_detection', FloodDetectionSystem(), 'environment', SystemPriority.WEATHER_EFFECT)
        self.register('drought_detection', DroughtDetectionSystem(), 'environment', SystemPriority.WEATHER_EFFECT)
        self.register('disaster_impact', DisasterImpactSystem(), 'environment', SystemPriority.WEATHER_EFFECT)

        # 新增：生物-环境耦合系统
        from environment.continuum.systems.vegetation_coupling_system import VegetationCouplingSystem
        from environment.continuum.systems.animal_coupling_system import AnimalCouplingSystem
        from environment.continuum.systems.human_coupling_system import HumanCouplingSystem
        from environment.continuum.systems.agriculture_coupling_system import AgricultureCouplingSystem
        self.register('vegetation_coupling', VegetationCouplingSystem(), 'environment', SystemPriority.ENVIRONMENT)
        self.register('animal_coupling', AnimalCouplingSystem(), 'environment', SystemPriority.ENVIRONMENT)
        self.register('human_coupling', HumanCouplingSystem(), 'environment', SystemPriority.ENVIRONMENT)
        self.register('agriculture_coupling', AgricultureCouplingSystem(), 'environment', SystemPriority.ENVIRONMENT)

        self.register('pathfinding', PathfindingSystem(), 'environment', SystemPriority.PATHFINDING)
        self.register('collision', CollisionSystem(auto_resolve=True), 'environment', SystemPriority.COLLISION)

    def _init_human(self) -> None:
        """人类层：社交、认知、生理、行动、战斗等"""
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
        from human.systems.combat.combat_system import CombatSystem
        from human.systems.combat.combat_ai_system import CombatAISystem
        from human.systems.interaction.dialogue_system import DialogueSystem
        from human.systems.physiological.health_system import HealthSystem
        from human.systems.physiological.hunger_system import HungerSystem
        from human.systems.physiological.thirst_system import ThirstSystem
        from human.systems.physiological.energy_system import EnergySystem
        from human.systems.physiological.comfort_system import ComfortSystem
        from human.systems.physiological.social_need_system import SocialNeedSystem
        from human.systems.physiological.physiology_needs_system import PhysiologyNeedsSystem

        # 社交系统
        for cls in [SocialSystem, PairingSystem, ReproductionSystem, BirthSystem,
                    TribeSystem, TerritorySystem, LeadershipSystem, LoyaltySystem, RecruitSystem]:
            name = cls.__name__.replace('System', '').lower()
            self.register(f'social_{name}', cls(), 'human', SystemPriority.HUMAN_COGNITIVE)

        # 认知系统
        for cls in [DecisionSystem, PerceptionSystem, EmotionSystem, ThoughtSystem, GoalSystem]:
            name = cls.__name__.replace('System', '').lower()
            self.register(f'cognitive_{name}', cls(), 'human', SystemPriority.HUMAN_COGNITIVE)

        # 核心系统
        for cls in [IntentSystem, PlanningSystem, ActionSystem]:
            name = cls.__name__.replace('System', '').lower()
            self.register(f'core_{name}', cls(), 'human', SystemPriority.HUMAN_COGNITIVE)

        # 行动系统
        for cls in [MovementSystem, EatSystem, DrinkSystem, SleepSystem, PickupSystem,
                    SearchSystem, SocializeSystem, HarvestSystem, PlantingSystem]:
            name = cls.__name__.replace('System', '').lower()
            self.register(f'action_{name}', cls(), 'human', SystemPriority.HUMAN_OBSERVATION)

        # 战斗系统
        self.register('combat', CombatSystem(), 'human', SystemPriority.COMBAT_AI)
        self.register('combat_ai', CombatAISystem(), 'human', SystemPriority.COMBAT_AI)
        self.register('dialogue', DialogueSystem(), 'human', SystemPriority.CONFLICT_DETECTION)

        # 生理系统
        for cls in [HealthSystem, HungerSystem, ThirstSystem, EnergySystem,
                    ComfortSystem, SocialNeedSystem, PhysiologyNeedsSystem]:
            name = cls.__name__.replace('System', '').lower()
            self.register(f'physiology_{name}', cls(), 'human', SystemPriority.PHYSIOLOGY)

        # self.register('human_observation', HumanObservationSystem(), 'human', SystemPriority.HUMAN_OBSERVATION)

    def _init_animal(self) -> None:
        """动物层：需求、社交、记忆、领地、迁徙、感知、学习、繁殖、捕食、觅食"""
        from animal.systems.animal_needs_system import AnimalNeedsSystem
        from animal.systems.animal_social_system import AnimalSocialSystem
        from animal.systems.animal_memory_system import AnimalMemorySystem
        from animal.systems.animal_territory_system import AnimalTerritorySystem
        from animal.systems.animal_migration_system import AnimalMigrationSystem
        from animal.systems.animal_perception_system import AnimalPerceptionSystem
        from animal.systems.animal_learning_system import AnimalLearningSystem
        from animal.systems.animal_reproduction_system import AnimalReproductionSystem
        from animal.systems.predation_system import PredationSystem
        from animal.systems.grazing_system import GrazingSystem

        for cls in [AnimalNeedsSystem, AnimalSocialSystem, AnimalMemorySystem,
                    AnimalTerritorySystem, AnimalMigrationSystem, AnimalPerceptionSystem,
                    AnimalLearningSystem, AnimalReproductionSystem, PredationSystem, GrazingSystem]:
            name = cls.__name__.replace('System', '').lower().replace('animal_', '')
            self.register(f'animal_{name}', cls(), 'animal', SystemPriority.ANIMAL_NEEDS)

    def _init_plant(self) -> None:
        """植物层：光合作用、吸水、种子传播、地形适应"""
        from plant.systems.photosynthesis_system import PlantPhotosynthesisSystem
        from plant.systems.water_uptake_system import PlantWaterUptakeSystem
        from plant.systems.seed_dispersal_system import SeedDispersalSystem
        from plant.systems.terrain_adaptation_system import TerrainAdaptationSystem

        self.register('plant_photosynthesis', PlantPhotosynthesisSystem(), 'plant', SystemPriority.PLANT_GROWTH)
        self.register('plant_water', PlantWaterUptakeSystem(), 'plant', SystemPriority.PLANT_GROWTH)
        self.register('plant_seed', SeedDispersalSystem(), 'plant', SystemPriority.PLANT_GROWTH)
        self.register('plant_terrain', TerrainAdaptationSystem(), 'plant', SystemPriority.PLANT_GROWTH)

    def _init_biology(self) -> None:
        """生物层：基因表达、生长、死亡、生命周期、免疫、营养"""
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

        self.register('gene_expression', GeneExpressionSystem(), 'biology', SystemPriority.GENE_EXPRESSION)
        self.register('growth', GrowthSystem(), 'biology', SystemPriority.GROWTH)
        self.register('morphology', MorphologySystem(), 'biology', SystemPriority.MORPHOLOGY)
        self.register('death_trigger', CreatureDeathTriggerSystem(), 'biology', SystemPriority.CREATURE_DEATH_TRIGGER)
        self.register('death', DeathSystem(), 'biology', SystemPriority.DEATH_EXECUTION)
        self.register('death_event', DeathEventSystem(), 'biology', SystemPriority.DEATH_EVENT)
        self.register('corpse', CorpseSystem(), 'biology', SystemPriority.CORPSE)
        self.register('life_cycle', LifeCycleSystem(), 'biology', SystemPriority.LIFE_CYCLE)
        self.register('senescence', SenescenceSystem(), 'biology', SystemPriority.SENESCENCE)
        self.register('mutation', MutationSystem(), 'biology', SystemPriority.MUTATION)
        self.register('biology_reproduction', BiologyReproductionSystem(), 'biology', SystemPriority.REPRODUCTION)
        self.register('immune', ImmuneSystem(), 'biology', SystemPriority.IMMUNE)
        self.register('damage_repair', DamageRepairSystem(), 'biology', SystemPriority.DAMAGE_REPAIR)
        self.register('nutrient', NutrientSystem(), 'biology', SystemPriority.NUTRIENT)
        self.register('competition', CompetitionSystem(), 'biology', SystemPriority.COMPETITION)

    def _init_ecology(self) -> None:
        """生态层：分解者、土壤同步、营养级、种群动态、生态平衡、物种形成"""
        from decomposer.systems.decomposer_system import DecomposerSystem
        from environment.soil.systems.soil_to_environment_sync_system import SoilToEnvironmentSyncSystem
        from biology.ecology.trophic_level_system import TrophicLevelSystem
        from biology.ecology.population_dynamics_system import PopulationDynamicsSystem
        from biology.ecology.ecology_balance_system import EcologyBalanceSystem
        from biology.ecology.speciation_system import SpeciationSystem

        self.register('decomposer', DecomposerSystem(), 'ecology', SystemPriority.BIOLOGY)
        self.register('soil_sync', SoilToEnvironmentSyncSystem(), 'ecology', SystemPriority.BIOLOGY)
        self.register('trophic_level', TrophicLevelSystem(), 'ecology', SystemPriority.BIOLOGY)
        self.register('population_dynamics', PopulationDynamicsSystem(), 'ecology', SystemPriority.BIOLOGY)
        self.register('ecology_balance', EcologyBalanceSystem(), 'ecology', SystemPriority.BIOLOGY)
        self.register('speciation', SpeciationSystem(), 'ecology', SystemPriority.BIOLOGY)

    def _init_civilization(self) -> None:
        """文明层：文明系统、技术演化、制作系统、建筑系统、农业系统"""
        from civilization.systems.civilization_system import CivilizationSystem
        from civilization.systems.technology_evolution_system import TechnologyEvolutionSystem
        from civilization.systems.crafting_system import CraftingSystem
        from civilization.systems.building_system import BuildingSystem
        from civilization.systems.farm_system import FarmSystem

        self.register('civilization', CivilizationSystem(), 'civilization', SystemPriority.CIVILIZATION)
        self.register('technology_evolution', TechnologyEvolutionSystem(), 'civilization', SystemPriority.CIVILIZATION)
        self.register('crafting', CraftingSystem(), 'civilization', SystemPriority.CIVILIZATION)
        self.register('building', BuildingSystem(), 'civilization', SystemPriority.CIVILIZATION)
        self.register('farm', FarmSystem(), 'civilization', SystemPriority.CIVILIZATION)

    def _init_v35_v36(self) -> None:
        """v3.5-v3.6 新系统：水文、地质、污染、海洋、天文、极端天气、物候学、迁徙、大气化学、紫外线"""
        try:
            from environment.hydrology.systems.water_cycle_system import WaterCycleSystem
            from environment.geology.systems.geology_system import GeologySystem
            from environment.pollution.systems.pollution_system import PollutionSystem
            from environment.ocean.systems.ocean_system import OceanSystem
            from environment.astronomy.systems.astronomy_system import AstronomySystem
            from environment.extreme_weather.systems.extreme_weather_system import ExtremeWeatherSystem
            from environment.phenology.systems.phenology_system import PhenologySystem
            from animal.migration.systems.migration_system import MigrationSystem
            from environment.atmosphere.systems.atmospheric_chemistry_system import AtmosphericChemistrySystem
            from environment.light_field.systems.uv_system import UVSystem

            self.register('water_cycle', WaterCycleSystem(), 'v35_v36', SystemPriority.WATER_CYCLE)
            self.register('geology', GeologySystem(), 'v35_v36', SystemPriority.GEOLOGY)
            self.register('pollution', PollutionSystem(), 'v35_v36', SystemPriority.POLLUTION)
            self.register('ocean', OceanSystem(), 'v35_v36', SystemPriority.OCEAN)
            self.register('astronomy', AstronomySystem(), 'v35_v36', SystemPriority.ASTRONOMY)
            self.register('extreme_weather', ExtremeWeatherSystem(), 'v35_v36', SystemPriority.EXTREME_WEATHER)
            self.register('phenology', PhenologySystem(), 'v35_v36', SystemPriority.PHENOLOGY)
            self.register('migration', MigrationSystem(), 'v35_v36', SystemPriority.MIGRATION)
            self.register('atmospheric_chemistry', AtmosphericChemistrySystem(), 'v35_v36', SystemPriority.ATMOSPHERIC_CHEMISTRY)
            self.register('uv', UVSystem(), 'v35_v36', SystemPriority.UV)
        except ImportError as e:
            logger.warning(f"[SystemRegistry] v3.5-v3.6 系统导入失败: {e}")
