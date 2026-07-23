#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:civilization_system.py
@说明:文明系统主控制器 - 协调所有文明子系统的系统
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:2.0 - 多维度自动评分，技术驱动阶段
'''

import logging

from core.system import System
from core.world import World
from typing import List

logger = logging.getLogger(__name__)

from human.components.basic.human_component import HumanComponent
from human.components.skill.human_tech_skill_component import HumanTechSkillComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.social.social_component import SocialComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent

from .resource_gathering_system import ResourceGatheringSystem
from .construction_system import ConstructionSystem
from .trade_system import TradeSystem
from .human_tech_innovation_system import HumanTechInnovationSystem as TechnologySystem


class CivilizationSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    文明系统主控制器

    功能：
    - 协调资源采集、建造、交易、技术进步等子系统
    - 多维度自动评估文明发展水平
    - 技术驱动阶段升级/降级，阶段是发展结果而非前提
    - 跟踪社会指标（人口、技术水平、经济规模等）
    - 触发文明事件和里程碑
    """

    def __init__(self):
        self.resource_gathering = ResourceGatheringSystem()
        self.construction = ConstructionSystem()
        self.trade = TradeSystem()
        self.technology = None  # 延迟从world获取，确保全局唯一实例

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
        
        # 核心领域技术加成：当某领域技术发展达到一定程度，直接给对应阶段基础分
        # 技术名动态，但领域和阶段有对应关系，数量代表发展水平
        self.core_tech_stage_map = {
            "agricultural": ("农业", 1),      # 有1个以上农业技术 → 农业社会基础分
            "bronze_age": ("生产", 2),        # 2个以上生产技术 → 青铜时代基础分
            "iron_age": ("材料", 3),          # 3个以上材料技术 → 铁器时代基础分
            "classical_age": ("建筑", 3),     # 3个以上建筑技术 → 古典时代基础分
            "medieval_age": ("社会", 4),      # 4个以上社会技术 → 中世纪基础分
            "industrial_age": ("能源", 2),    # 2个以上能源技术 → 工业时代基础分
        }
        
        self._domain_counts = {}

        # 文明阶段（自动匹配当前评分，无需手动设置）
        self.civilization_stage = "hunter_gatherer"  # 初始狩猎采集
        self._last_stage = "hunter_gatherer"

    def update(self, world: World, dt: float) -> None:
        """更新文明系统"""
        # 延迟获取全局唯一的技术系统实例
        if self.technology is None:
            self.technology = world.get_system("HumanTechInnovationSystem")
            if self.technology is None:
                self.technology = world.get_system(TechnologySystem)
        
        # 更新子系统
        self.resource_gathering.update(world, dt)
        self.construction.update(world, dt)
        self.trade.update(world, dt)
        if self.technology:
            self.technology.update(world, dt)

        # 更新文明指标
        self._update_civilization_metrics(world)

        # 检查文明阶段转换（自动升级/降级）
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
        self.civilization_metrics['average_lifespan'] = min(100, total_age / max(1, human_count) / 365 * 100)  # 换算成0-100分
        self.civilization_metrics['population_density'] = min(100, human_count / 100 * 100)  # 假设世界100x100

        # === 技术维度 ===
        # 从人类个体的技术技能掌握情况统计文明技术水平
        total_skills = 0
        total_skill_level = 0.0
        max_skill_level = 0.0
        domain_counts = {}
        top_innovators = 0
        
        for entity, tech_skill in world.get_components(HumanTechSkillComponent):
            if not tech_skill.skills:
                continue
            total_skills += len(tech_skill.skills)
            for skill_name, skill_data in tech_skill.skills.items():
                level = tech_skill.get_skill_level(skill_name)
                total_skill_level += level
                max_skill_level = max(max_skill_level, level)
                domain = skill_data.get('domain', 'general')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            if tech_skill.innovation_count > 0:
                top_innovators += 1
        
        # 技术数量：人均掌握技能数
        self.civilization_metrics['technology_count'] = min(100, total_skills / max(1, human_count) * 10)
        # 技术复杂度：平均技能等级
        avg_level = total_skill_level / max(1, total_skills) if total_skills > 0 else 0
        self.civilization_metrics['technology_complexity'] = min(100, avg_level * 100)
        # 工具水平：根据生产/材料/建筑领域技能数量
        production_skills = domain_counts.get('生产', 0) + domain_counts.get('材料', 0)
        construction_skills = domain_counts.get('建筑', 0)
        self.civilization_metrics['tool_level'] = min(100, (production_skills * 10 + construction_skills * 5 + max_skill_level * 20))
        
        # 存储领域统计，供阶段评分使用
        self._domain_counts = domain_counts

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
            if building.type in ['house', 'farm', 'mine', 'workshop', 'temple']:
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
        
        # 核心领域技术加成：某领域技术达到数量阈值，直接给对应阶段基础分
        for stage, (domain, threshold) in self.core_tech_stage_map.items():
            domain_count = self._domain_counts.get(domain, 0)
            if domain_count >= threshold:
                base_score = self.stage_score_ranges[stage][0]
                if total_score < base_score:
                    total_score = base_score  # 该领域技术成熟，直接达到对应阶段最低分
        
        return total_score

    def _check_stage_transition(self, world: World):
        """根据当前评分自动匹配文明阶段（支持升级和降级）"""
        total_score = self._calculate_civilization_score()
        
        # 匹配当前阶段
        new_stage = self.civilization_stage
        for stage, (min_score, max_score) in self.stage_score_ranges.items():
            if min_score <= total_score < max_score:
                new_stage = stage
                break
        
        # 阶段发生变化
        if new_stage != self._last_stage:
            # 触发阶段转换事件（支持升级和降级）
            self._on_stage_transition(world, self._last_stage, new_stage, total_score)
            self._last_stage = new_stage
            self.civilization_stage = new_stage

    def _on_stage_transition(self, world: World, old_stage: str, new_stage: str, score: float):
        """阶段转换事件通知（仅做日志和事件触发，不解锁任何东西，技术已经提前解锁）"""
        stage_name_map = {
            "hunter_gatherer": "狩猎采集",
            "agricultural": "农业社会",
            "bronze_age": "青铜时代",
            "iron_age": "铁器时代",
            "classical_age": "古典时代",
            "medieval_age": "中世纪",
            "industrial_age": "工业时代",
        }
        
        # 判断是升级还是降级
        stage_order = list(self.stage_score_ranges.keys())
        old_idx = stage_order.index(old_stage)
        new_idx = stage_order.index(new_stage)
        transition_type = "升级" if new_idx > old_idx else "降级"
        
        logger.warning(
            f"[Civilization] 文明{transition_type}：从 {stage_name_map[old_stage]} 进入 {stage_name_map[new_stage]}，"
            f"当前评分 {score:.0f}/1000"
        )
        
        # 发送文明阶段变化事件到事件总线，供其他系统订阅
        if hasattr(world, 'event_bus'):
            world.event_bus.publish(
                "civilization_stage_changed", 
                {
                    "old_stage": old_stage,
                    "new_stage": new_stage,
                    "transition_type": transition_type,
                    "score": score,
                    "metrics": self.civilization_metrics.copy()
                }
            )

    def _trigger_civilization_events(self, world: World, dt: float):
        """触发随机文明事件（灾害、繁荣、文化突破等）"""
        # 示例：低社会稳定度时触发叛乱事件
        if self.civilization_metrics['social_stability'] < 30 and self._rng.random() < 0.01:
            logger.warning("[Civilization] 社会稳定度过低，发生叛乱事件！")
            # 叛乱会损失人口、建筑、资源
            # TODO: 实现具体事件逻辑