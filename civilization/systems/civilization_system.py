#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:civilization_system.py
@说明:文明系统主控制器 - 协调所有文明子系统的系统
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

import logging

from core.system import System
from core.world import World
from typing import List

logger = logging.getLogger(__name__)

from human.components.basic.human_component import HumanComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.social.social_component import SocialComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent

from .resource_gathering_system import ResourceGatheringSystem
from .construction_system import ConstructionSystem
from .trade_system import TradeSystem
from .technology_system import TechnologySystem


class CivilizationSystem(System):
    """
    文明系统主控制器

    功能：
    - 协调资源采集、建造、交易、技术进步等子系统
    - 管理文明发展阶段
    - 跟踪社会指标（人口、技术水平、经济规模等）
    - 触发文明事件和里程碑
    """

    def __init__(self):
        self.resource_gathering = ResourceGatheringSystem()
        self.construction = ConstructionSystem()
        self.trade = TradeSystem()
        self.technology = TechnologySystem()

        # 文明发展指标
        self.civilization_metrics = {
            'population': 0,
            'technology_level': 1.0,
            'economic_complexity': 1.0,
            'social_organization': 1.0,
            'resource_diversity': 1.0
        }

        # 文明阶段
        self.civilization_stage = "hunter_gatherer"  # 狩猎采集

    def update(self, world: World, dt: float):
        """更新文明系统"""
        # 更新子系统
        self.resource_gathering.update(world, dt)
        self.construction.update(world, dt)
        self.trade.update(world, dt)
        self.technology.update(world, dt)

        # 更新文明指标
        self._update_civilization_metrics(world)

        # 检查文明阶段转换
        self._check_stage_transition(world)

        # 触发文明事件
        self._trigger_civilization_events(world, dt)

    def _update_civilization_metrics(self, world: World):
        """更新文明发展指标"""
        # 计算人口
        human_count = 0
        for entity, _ in world.get_components(HumanComponent):  # 需要导入HumanComponent
            human_count += 1
        self.civilization_metrics['population'] = human_count

        # 计算技术水平
        discovered_techs = len(self.technology.discovered_technologies)
        self.civilization_metrics['technology_level'] = 1.0 + discovered_techs * 0.5

        # 计算经济复杂度
        total_wealth = 0.0
        trade_count = 0
        for entity, components in world.get_components(EconomyComponent):
            economy = components[0]  # EconomyComponent是第一个组件
            total_wealth += economy.wealth
            # 计算交易历史
            memory = world.get_component(entity, MemoryComponent)
            if memory:
                trade_experiences = [event for event in memory.events if event.get('type') == 'trade']
                trade_count += len(trade_experiences)

        self.civilization_metrics['economic_complexity'] = 1.0 + (total_wealth * 0.001) + (trade_count * 0.01)

        # 计算社会组织度
        relationship_count = 0
        for entity, components in world.get_components(SocialComponent):
            social = components[0]  # SocialComponent是第一个组件
            relationship_count += len(social.relations)

        self.civilization_metrics['social_organization'] = 1.0 + (relationship_count * 0.1)

        # 计算资源多样性
        resource_types = set()
        for entity, components in world.get_components(InventoryComponent):
            inventory = components[0]  # InventoryComponent是第一个组件
            # 简化：假设库存中有物品就认为有该资源类型
            if len(inventory.items) > 0:
                resource_types.add('items')  # 简化为有物品

        self.civilization_metrics['resource_diversity'] = len(resource_types)

    def _check_stage_transition(self, world: World):
        """检查文明阶段转换"""
        current_stage = self.civilization_stage

        # 狩猎采集 -> 农业社会
        if (current_stage == "hunter_gatherer" and
            self.civilization_metrics['technology_level'] >= 2.0 and
            "basic_farming" in self.technology.discovered_technologies):
            self.civilization_stage = "agricultural"
            self._on_stage_transition("agricultural", world)

        # 农业社会 -> 青铜时代
        elif (current_stage == "agricultural" and
              self.civilization_metrics['technology_level'] >= 4.0 and
              "metal_tools" in self.technology.discovered_technologies):
            self.civilization_stage = "bronze_age"
            self._on_stage_transition("bronze_age", world)

        # 青铜时代 -> 铁器时代
        elif (current_stage == "bronze_age" and
              self.civilization_metrics['technology_level'] >= 6.0 and
              self.civilization_metrics['economic_complexity'] >= 3.0):
            self.civilization_stage = "iron_age"
            self._on_stage_transition("iron_age", world)

    def _on_stage_transition(self, new_stage: str, world: World):
        """文明阶段转换事件"""
        logger.info(f"[CivilizationSystem] Civilization advanced to: {new_stage}")

        # 触发阶段特定事件
        if new_stage == "agricultural":
            # 解锁农业相关行为
            self._unlock_agricultural_behaviors(world)
        elif new_stage == "bronze_age":
            # 解锁金属加工
            self._unlock_metalworking_behaviors(world)
        elif new_stage == "iron_age":
            # 解锁高级建造
            self._unlock_advanced_construction(world)

    def _trigger_civilization_events(self, world: World, dt: float):
        """触发文明事件"""
        # 人口里程碑
        if self.civilization_metrics['population'] >= 10 and not hasattr(self, '_population_milestone_10'):
            self._population_milestone_10 = True
            self._trigger_population_event(10, world)

        if self.civilization_metrics['population'] >= 50 and not hasattr(self, '_population_milestone_50'):
            self._population_milestone_50 = True
            self._trigger_population_event(50, world)

        # 技术里程碑
        if len(self.technology.discovered_technologies) >= 3 and not hasattr(self, '_tech_milestone_3'):
            self._tech_milestone_3 = True
            self._trigger_technology_event(3, world)

    def _trigger_population_event(self, milestone: int, world: World):
        """触发人口里程碑事件"""
        logger.info(f"[CivilizationSystem] Population milestone reached: {milestone} humans")

        # 增加社会复杂度
        self.civilization_metrics['social_organization'] *= 1.2

    def _trigger_technology_event(self, milestone: int, world: World):
        """触发技术里程碑事件"""
        logger.info(f"[CivilizationSystem] Technology milestone reached: {milestone} technologies")

        # 增加技术水平
        self.civilization_metrics['technology_level'] *= 1.1

    def _unlock_agricultural_behaviors(self, world: World):
        """解锁农业行为"""
        logger.info("[CivilizationSystem] Agricultural behaviors unlocked")
        # 这里可以添加农业相关的行为解锁逻辑

    def _unlock_metalworking_behaviors(self, world: World):
        """解锁金属加工行为"""
        logger.info("[CivilizationSystem] Metalworking behaviors unlocked")
        # 这里可以添加金属加工相关的行为解锁逻辑

    def _unlock_advanced_construction(self, world: World):
        """解锁高级建造"""
        logger.info("[CivilizationSystem] Advanced construction unlocked")
        # 这里可以添加高级建造相关的行为解锁逻辑

    def get_civilization_status(self) -> dict:
        """获取文明状态"""
        return {
            'stage': self.civilization_stage,
            'metrics': self.civilization_metrics.copy(),
            'discovered_technologies': list(self.technology.discovered_technologies)
        }