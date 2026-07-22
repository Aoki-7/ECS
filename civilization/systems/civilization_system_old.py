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
    tick_interval = 20  # 每20帧执行一次
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

        # 文明发展多维度指标（0-100分）
        self.civilization_metrics = {
            # 基础维度
            'population': 0,               # 人口数量
            'population_density': 0.0,     # 人口密度
            'average_lifespan': 0.0,       # 平均寿命
            
            # 技术维度
            'technology_count': 0,         # 已解锁技术数量
            'technology_complexity': 0.0,  # 技术复杂度
            'tool_level': 0.0,             # 生产工具水平
            
            # 生产维度
            'resource_output_per_capita': 0.0,  # 人均资源产量
            'surplus_product_rate': 0.0,   # 剩余产品率
            'production_efficiency': 0.0,  # 生产效率
            
            # 社会维度
            'social_organization': 0.0,    # 社会组织度
            'division_of_labor_level': 0.0,# 分工程度
            'social_stability': 0.0,       # 社会稳定度
            
            # 文化维度
            'culture_points': 0.0,         # 文化积累点数
            'value_consensus': 0.0,        # 价值观共识度
            'tradition_count': 0,          # 传统数量
            
            # 基础设施维度
            'building_count': 0,           # 建筑数量
            'public_facility_level': 0.0,  # 公共设施水平
            'settlement_scale': 0.0,       # 定居点规模
        }

        # 文明阶段评分标准（总分0-1000）
        self.stage_score_ranges = {
            "hunter_gatherer": (0, 100),     # 狩猎采集：0-100分
            "agricultural": (100, 300),      # 农业社会：100-300分
            "bronze_age": (300, 500),        # 青铜时代：300-500分
            "iron_age": (500, 700),          # 铁器时代：500-700分
            "classical_age": (700, 850),     # 古典时代：700-850分
            "medieval_age": (850, 950),      # 中世纪：850-950分
            "industrial_age": (950, 1000),   # 工业时代：950-1000分
        }
        
        # 核心技术对应阶段（解锁这些技术会大幅提升对应维度评分，自然进入对应阶段）
        self.core_tech_stage_map = {
            "basic_farming": "agricultural",
            "bronze_smelting": "bronze_age",
            "iron_smelting": "iron_age",
            "masonry": "classical_age",
            "steelmaking": "medieval_age",
            "steam_power": "industrial_age",
        }

        # 文明阶段（自动匹配当前评分，无需手动设置）
        self.civilization_stage = "hunter_gatherer"  # 初始狩猎采集
        self._last_stage = "hunter_gatherer"

    def update(self, world: World, dt: float) -> None:
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
        """多维度更新文明发展指标"""
        # === 基础维度 ===
        # 人口
        human_count = 0
        total_age = 0.0
        from human.components.physiological.health_component import HealthComponent
        for entity, (human, health) in world.get_components([HumanComponent, HealthComponent]):
            human_count += 1
            total_age += human.age
        
        self.civilization_metrics['population'] = human_count
        self.civilization_metrics['average_lifespan'] = total_age / max(1, human_count) / 365 * 100  # 换算成0-100分
        self.civilization_metrics['population_density'] = min(100, human_count / 100 * 100)  # 假设世界100x100

        # === 技术维度 ===
        discovered_techs = list(self.technology.discovered_technologies.keys())
        tech_count = len(discovered_techs)
        self.civilization_metrics['technology_count'] = tech_count
        # 技术复杂度：根据最高技术的等级计算
        max_tech_level = max([tech.get('level', 1) for tech in self.technology.discovered_technologies.values()] or [1])
        self.civilization_metrics['technology_complexity'] = min(100, max_tech_level * 10)
        # 工具水平：是否解锁了金属工具
        tool_level = 10 if 'stone_tools' in discovered_techs else 0
        tool_level += 30 if 'bronze_tools' in discovered_techs else 0
        tool_level += 40 if 'iron_tools' in discovered_techs else 0
        tool_level += 20 if 'steel_tools' in discovered_techs else 0
        self.civilization_metrics['tool_level'] = tool_level

        # === 生产维度 ===
        total_food = 0
        total_production = 0
        from human.components.economic.inventory.inventory_component import InventoryComponent
        for entity, inv in world.get_components(InventoryComponent):
            total_food += inv.get_resource('food', 0)
            total_production += inv.get_total_value()
        
        self.civilization_metrics['resource_output_per_capita'] = min(100, total_production / max(1, human_count) / 10)
        self.civilization_metrics['surplus_product_rate'] = min(100, max(0, (total_food - human_count * 10) / max(1, human_count * 10) * 100))
        self.civilization_metrics['production_efficiency'] = self.civilization_metrics['tool_level'] * 0.8 + self.civilization_metrics['technology_complexity'] * 0.2

        # === 社会维度 ===
        total_relations = 0
        total_groups = 0
        from human.components.social.social_component import SocialComponent
        for entity, social in world.get_components(SocialComponent):
            total_relations += len(social.relations)
            if social.social_group_id != -1:
                total_groups += 1
        
        self.civilization_metrics['division_of_labor_level'] = min(100, len(discovered_techs) / 5 * 100)
        self.civilization_metrics['social_organization'] = min(100, total_groups / max(1, human_count) * 100)
        self.civilization_metrics['social_stability'] = 100 - min(100, self.trade.conflict_count / max(1, human_count) * 50)

        # === 文化维度 ===
        from civilization.components.culture_component import CultureComponent
        culture = world.get_world_component(CultureComponent)
        if culture:
            self.civilization_metrics['culture_points'] = min(100, culture.culture_points / 100)
            self.civilization_metrics['value_consensus'] = min(100, culture.consensus * 100)
            self.civilization_metrics['tradition_count'] = min(100, len(culture.traditions) * 10)
        else:
            self.civilization_metrics['culture_points'] = 0
            self.civilization_metrics['value_consensus'] = 0
            self.civilization_metrics['tradition_count'] = 0

        # === 基础设施维度 ===
        from building.components.building_component import BuildingComponent
        building_count = 0
        public_building_count = 0
        for entity, building in world.get_components(BuildingComponent):
            building_count += 1
            if building.type in ['house', 'farm', 'mine', 'workshop']:
                public_building_count += 1
        
        self.civilization_metrics['building_count'] = min(100, building_count * 2)
        self.civilization_metrics['public_facility_level'] = min(100, public_building_count * 5)
        self.civilization_metrics['settlement_scale'] = min(100, building_count / max(1, human_count) * 100)

    def _calculate_civilization_score(self) -> float:
        """计算文明总评分（0-1000分）"""
        weights = {
            # 基础维度：15%权重
            'population': 0.05,
            'population_density': 0.05,
            'average_lifespan': 0.05,
            
            # 技术维度：30%权重（核心驱动力）
            'technology_count': 0.1,
            'technology_complexity': 0.12,
            'tool_level': 0.08,
            
            # 生产维度：20%权重
            'resource_output_per_capita': 0.07,
            'surplus_product_rate': 0.07,
            'production_efficiency': 0.06,
            
            # 社会维度：15%权重
            'social_organization': 0.05,
            'division_of_labor_level': 0.05,
            'social_stability': 0.05,
            
            # 文化维度：10%权重
            'culture_points': 0.03,
            'value_consensus': 0.04,
            'tradition_count': 0.03,
            
            # 基础设施维度：10%权重
            'building_count': 0.03,
            'public_facility_level': 0.04,
            'settlement_scale': 0.03,
        }
        
        total_score = 0.0
        for metric, value in self.civilization_metrics.items():
            if metric in weights:
                total_score += value * weights[metric]
        
        # 核心技术加成：解锁核心技术直接加对应阶段的基础分
        for tech, stage in self.core_tech_stage_map.items():
            if tech in self.technology.discovered_technologies:
                base_score = self.stage_score_ranges[stage][0]
                if total_score < base_score:
                    total_score = base_score  # 解锁核心技术直接达到对应阶段最低分
        
        return total_score

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
              "bronze_smelting" in self.technology.discovered_technologies):
            self.civilization_stage = "bronze_age"
            self._on_stage_transition("bronze_age", world)

        # 青铜时代 -> 铁器时代
        elif (current_stage == "bronze_age" and
              self.civilization_metrics['technology_level'] >= 6.0 and
              "iron_smelting" in self.technology.discovered_technologies):
            self.civilization_stage = "iron_age"
            self._on_stage_transition("iron_age", world)
        
        # 铁器时代 -> 古典时代
        elif (current_stage == "iron_age" and
              self.civilization_metrics['technology_level'] >= 10.0 and
              "masonry" in self.technology.discovered_technologies and
              "anatomy" in self.technology.discovered_technologies and
              self.civilization_metrics['population'] >= 50):
            self.civilization_stage = "classical_age"
            self._on_stage_transition("classical_age", world)
        
        # 古典时代 -> 中世纪
        elif (current_stage == "classical_age" and
              self.civilization_metrics['technology_level'] >= 14.0 and
              "steelmaking" in self.technology.discovered_technologies and
              "gunpowder" in self.technology.discovered_technologies and
              self.civilization_metrics['population'] >= 100):
            self.civilization_stage = "medieval_age"
            self._on_stage_transition("medieval_age", world)
        
        # 中世纪 -> 工业时代
        elif (current_stage == "medieval_age" and
              self.civilization_metrics['technology_level'] >= 18.0 and
              "steam_power" in self.technology.discovered_technologies and
              "mechanized_farming" in self.technology.discovered_technologies and
              self.civilization_metrics['population'] >= 200):
            self.civilization_stage = "industrial_age"
            self._on_stage_transition("industrial_age", world)

    def _on_stage_transition(self, new_stage: str, world: World):
        """文明阶段转换事件"""
        logger.info(f"[CivilizationSystem] Civilization advanced to: {new_stage}")
        # 发送到事件总线
        if hasattr(world, 'event_bus'):
            world.event_bus.publish("civilization_stage_upgraded", {"new_stage": new_stage})

        # 触发阶段特定事件
        if new_stage == "agricultural":
            # 解锁农业相关行为
            logger.info("[CivilizationSystem] 农业社会解锁：种植、养殖、定居点")
            self._unlock_agricultural_behaviors(world)
        elif new_stage == "bronze_age":
            # 解锁金属加工
            logger.info("[CivilizationSystem] 青铜时代解锁：青铜工具、武器、大型建筑")
            self._unlock_metalworking_behaviors(world)
        elif new_stage == "iron_age":
            # 解锁高级建造
            logger.info("[CivilizationSystem] 铁器时代解锁：铁制工具、大规模农业、坚固建筑")
            self._unlock_advanced_construction(world)
        elif new_stage == "classical_age":
            # 解锁古典时代特性
            logger.info("[CivilizationSystem] 古典时代解锁：大型城市、文化、医学、哲学")
            # 人口上限提升50%
            self.civilization_metrics['population_cap'] = self.civilization_metrics.get('population_cap', 100) * 1.5
        elif new_stage == "medieval_age":
            # 解锁中世纪特性
            logger.info("[CivilizationSystem] 中世纪解锁：封建制度、火药、大型战争、贸易网络")
            # 经济复杂度提升100%
            self.civilization_metrics['economic_complexity'] *= 2.0
        elif new_stage == "industrial_age":
            # 解锁工业时代特性
            logger.info("[CivilizationSystem] 工业时代解锁：机械化生产、蒸汽动力、铁路、大规模工业")
            # 资源采集效率提升100%
            self.civilization_metrics['resource_gathering_multiplier'] = 2.0

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