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
import math
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
from core.system import System

# 空间系统
from space.space_system import SpaceSystem

# 时间系统
from time_module.time_system import TimeSystem

# 环境系统
from environment.config.environment_builder import EnvironmentBuilder

# 人类系统
from human.systems.social.social_system import SocialSystem
from human.systems.social.pairing_system import PairingSystem
from human.systems.social.reproduction_system import ReproductionSystem
from human.systems.social.tribe_system import TribeSystem
from human.systems.social.territory_system import TerritorySystem
from human.systems.social.leadership_system import LeadershipSystem
from human.systems.social.loyalty_system import LoyaltySystem
from human.systems.social.recruit_system import RecruitSystem
from human.systems.cognitive.decision_system import DecisionSystem
from human.systems.cognitive.preception_system import PreceptionSystem
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
from human.systems.physiological.human_death_system import HumanDeathSystem

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
from biology.systems.growth_system import GrowthSystem
from biology.systems.morphology_system import MorphologySystem
from biology.systems.death_system import DeathSystem
from biology.systems.life_cycle_system import LifeCycleSystem
from biology.systems.senescence_system import SenescenceSystem
from biology.systems.mutation_system import MutationSystem
from biology.systems.reproduction_system import ReproductionSystem as BiologyReproductionSystem
from biology.systems.immune_system import ImmuneSystem
from biology.systems.damage_repair_system import DamageRepairSystem
from biology.systems.nutrient_system import NutrientSystem
from biology.systems.competition_system import CompetitionSystem

# 规则系统
from rules.transformation_system import TransformationSystem
from rules.transformation_rule import TransformationRule
from rules.rules_config import spoiled_food_condition, spoiled_food_transform
from resource.food.components.food_component import FoodComponent

# 文明系统
from civilization import CivilizationSystem
from human.systems.visualization.human_panel import HumanStatePanel
from core.event_log_component import EventLogComponent
from core.systems.event_log_system import EventLogSystem, EventLog
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

        # 获取空间系统引用
        # 获取SpaceSystem引用
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

        # 1. 时间系统（priority 5，仅次于空间系统）
        self.time_system = TimeSystem()
        self.time_system.priority = 5
        self.world.add_system(self.time_system)

        # 1.5 事件日志系统（priority 5，自动挂载 EventLogComponent）
        self.event_log_system = EventLogSystem()
        self.event_log_system.priority = 5
        self.world.add_system(self.event_log_system)

        # 2. 环境管线（统一编排 14 个子系统，priority 20）
        self.env_pipeline = EnvironmentBuilder.build(self.world)
        self.env_pipeline.priority = 20
        self.world.add_system(self.env_pipeline)

        # 2.5 大气物理系统（priority 20，ISA 模型与派生参数计算）
        self.atmosphere_physics_system = AtmospherePhysicsSystem()
        self.atmosphere_physics_system.priority = 20
        self.world.add_system(self.atmosphere_physics_system)

        # 2.5 天气效果子系统（拆分版，priority 25，替代原 WeatherEffectSystem）
        self.weather_subsystems = [
            HeatEffectSystem(),
            ColdEffectSystem(),
            RainEffectSystem(),
            WindEffectSystem(),
            HumidityEffectSystem(),
        ]
        for system in self.weather_subsystems:
            system.priority = 25
            self.world.add_system(system)

        # 2.7 路径规划系统（priority 28，在战斗AI之前）
        self.pathfinding_system = PathfindingSystem()
        self.pathfinding_system.priority = 28
        self.world.add_system(self.pathfinding_system)

        # 3. 人类系统（按处理流水线排序，priority 30）
        #    感知→情绪→思维→目标→意图→决策→规划→动作调度→搜索/移动/交互→社交
        self.human_systems = [
            # 角色系统（社会身份管理）
            RoleSystem(),
            # 感知层
            PreceptionSystem(),
            # 情绪层：根据生理/环境/行为/社交更新情绪
            EmotionSystem(),
            # 思维层：生成内心独白，更新心理状态
            ThoughtSystem(),
            # 目标层：根据人生阶段和状态更新长期目标
            GoalSystem(),
            # 需求→意图层
            IntentSystem(),
            # 决策层：情绪/性格/记忆/目标→调整意图
            DecisionSystem(),
            # 规划层：意图→任务动作队列
            PlanningSystem(),
            # 动作调度层
            ActionSystem(),
            # 动作执行层
            SearchSystem(),
            MovementSystem(),
            EatSystem(),
            DrinkSystem(),
            SleepSystem(),
            PickupSystem(),
            SocializeSystem(),
            # 战斗层
            CombatSystem(),
            # 社交/繁衍层
            SocialSystem(),
            PairingSystem(),
            ReproductionSystem(),
            # 对话系统
            DialogueSystem(),
        ]
        for system in self.human_systems:
            system.priority = 30
            self.world.add_system(system)

        # 3.5 战斗 AI 系统（priority 29，在动作执行前生成战斗意图）
        self.combat_ai_system = CombatAISystem()
        self.combat_ai_system.priority = 29
        self.world.add_system(self.combat_ai_system)

        # 3.6 冲突管理系统（已拆分为检测+解决，priority 31/32）
        self.conflict_detection_system = ConflictDetectionSystem()
        self.conflict_detection_system.priority = 31
        self.world.add_system(self.conflict_detection_system)

        self.conflict_resolution_system = ConflictResolutionSystem()
        self.conflict_resolution_system.priority = 32
        self.world.add_system(self.conflict_resolution_system)

        # 3.7 声誉系统（priority 35）
        self.reputation_system = ReputationSystem()
        self.reputation_system.priority = 35
        self.world.add_system(self.reputation_system)

        # 3.8 经济系统（priority 35，在人类核心系统之后）
        self.economy_system = EconomySystem()
        self.economy_system.priority = 35
        self.world.add_system(self.economy_system)

        # 3.9 部落子系统（从 TribeSystem 拆分，priority 39-42）
        self.territory_system = TerritorySystem()
        self.territory_system.priority = 39
        self.world.add_system(self.territory_system)

        self.leadership_system = LeadershipSystem()
        self.leadership_system.priority = 40
        self.world.add_system(self.leadership_system)

        self.loyalty_system = LoyaltySystem()
        self.loyalty_system.priority = 41
        self.world.add_system(self.loyalty_system)

        self.recruit_system = RecruitSystem()
        self.recruit_system.priority = 42
        self.world.add_system(self.recruit_system)

        # 部落系统协调器（priority 43，负责初始化和清理）
        self.tribe_system = TribeSystem()
        self.tribe_system.priority = 43
        self.world.add_system(self.tribe_system)
        self.human_systems.append(self.tribe_system)

        # 4. 生理系统（priority 40，拆分后的独立子系统）
        self.physiology_systems = [
            PhysiologyNeedsSystem(),
            HealthSystem(),
            HumanDeathSystem(),
        ]
        for system in self.physiology_systems:
            system.priority = 40
            self.world.add_system(system)

        # 4.5 疾病传播系统（priority 41）
        self.disease_spread_system = DiseaseSpreadSystem()
        self.disease_spread_system.priority = 41
        self.world.add_system(self.disease_spread_system)

        # 4.6 医疗保健系统（priority 42）
        self.healthcare_system = HealthcareSystem()
        self.healthcare_system.priority = 42
        self.world.add_system(self.healthcare_system)

        # 4.7 记忆衰减系统（priority 43）
        self.memory_decay_system = MemoryDecaySystem()
        self.memory_decay_system.priority = 43
        self.world.add_system(self.memory_decay_system)

        # 5. 生物学系统（priority 50）
        # 执行顺序：
        #   基因表达 → 竞争 → 生长 → 形态 → 营养 → 生命周期 → 衰老 → 损伤修复 → 变异 → 繁殖 → 免疫 → 死亡
        self.biology_systems = [
            GeneExpressionSystem(),      # 基因型 → 表型
            CompetitionSystem(),         # 生态竞争（影响 phenotype）
            GrowthSystem(),              # 光合作用 + 呼吸 + 能量分配
            MorphologySystem(),          # 生长池 → 形态更新
            NutrientSystem(),            # N/P/K 吸收与消耗
            LifeCycleSystem(),           # 积温累积 + 阶段推进
            SenescenceSystem(),          # 衰老退化
            DamageRepairSystem(),        # 损伤修复（消耗能量）
            MutationSystem(),            # 持续环境诱变
            BiologyReproductionSystem(), # 成熟期繁殖
            ImmuneSystem(),              # 感染传播与免疫反应
            DeathSystem(),               # 死亡判定（最后执行，移除实体）
        ]
        for system in self.biology_systems:
            system.priority = 50
            self.world.add_system(system)

        # 6. 规则系统（priority 60）
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
            system.priority = 60
            self.world.add_system(system)

        # 7. 文明系统（最高层级，priority 70）
        self.civilization_system = CivilizationSystem()
        self.civilization_system.priority = 70
        self.world.add_system(self.civilization_system)
        
        # 8. 可视化面板
        self.human_panel = HumanStatePanel()

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
        logger.info(f"[Init] 资源: {food_count} 食物, {water_count} 水源")

        for i in range(food_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            food = self.food_factory.create_food(
                self.world, x=x, y=y,
                food_type="berry",
                amount=random.uniform(10, 50)
            )

        # 水源聚落化分布：创建5-8个聚落中心，每个中心附近生成多个水源
        import math
        num_clusters = random.randint(5, 8)
        cluster_centers = [(random.randint(10, 89), random.randint(10, 89)) for _ in range(num_clusters)]
        for i in range(water_count):
            # 随机选择一个聚落中心
            cx, cy = random.choice(cluster_centers)
            # 在中心附近生成水源（正态分布，sigma=8）
            x = int(random.gauss(cx, 8))
            y = int(random.gauss(cy, 8))
            x = max(0, min(99, x))
            y = max(0, min(99, y))
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
            for _ in range(need):
                if existing_food_positions and random.random() < 0.7:
                    # 70% 概率在已有食物附近生成（聚落化）
                    fx, fy = random.choice(existing_food_positions)
                    x = int(random.gauss(fx, 5))
                    y = int(random.gauss(fy, 5))
                else:
                    # 30% 概率完全随机（探索新区域）
                    x = random.randint(0, 99)
                    y = random.randint(0, 99)
                x = max(0, min(99, x))
                y = max(0, min(99, y))
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
                    x = random.randint(0, 99)
                    y = random.randint(0, 99)
                x = max(0, min(99, x))
                y = max(0, min(99, y))
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

        human_count = sum(1 for _ in self.world.query_components(HumanComponent))
        food_count = sum(1 for _ in self.world.get_components(FoodComponent))
        water_count = sum(1 for _ in self.world.get_components(WaterComponent))

        try:
            civilization_status = self.civilization_system.get_civilization_status()
        except Exception:
            civilization_status = {'stage': 'unknown', 'metrics': {}, 'discovered_technologies': []}

        return {
            'step_count': self.step_count,
            'elapsed_time': elapsed,
            'steps_per_second': self.step_count / elapsed if elapsed > 0 else 0,
            'total_entities': total_entities,
            'human_count': human_count,
            'food_count': food_count,
            'water_count': water_count,
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
                            f"水源:{stats['water_count']:>2} "
                            f"{stats['steps_per_second']:>6.1f}步/s")
            
            if show_panel and step % panel_interval == 0 and step > 0:
                self.human_panel.print_panel(self.world, step)

            self.update(delta_hours)

        final_stats = self.get_stats()
        logger.info(f"[Done] 实体:{final_stats['total_entities']} 人口:{final_stats['human_count']} "
                    f"食物:{final_stats['food_count']} 水源:{final_stats['water_count']} "
                    f"文明:{final_stats['civilization_stage']} "
                    f"{final_stats['steps_per_second']:.0f}步/s")

    def _debug_human_status(self):
        """打印所有人类的完整状态（调试用）"""
        pass  # 默认关闭，避免输出过多


def main():
    """主函数"""
    logger.info("=== ECS 世界模拟 ===")

    world = World()
    simulation = SimulationLoop(world)
    simulation.create_initial_resources(food_count=80, water_count=80)
    simulation.create_initial_population(human_count=10)
    simulation.run_simulation(steps=300, delta_hours=1.0, verbose=True)


if __name__ == "__main__":
    main()
