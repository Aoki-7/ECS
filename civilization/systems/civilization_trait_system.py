#!/usr/bin/env python3
"""
文明特质生效系统 v4.16.0
处理文明特质对所有相关系统的效果应用
"""

import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from civilization.components.civilization_component import CivilizationComponent
from civilization.components.civilization_trait_component import CivilizationTraitComponent, CivilizationTraitType
from human.components.economic.economy_component import EconomyComponent
from human.components.health.health_component import HealthComponent
from human.components.social.reproduction_component import ReproductionComponent
from resource.food.components.food_production_component import FoodProductionComponent
from technology.components.tech_research_component import TechResearchComponent

logger = logging.getLogger(__name__)


class CivilizationTraitSystem(System):
    """
    文明特质生效系统
    每帧计算所有文明的特质效果，应用到对应属性上
    """

    tick_interval = 5  # 每5tick执行一次
    priority = 150  # 在各业务系统之前运行，提前应用修正

    def update(self, world: World, dt: float):
        # 遍历所有文明实体
        for entity, civ, trait_comp in world.query(
            CivilizationComponent,
            CivilizationTraitComponent
        ):
            # 应用特质效果到文明整体属性
            self._apply_civilization_effects(civ, trait_comp)
            
            # 应用特质效果到文明所属所有人类
            for human_id in civ.member_ids:
                if human_id not in world.entities:
                    continue
                self._apply_human_effects(world, human_id, trait_comp)
            
            # 应用特质效果到文明所属所有生产建筑
            for building_id in civ.building_ids:
                if building_id not in world.entities:
                    continue
                self._apply_building_effects(world, building_id, trait_comp)
    
    def _apply_civilization_effects(self, civ: CivilizationComponent, traits: CivilizationTraitComponent) -> None:
        """应用特质效果到文明整体属性"""
        # 科技研发速度
        if hasattr(civ, 'tech_research_speed'):
            civ.tech_research_speed = traits.get_attribute_modifier(
                "tech_research_speed",
                civ.tech_research_speed
            )
        
        # 生育率修正
        if hasattr(civ, 'base_pregnancy_rate'):
            civ.base_pregnancy_rate = traits.get_attribute_modifier(
                "pregnancy_chance",
                civ.base_pregnancy_rate
            )
        
        # 资源存储上限
        if hasattr(civ, 'resource_storage_capacity'):
            civ.resource_storage_capacity = traits.get_attribute_modifier(
                "resource_storage_capacity",
                civ.resource_storage_capacity
            )
        
        # 战斗能力修正
        if hasattr(civ, 'base_combat_strength'):
            civ.base_combat_strength = traits.get_attribute_modifier(
                "combat_ability",
                civ.base_combat_strength
            )
        
        # 外交关系修正
        if hasattr(civ, 'diplomacy_bonus'):
            civ.diplomacy_bonus = traits.get_attribute_modifier(
                "diplomacy_relation_bonus",
                civ.diplomacy_bonus
            )
        
        # 农业产量修正
        if hasattr(civ, 'agriculture_yield_bonus'):
            civ.agriculture_yield_bonus = traits.get_attribute_modifier(
                "crop_yield",
                civ.agriculture_yield_bonus
            )
        
        # 采矿产量修正
        if hasattr(civ, 'mining_yield_bonus'):
            civ.mining_yield_bonus = traits.get_attribute_modifier(
                "ore_yield",
                civ.mining_yield_bonus
            )
    
    def _apply_human_effects(self, world: World, human_id: int, traits: CivilizationTraitComponent) -> None:
        """应用特质效果到人类个体"""
        # 健康组件：疾病抗性
        health = world.get_component(human_id, HealthComponent)
        if health and hasattr(health, 'disease_resistance'):
            health.disease_resistance = traits.get_attribute_modifier(
                "disease_resistance",
                health.disease_resistance
            )
        
        # 生育组件：怀孕概率、生育间隔
        repro = world.get_component(human_id, ReproductionComponent)
        if repro:
            if hasattr(repro, 'pregnancy_chance'):
                repro.pregnancy_chance = traits.get_attribute_modifier(
                    "pregnancy_chance",
                    repro.pregnancy_chance
                )
            if hasattr(repro, 'birth_cooldown'):
                repro.birth_cooldown = traits.get_attribute_modifier(
                    "birth_interval",
                    repro.birth_cooldown
                )
        
        # 经济组件：财富获取
        economy = world.get_component(human_id, EconomyComponent)
        if economy and hasattr(economy, 'wealth_gain_multiplier'):
            economy.wealth_gain_multiplier = traits.get_attribute_modifier(
                "loot_amount",
                economy.wealth_gain_multiplier
            )
        
        # 食物消耗修正
        if hasattr(health, 'food_consumption_rate'):
            health.food_consumption_rate = traits.get_attribute_modifier(
                "food_consumption_rate",
                health.food_consumption_rate
            )
        
        # 水消耗修正
        if hasattr(health, 'water_consumption_rate'):
            health.water_consumption_rate = traits.get_attribute_modifier(
                "water_consumption_rate",
                health.water_consumption_rate
            )
    
    def _apply_building_effects(self, world: World, building_id: int, traits: CivilizationTraitComponent) -> None:
        """应用特质效果到建筑"""
        # 食物生产建筑：产量修正
        food_prod = world.get_component(building_id, FoodProductionComponent)
        if food_prod and hasattr(food_prod, 'production_rate'):
            food_prod.production_rate = traits.get_attribute_modifier(
                "crop_yield",
                food_prod.production_rate
            )
        
        # 科技建筑：研发速度修正
        tech_research = world.get_component(building_id, TechResearchComponent)
        if tech_research and hasattr(tech_research, 'research_speed'):
            tech_research.research_speed = traits.get_attribute_modifier(
                "tech_research_speed",
                tech_research.research_speed
            )
        
        # 通用建筑：耐久修正
        from building.components.building_component import BuildingComponent
        building = world.get_component(building_id, BuildingComponent)
        if building and hasattr(building, 'durability'):
            building.durability = traits.get_attribute_modifier(
                "building_durability",
                building.durability
            )
    
    def get_trait_description(self, trait_type: CivilizationTraitType) -> str:
        """获取特质的描述文本"""
        trait_descriptions = {
            CivilizationTraitType.AGRICULTURAL_EXPERT: "农业专家：作物产量+30%，生长速度+20%",
            CivilizationTraitType.HUNTING_MASTER: "狩猎大师：狩猎成功率+40%，动物掉落+25%",
            CivilizationTraitType.MINING_PROFICIENT: "采矿能手：矿石产出+35%，开采速度+30%",
            CivilizationTraitType.CRAFTSMAN_SPIRIT: "工匠精神：工具耐久+50%，制成品品质+25%",
            CivilizationTraitType.HIGH_FERTILITY: "高生育率：怀孕概率+40%，生育间隔-30%",
            CivilizationTraitType.SOCIAL_COHESION: "社会凝聚力：内部冲突概率-60%，关系提升速度+50%",
            CivilizationTraitType.KNOWLEDGE_SHARING: "知识共享：科技研发速度+40%，技能传承效率+50%",
            CivilizationTraitType.PEACE_LOVING: "爱好和平：对外战争概率-70%，外交关系+30%",
            CivilizationTraitType.HARDY_CONSTITUTION: "强健体质：疾病抵抗+50%，恶劣环境耐受+40%",
            CivilizationTraitType.ADAPTABLE: "适应性强：任何地形移动成本-30%，资源获取阈值-25%",
            CivilizationTraitType.NIGHT_VISION: "夜视能力：夜间活动效率+70%，夜间视野+50%",
            CivilizationTraitType.RATIONING_EXPERT: "配给专家：食物/水消耗速率-30%，资源存储上限+40%",
            CivilizationTraitType.WARRIOR_CULTURE: "战士文化：战斗能力+50%，武器伤害+30%",
            CivilizationTraitType.RAIDING_TRADITION: "劫掠传统：战利品获取+60%，敌方资源掠夺+40%",
            CivilizationTraitType.DEFENSIVE_EXPERT: "防御专家：建筑耐久+100%，防御战伤害减免+50%",
            CivilizationTraitType.NAVAL_MASTERY: "航海精通：水上移动速度+100%，水上战斗+70%",
            CivilizationTraitType.ANIMAL_FRIEND: "动物之友：野生动物不会主动攻击，驯养成功率+80%",
            CivilizationTraitType.LUCKY: "幸运：所有概率事件正面结果权重+30%",
            CivilizationTraitType.SCHOLARLY: "尚学：科技点获取+60%，识字率+100%",
            CivilizationTraitType.TRADITIONAL: "传统：文化传承速度+80%，社会稳定性+50%，科技研发速度-20%",
        }
        return trait_descriptions.get(trait_type, "未知特质")