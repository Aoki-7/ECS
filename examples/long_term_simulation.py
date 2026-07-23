#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长时间模拟脚本：运行足够长的时间来观察文明的演进，测试所有新功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import logging
import random
from typing import Dict, List
from core.world import World
from core.components.world_config_component import WorldConfigComponent
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from human.components.cognitive.memory_component import MemoryComponent
from space.space_component import SpaceComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from resource.components.resource_component import ResourceComponent
from human.rl import (
    HierarchicalRLIntentSystem,
    BehaviorVisualizer,
    ComplexTaskSystem,
    SocialStructureSystem,
    CulturalInheritanceSystem,
    KnowledgeType
)
from human.rl.social_interaction import SocialInteractionSystem

# 配置日志：减少日志输出以提高性能
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LongTermSimulation:
    """长时间模拟：观察文明演进"""

    def __init__(self, num_humans: int = 50, num_resources: int = 100, steps: int = 5000):
        """
        初始化模拟
        Args:
            num_humans: 初始人类数量
            num_resources: 初始资源数量
            steps: 模拟步数
        """
        self.num_humans = num_humans
        self.num_resources = num_resources
        self.steps = steps
        self.world = World()
        self.population_history = []
        self.group_history = []
        self.knowledge_history = []
        self.setup_world()
        self.setup_systems()
        self.simulation_start_time = time.time()

    def setup_world(self):
        """设置世界"""
        logger.info("初始化世界...")
        # 添加世界配置
        world_entity = self.world.get_world_entity()
        self.world.add_component(world_entity, WorldConfigComponent(
            use_rl_intent=True,
            rl_training=True,
            map_width=200,
            map_height=200
        ))

        # 创建人类实体
        logger.info(f"创建 {self.num_humans} 个人类实体...")
        for i in range(self.num_humans):
            self._create_human()

        # 创建资源实体
        logger.info(f"创建 {self.num_resources} 个资源实体...")
        resource_types = ["food", "water", "wood", "stone", "ore"]
        for i in range(self.num_resources):
            self._create_resource(random.choice(resource_types))

    def _create_human(self):
        """创建单个人类实体"""
        entity_id = self.world.create_entity()
        self.world.add_component(entity_id, HumanComponent())
        self.world.add_component(entity_id, PhysiologyNeedsComponent(
            hunger=random.uniform(30, 70),
            thirst=random.uniform(30, 70),
            energy=random.uniform(50, 100),
            health=100.0,
            social=random.uniform(30, 70)
        ))
        self.world.add_component(entity_id, IntentComponent())
        self.world.add_component(entity_id, SpaceComponent(
            x=random.uniform(0, 200),
            y=random.uniform(0, 200)
        ))
        self.world.add_component(entity_id, MemoryComponent())
        self.world.add_component(entity_id, SkillComponent())
        self.world.add_component(entity_id, InventoryComponent())
        return entity_id

    def _create_resource(self, resource_type: str):
        """创建单个资源实体"""
        entity_id = self.world.create_entity()
        self.world.add_component(entity_id, ResourceComponent(
            resource_type=resource_type,
            amount=random.uniform(50, 200)
        ))
        self.world.add_component(entity_id, SpaceComponent(
            x=random.uniform(0, 200),
            y=random.uniform(0, 200)
        ))
        return entity_id

    def setup_systems(self):
        """设置系统"""
        logger.info("初始化系统...")
        # 添加分层RL意图系统
        self.rl_system = HierarchicalRLIntentSystem(training=True)
        self.world.add_system(self.rl_system)

        # 添加行为可视化系统
        self.visualizer = BehaviorVisualizer()
        self.world.add_system(self.visualizer)

        # 添加复杂任务系统
        self.task_system = ComplexTaskSystem()
        self.world.add_system(self.task_system)

        # 添加社会结构系统
        self.social_system = SocialStructureSystem()
        self.world.add_system(self.social_system)

        # 添加文化传承系统
        self.cultural_system = CulturalInheritanceSystem()
        self.world.add_system(self.cultural_system)

        # 添加社会互动系统
        self.interaction_system = SocialInteractionSystem()
        self.world.add_system(self.interaction_system)

        # 给人类实体添加初始知识
        logger.info("给人类实体添加初始知识...")
        for e, (human, skill) in self.world.get_components(HumanComponent, SkillComponent):
            entity_id = e.id
            # 给每个实体随机分配一些初始知识
            initial_knowledge = {}
            for knowledge_type in KnowledgeType:
                if random.random() < 0.3:  # 30%的概率拥有某种知识
                    initial_knowledge[knowledge_type] = random.uniform(0.5, 2.0)
            self.cultural_system.entity_knowledge[entity_id] = initial_knowledge

    def _handle_population_growth(self):
        """处理人口增长：新人类诞生"""
        # 每100步有一定概率诞生新人类
        if random.random() < 0.1:  # 10%概率
            new_human_id = self._create_human()
            logger.info(f"[Population] 新人类诞生: 实体{new_human_id}")

            # 给新人类一些初始知识（从父母或社会继承）
            if self.cultural_system.entity_knowledge:
                # 随机选择一个现有实体作为"父母"
                parent_id = random.choice(list(self.cultural_system.entity_knowledge.keys()))
                parent_knowledge = self.cultural_system.entity_knowledge[parent_id]
                # 继承父母的一部分知识
                inherited_knowledge = {}
                for knowledge_type, level in parent_knowledge.items():
                    inherited_knowledge[knowledge_type] = level * random.uniform(0.3, 0.7)
                self.cultural_system.entity_knowledge[new_human_id] = inherited_knowledge

    def _handle_resource_regeneration(self):
        """处理资源再生"""
        # 每50步补充资源
        if random.random() < 0.2:  # 20%概率
            resource_type = random.choice(["food", "water", "wood", "stone", "ore"])
            new_resource_id = self._create_resource(resource_type)
            logger.debug(f"[Resource] 新资源生成: {resource_type} at 实体{new_resource_id}")

    def run_simulation(self):
        """运行模拟"""
        logger.info(f"开始长时间模拟，共 {self.steps} 步...")
        logger.info("=" * 60)

        for step in range(self.steps):
            # 更新世界
            self.world.update(1.0)

            # 处理人口增长和资源再生
            self._handle_population_growth()
            self._handle_resource_regeneration()

            # 记录历史数据
            if step % 100 == 0:
                self._record_history(step)

            # 每500步打印一次统计信息
            if step % 500 == 0 and step > 0:
                self.print_stats(step)

            # 每1000步导出一次行为数据
            if step % 1000 == 0 and step > 0:
                self.export_data(step)

        # 模拟结束，打印最终统计
        logger.info("=" * 60)
        logger.info("模拟结束！")
        self.print_final_stats()
        self._print_evolution_analysis()

    def _record_history(self, step: int):
        """记录历史数据"""
        humans = [e.id for e, _ in self.world.get_components(HumanComponent)]
        self.population_history.append((step, len(humans)))
        self.group_history.append((step, len(self.social_system.groups)))
        self.knowledge_history.append((step, len(self.cultural_system.knowledge)))

    def print_stats(self, step: int):
        """打印统计信息"""
        logger.info(f"\n步数: {step}/{self.steps}")
        logger.info(f"运行时间: {time.time() - self.simulation_start_time:.1f}秒")

        # 人口统计
        humans = [e.id for e, _ in self.world.get_components(HumanComponent)]
        logger.info(f"人口数量: {len(humans)}")

        # 社会结构统计
        groups = self.social_system.groups
        group_types = {}
        for group in groups.values():
            group_types[group.group_type] = group_types.get(group.group_type, 0) + 1
        logger.info(f"社会群体数量: {len(groups)} {group_types}")

        # 文化传承统计
        knowledge = self.cultural_system.knowledge
        traditions = self.cultural_system.traditions
        logger.info(f"知识数量: {len(knowledge)}")
        logger.info(f"文化传统数量: {len(traditions)}")

        # 任务统计
        tasks = self.task_system.tasks
        logger.info(f"活跃任务数量: {len(tasks)}")

        # 社会关系统计
        relations = self.interaction_system.group_relations
        if relations:
            avg_relation = sum(relations.values()) / len(relations)
            logger.info(f"平均社会关系: {avg_relation:.1f}")

        # RL智能体统计
        rl_stats = self.rl_system.get_stats()
        logger.info(f"RL智能体统计: 高层平均奖励: {rl_stats['high_level_avg_reward']:.2f}, 低层平均奖励: {rl_stats['low_level_avg_reward']:.2f}")

    def export_data(self, step: int):
        """导出数据"""
        path = f"data/simulation_step_{step}.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.visualizer.export_behavior_data(path)
        logger.info(f"行为数据已导出到 {path}")

    def print_final_stats(self):
        """打印最终统计"""
        logger.info("\n最终统计:")
        logger.info(f"总运行时间: {time.time() - self.simulation_start_time:.1f}秒")

        # 人口统计
        humans = [e.id for e, _ in self.world.get_components(HumanComponent)]
        logger.info(f"最终人口数量: {len(humans)}")

        # 社会结构统计
        groups = self.social_system.groups
        logger.info(f"最终社会群体数量: {len(groups)}")
        role_distribution = self.social_system.get_role_distribution()
        logger.info(f"角色分布: {role_distribution}")

        # 文化传承统计
        knowledge = self.cultural_system.knowledge
        traditions = self.cultural_system.traditions
        knowledge_distribution = self.cultural_system.get_knowledge_distribution()
        logger.info(f"最终知识数量: {len(knowledge)}")
        logger.info(f"知识分布: {knowledge_distribution}")
        logger.info(f"最终文化传统数量: {len(traditions)}")

        # 社会关系统计
        relations = self.interaction_system.group_relations
        if relations:
            avg_relation = sum(relations.values()) / len(relations)
            logger.info(f"平均社会关系: {avg_relation:.1f}")
            positive_relations = sum(1 for r in relations.values() if r > 0)
            negative_relations = sum(1 for r in relations.values() if r < 0)
            logger.info(f"正面关系: {positive_relations}, 负面关系: {negative_relations}")

        # 任务统计
        tasks = self.task_system.tasks
        logger.info(f"最终活跃任务数量: {len(tasks)}")

        # RL智能体统计
        rl_stats = self.rl_system.get_stats()
        logger.info(f"最终RL智能体统计:")
        logger.info(f"  高层平均奖励: {rl_stats['high_level_avg_reward']:.2f}, 探索率: {rl_stats['high_level_epsilon']:.2f}")
        logger.info(f"  低层平均奖励: {rl_stats['low_level_avg_reward']:.2f}, 探索率: {rl_stats['low_level_epsilon']:.2f}")
        logger.info(f"  协作平均奖励: {rl_stats['cooperation_avg_reward']:.2f}, 探索率: {rl_stats['cooperation_epsilon']:.2f}")

        # 行为可视化统计
        logger.info(f"总行为记录数: {len(self.visualizer.behavior_records)}")
        logger.info(f"协作网络数: {len(self.visualizer.cooperation_networks)}")

    def _print_evolution_analysis(self):
        """打印演进分析"""
        logger.info("\n" + "=" * 60)
        logger.info("文明演进分析")
        logger.info("=" * 60)

        # 人口演进
        logger.info("\n人口演进:")
        for step, pop in self.population_history[::10]:  # 每10个数据点打印一次
            logger.info(f"  步数 {step}: {pop} 人")

        # 社会结构演进
        logger.info("\n社会结构演进:")
        for step, groups in self.group_history[::10]:
            logger.info(f"  步数 {step}: {groups} 个群体")

        # 知识演进
        logger.info("\n知识演进:")
        for step, knowledge in self.knowledge_history[::10]:
            logger.info(f"  步数 {step}: {knowledge} 个知识")

        # 最终社会结构详情
        logger.info("\n最终社会结构详情:")
        for group_id, group in self.social_system.groups.items():
            logger.info(f"\n  {group.name} (ID: {group_id})")
            logger.info(f"    类型: {group.group_type}")
            logger.info(f"    成员数: {len(group.members)}")
            logger.info(f"    领导者: {group.leader_id}")
            logger.info(f"    角色分布:")
            role_counts = {}
            for role in group.roles.values():
                role_counts[role.name] = role_counts.get(role.name, 0) + 1
            for role_name, count in role_counts.items():
                logger.info(f"      {role_name}: {count} 人")

if __name__ == "__main__":
    # 创建模拟：50个人类，100个资源，2000步
    simulation = LongTermSimulation(num_humans=50, num_resources=100, steps=2000)
    # 运行模拟
    simulation.run_simulation()