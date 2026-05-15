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

from core.world import World
from core.system import System

# 空间系统
from space.space_system import SpaceSystem

# 时间系统
from time_module.time_system import TimeSystem

# 环境系统
from environment.config.environment_builder import EnvironmentBuilder
from environment.environment_component import EnvironmentComponent

# 人类系统
from human.systems.social.social_system import SocialSystem
from human.systems.social.pairing_system import PairingSystem
from human.systems.social.reproduction_system import ReproductionSystem
from human.systems.cognitive.decision_system import DecisionSystem
from human.systems.cognitive.preception_system import PreceptionSystem
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

# 生理系统
from human.systems.physiological.physiology_needs_system import PhysiologyNeedsSystem
from human.systems.physiological.health_system import HealthSystem

# 生物学系统
from biology.systems.gene_expression_system import GeneExpressionSystem
from biology.systems.growth_system import GrowthSystem
from biology.systems.morphology_system import MorphologySystem
from biology.systems.death_system import DeathSystem
from biology.systems.reproduction_system import ReproductionSystem as BiologyReproductionSystem

# 规则系统
from rules.transformation_system import TransformationSystem
from rules.transformation_rule import TransformationRule
from rules.rules_config import spoiled_food_condition, spoiled_food_transform
from resource.food.components.food_component import FoodComponent

# 文明系统
from civilization import CivilizationSystem

# 工厂
from human.human_factory import HumanFactory
from biology.factories.plant_factory import PlantFactory
from resource.food.food_factory import FoodFactory
from resource.water.water_factory import WaterFactory


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

        # 添加世界级环境组件，确保环境系统可读取数据
        self.world.get_world_entity().add_component(EnvironmentComponent())

        # 获取SpaceSystem引用
        self.space_system = self.world.get_system(SpaceSystem)

        # 初始化所有系统
        self._init_systems()

        # 初始化工厂
        self.human_factory = HumanFactory()
        self.plant_factory = PlantFactory()
        self.food_factory = FoodFactory()
        self.water_factory = WaterFactory()

        # 统计信息
        self.step_count = 0
        self.start_time = time.time()

    def _init_systems(self):
        """初始化所有系统，按执行顺序分组"""

        # 1. 时间系统（最高优先级）
        self.time_system = TimeSystem()

        # 2. 环境系统
        self.env_systems = EnvironmentBuilder.build(self.world)

        # 3. 人类系统（按处理流水线排序）
        #    感知→意图→规划→动作调度→搜索/移动/交互→决策
        self.human_systems = [
            # 感知层
            PreceptionSystem(),
            # 需求→意图层
            IntentSystem(),
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
            # 社交/繁衍层
            SocialSystem(),
            PairingSystem(),
            ReproductionSystem(),
            # 高层决策
            DecisionSystem(),
        ]

        # 4. 生理系统
        self.physiology_systems = [
            PhysiologyNeedsSystem(),
            HealthSystem(),
        ]

        # 5. 生物学系统
        self.biology_systems = [
            GeneExpressionSystem(),
            GrowthSystem(),
            MorphologySystem(),
            DeathSystem(),
        ]

        # 6. 规则系统
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

        # 7. 文明系统（最高层级）
        self.civilization_system = CivilizationSystem()

    def update(self, delta_hours: float = 1.0):
        """
        执行一个时间步的更新

        Args:
            delta_hours: 时间增量（小时）
        """

        # 0. 空间系统同步（确保所有dirty实体位置更新到空间索引）
        self.space_system.update()

        # 1. 时间推进
        self.time_system.update(self.world, delta_hours)

        # 2. 环境更新
        for system in self.env_systems:
            system.update(self.world, delta_hours)

        # 3. 人类系统更新
        for system in self.human_systems:
            system.update(self.world, delta_hours)

        # 4. 生理系统更新
        for system in self.physiology_systems:
            system.update(self.world, delta_hours)

        # 5. 生物学系统更新
        for system in self.biology_systems:
            try:
                system.update(self.world, delta_hours)
            except TypeError:
                system.update(self.world)

        # 6. 规则系统更新
        for system in self.rule_systems:
            system.update(self.world, delta_hours)

        # 7. 文明系统更新
        self.civilization_system.update(self.world, delta_hours)

        self.step_count += 1

    def create_initial_resources(self, food_count: int = 30, water_count: int = 10):
        """
        创建初始资源（食物和水源）

        Args:
            food_count: 食物实体数量
            water_count: 水源实体数量
        """
        print(f"[SimulationLoop] 创建初始资源：{food_count} 食物，{water_count} 水源")

        for i in range(food_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            food = self.food_factory.create_food(
                self.world, x=x, y=y,
                food_type="berry",
                amount=random.uniform(10, 50)
            )

        for i in range(water_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            water = self.water_factory.create_water(
                self.world, x=x, y=y,
                amount=random.uniform(50, 200)
            )

    def create_initial_population(self, human_count: int = 10):
        """
        创建初始人口

        Args:
            human_count: 初始人类数量
        """
        print(f"[SimulationLoop] 创建初始人口：{human_count} 人类")

        for i in range(human_count):
            name = f"Human_{i+1}"
            x, y = random.randint(0, 99), random.randint(0, 99)
            human = self.human_factory.create_human(self.world, name, x, y)
            print(f"  创建人类实体: {human} - {name} at ({x}, {y})")

    def get_stats(self) -> dict:
        """获取当前统计信息"""
        current_time = time.time()
        elapsed = current_time - self.start_time

        total_entities = len(self.world.entities)

        # 统计数据
        human_count = 0
        food_count = 0
        water_count = 0
        for eid, entity in self.world.entities.items():
            if self.world.get_component(entity, FoodComponent):
                food_count += 1

        from human.components.basic.human_component import HumanComponent
        for entity, _ in self.world.query_components(HumanComponent):
            human_count += 1

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
            'civilization_stage': civilization_status['stage'],
            'civilization_metrics': civilization_status.get('metrics', {}),
            'discovered_technologies': civilization_status.get('discovered_technologies', [])
        }

    def run_simulation(self, steps: int = 100, delta_hours: float = 1.0, verbose: bool = True):
        """
        运行模拟

        Args:
            steps: 运行步数
            delta_hours: 每步时间增量
            verbose: 是否打印详细信息
        """
        print(f"[SimulationLoop] 开始运行模拟：{steps} 步，每步 {delta_hours} 小时")

        for step in range(steps):
            if verbose and step % 20 == 0:
                stats = self.get_stats()
                print(f"步 {step}/{steps} - 实体:{stats['total_entities']} "
                      f"人口:{stats['human_count']} 食物:{stats['food_count']} "
                      f"文明:{stats['civilization_stage']} "
                      f"速度:{stats['steps_per_second']:.1f}步/秒")
            
            # 每50步打印一次人类行为状态
            if verbose and step % 50 == 0 and step > 0:
                self._debug_human_status()

            self.update(delta_hours)

        print("[SimulationLoop] 模拟完成")
        final_stats = self.get_stats()
        print(f"最终统计: 实体={final_stats['total_entities']} "
              f"人口={final_stats['human_count']} "
              f"文明={final_stats['civilization_stage']}")

        # Final debug
        self._debug_human_status()

    def _debug_human_status(self):
        """打印所有人类的完整状态"""
        from human.components.basic.human_component import HumanComponent
        from human.components.cognitive.intent_component import IntentComponent
        from human.components.action.action_component import ActionComponent, ActionType
        from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
        from space.space_component import SpaceComponent

        print(f"\n--- 人类状态 (步 {self.step_count}) ---")
        for entity, (hc, intent, action, needs, space) in self.world.get_components(
            HumanComponent, IntentComponent, ActionComponent,
            PhysiologyNeedsComponent, SpaceComponent
        ):
            print(f"  H{entity.id} @({space.x:.0f},{space.y:.0f}) "
                  f"意:{intent.intent.name} 动:{action.current_action.name} "
                  f"队:{len(action.action_queue)} "
                  f"饥:{needs.hunger:.0f} 渴:{needs.thirst:.0f} 能:{needs.energy:.0f}")
        print("---\n")


def main():
    """主函数"""
    print("=== ECS 世界模拟系统 ===")

    # 创建世界
    world = World()

    # 创建模拟循环
    simulation = SimulationLoop(world)

    # 创建初始资源（更密集分布）
    simulation.create_initial_resources(food_count=60, water_count=25)

    # 创建初始人口（更多人类）
    simulation.create_initial_population(human_count=10)

    # 运行模拟（更多步，验证行为触发）
    simulation.run_simulation(steps=300, delta_hours=1.0, verbose=True)


if __name__ == "__main__":
    main()
