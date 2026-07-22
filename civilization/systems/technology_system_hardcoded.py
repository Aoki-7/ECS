#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:technology_system.py
@说明:技术进步系统 - 文明技术发展和知识传承的系统
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

import logging

from core.system import System
from core.world import World
from typing import Dict, List, Any, Set, Optional
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

from human.components.abilities.skill_component import SkillComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.social.social_component import SocialComponent
from human.components.economic.economy_component import EconomyComponent
from civilization.components.technology_modifier_component import TechnologyModifierComponent


class TechnologyType(Enum):
    """技术类型枚举"""
    AGRICULTURE = "agriculture"      # 农业
    METALWORKING = "metalworking"    # 金属加工
    CONSTRUCTION = "construction"    # 建筑
    MEDICINE = "medicine"           # 医药
    WEAPONRY = "weaponry"          # 武器
    TRANSPORTATION = "transportation" # 交通


@dataclass
class Technology:
    """技术类"""
    name: str
    type: TechnologyType
    level: int = 1
    prerequisites: Set[str] = field(default_factory=set)
    research_cost: Dict[str, float] = field(default_factory=dict)
    unlocked_features: List[str] = field(default_factory=list)


class TechnologySystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    技术进步系统

    功能：
    - 管理技术树和研究进度
    - 人类可以通过经验积累来解锁新技术
    - 技术可以传承给后代
    - 技术进步影响社会发展
    """

    # 技术树定义
    TECHNOLOGIES = {
        # 农业线
        "basic_farming": Technology(
            name="基础农业",
            type=TechnologyType.AGRICULTURE,
            prerequisites=set(),
            research_cost={"experience": 100.0},
            unlocked_features=["plant_cultivation", "crop_rotation"]
        ),
        "advanced_farming": Technology(
            name="高级农业",
            type=TechnologyType.AGRICULTURE,
            prerequisites={"basic_farming"},
            research_cost={"experience": 200.0},
            unlocked_features=["irrigation", "selective_breeding"]
        ),
        "fertilizer_tech": Technology(
            name="肥料技术",
            type=TechnologyType.AGRICULTURE,
            prerequisites={"advanced_farming"},
            research_cost={"experience": 300.0},
            unlocked_features=["organic_fertilizer", "yield_boost_30"]
        ),
        "mechanized_farming": Technology(
            name="机械化农业",
            type=TechnologyType.AGRICULTURE,
            prerequisites={"fertilizer_tech", "steam_power"},
            research_cost={"metal": 200.0, "experience": 500.0},
            unlocked_features=["farm_machinery", "yield_boost_100"]
        ),
        # 金属加工线
        "metal_tools": Technology(
            name="金属工具",
            type=TechnologyType.METALWORKING,
            prerequisites=set(),
            research_cost={"metal": 50.0, "experience": 150.0},
            unlocked_features=["metal_axes", "metal_picks", "improved_tools"]
        ),
        "bronze_smelting": Technology(
            name="青铜冶炼",
            type=TechnologyType.METALWORKING,
            prerequisites={"metal_tools"},
            research_cost={"metal": 100.0, "experience": 200.0},
            unlocked_features=["bronze_alloy", "bronze_tools_boost"]
        ),
        "iron_smelting": Technology(
            name="冶铁技术",
            type=TechnologyType.METALWORKING,
            prerequisites={"bronze_smelting"},
            research_cost={"metal": 150.0, "experience": 300.0},
            unlocked_features=["iron_alloy", "iron_tools_boost"]
        ),
        "steelmaking": Technology(
            name="炼钢技术",
            type=TechnologyType.METALWORKING,
            prerequisites={"iron_smelting"},
            research_cost={"metal": 300.0, "experience": 400.0},
            unlocked_features=["steel_alloy", "steel_tools_boost"]
        ),
        # 建筑线
        "basic_construction": Technology(
            name="基础建筑",
            type=TechnologyType.CONSTRUCTION,
            prerequisites={"metal_tools"},
            research_cost={"stone": 100.0, "wood": 100.0, "experience": 200.0},
            unlocked_features=["stone_houses", "workshops", "storage_facilities"]
        ),
        "masonry": Technology(
            name="砖石建筑",
            type=TechnologyType.CONSTRUCTION,
            prerequisites={"basic_construction"},
            research_cost={"stone": 200.0, "experience": 250.0},
            unlocked_features=["masonry_construction", "durability_boost"]
        ),
        "concrete": Technology(
            name="混凝土技术",
            type=TechnologyType.CONSTRUCTION,
            prerequisites={"masonry", "steelmaking"},
            research_cost={"stone": 300.0, "metal": 100.0, "experience": 400.0},
            unlocked_features=["concrete_building", "skyscraper_possible"]
        ),
        # 医药线
        "herbal_medicine": Technology(
            name="草药医学",
            type=TechnologyType.MEDICINE,
            prerequisites=set(),
            research_cost={"experience": 120.0},
            unlocked_features=["basic_healing", "disease_prevention"]
        ),
        "anatomy": Technology(
            name="解剖学",
            type=TechnologyType.MEDICINE,
            prerequisites={"herbal_medicine"},
            research_cost={"experience": 250.0},
            unlocked_features=["surgery", "healing_boost_20"]
        ),
        "antibiotics": Technology(
            name="抗生素",
            type=TechnologyType.MEDICINE,
            prerequisites={"anatomy"},
            research_cost={"experience": 400.0},
            unlocked_features=["infection_treatment", "lifespan_boost_20"]
        ),
        # 武器线
        "basic_weaponry": Technology(
            name="基础武器",
            type=TechnologyType.WEAPONRY,
            prerequisites={"metal_tools"},
            research_cost={"metal": 30.0, "wood": 50.0, "experience": 180.0},
            unlocked_features=["metal_weapons", "defensive_structures"]
        ),
        "bronze_weapons": Technology(
            name="青铜武器",
            type=TechnologyType.WEAPONRY,
            prerequisites={"basic_weaponry", "bronze_smelting"},
            research_cost={"metal": 100.0, "experience": 250.0},
            unlocked_features=["bronze_weapon_damage_boost_30"]
        ),
        "gunpowder": Technology(
            name="火药",
            type=TechnologyType.WEAPONRY,
            prerequisites={"iron_smelting", "basic_construction"},
            research_cost={"metal": 200.0, "experience": 400.0},
            unlocked_features=["explosives", "early_guns"]
        ),
        # 交通/能源线
        "wheel": Technology(
            name="轮子",
            type=TechnologyType.TRANSPORTATION,
            prerequisites={"basic_construction"},
            research_cost={"wood": 50.0, "experience": 150.0},
            unlocked_features=["cart", "transport_efficiency_20"]
        ),
        "steam_power": Technology(
            name="蒸汽动力",
            type=TechnologyType.TRANSPORTATION,
            prerequisites={"iron_smelting", "basic_construction"},
            research_cost={"metal": 300.0, "experience": 500.0},
            unlocked_features=["steam_engine", "power_boost_50"]
        )
    }

    def __init__(self):
        self.discovered_technologies: Set[str] = set()
        self.global_tech_progress: Dict[str, float] = {}

    def update(self, world: World, dt: float) -> None:
        """更新技术进步"""
        # 检查是否有新技术的解锁条件满足
        self._check_technology_unlocks(world)

        # 推进研究进度
        self._advance_research(world, dt)

        # 传承技术知识
        self._inherit_technologies(world)

        # 应用技术效果
        self._apply_technology_effects(world)

    def _check_technology_unlocks(self, world: World):
        """检查技术解锁条件"""
        for tech_name, technology in self.TECHNOLOGIES.items():
            if tech_name in self.discovered_technologies:
                continue

            # 检查前提条件
            if not technology.prerequisites.issubset(self.discovered_technologies):
                continue

            # 检查解锁条件
            if self._check_unlock_conditions(tech_name, technology, world):
                self._unlock_technology(tech_name, technology, world)

    def _check_unlock_conditions(self, tech_name: str, technology: Technology, world: World) -> bool:
        """检查解锁条件"""
        # 检查是否有足够的人类拥有相关经验
        required_experience = technology.research_cost.get("experience", 0.0)

        if required_experience > 0:
            total_experience = 0.0
            for entity, (skill, knowledge) in world.get_components(SkillComponent, KnowledgeComponent):
                # 计算相关技能经验
                relevant_skills = self._get_relevant_skills(technology.type)
                for skill_name in relevant_skills:
                    if skill_name in skill.skills:
                        total_experience += skill.skills[skill_name] * 10.0  # 技能等级转换为经验

                # 检查知识库
                if knowledge and tech_name in knowledge.known_technologies:
                    total_experience += 50.0  # 已有知识加成

            # 研究进度也转化为经验，加速技术自然涌现
            total_experience += self.global_tech_progress.get(tech_name, 0.0) * 5.0

            if total_experience < required_experience:
                return False

        # 检查资源条件
        for resource, amount in technology.research_cost.items():
            if resource == "experience":
                continue
            # 这里需要检查全球资源总量，暂时简化
            if not self._check_global_resource_availability(resource, amount, world):
                return False

        return True

    def _unlock_technology(self, tech_name: str, technology: Technology, world: World):
        """解锁技术"""
        self.discovered_technologies.add(tech_name)
        self.global_tech_progress[tech_name] = 1.0

        # 通知所有人类（限制上限避免内存泄漏）
        count = 0
        for entity, (knowledge,) in world.get_components(KnowledgeComponent):
            if knowledge:
                knowledge.known_technologies.add(tech_name)
                count += 1
                if count >= 10000:  # 限制上限
                    break

        logger.info(f"[TechnologySystem] Technology unlocked: {technology.name}")

        # 触发技术解锁事件
        self._trigger_technology_events(tech_name, technology, world)

    def _advance_research(self, world: World, dt: float):
        """推进研究进度"""
        for entity, (skill, knowledge, memory) in world.get_components(
            SkillComponent, KnowledgeComponent, MemoryComponent
        ):
            # 基于经验积累推进研究
            research_points = dt * 0.2  # 基础研究点数（适度加快）

            # 技能加成
            research_skill = skill.skills.get('research', 1.0)
            research_points *= (0.5 + research_skill * 0.5)

            # 分配研究点数到潜在技术
            potential_techs = self._get_potential_technologies(knowledge)
            if potential_techs:
                points_per_tech = research_points / len(potential_techs)
                for tech_name in potential_techs:
                    if tech_name not in self.global_tech_progress:
                        self.global_tech_progress[tech_name] = 0.0
                    self.global_tech_progress[tech_name] += points_per_tech

    def _inherit_technologies(self, world: World):
        """传承技术知识"""
        # 父母向子女传承技术
        for entity, (social, knowledge) in world.get_components(SocialComponent, KnowledgeComponent):
            if not social or not knowledge:
                continue

            # 查找子女（限制上限避免内存泄漏）
            children = []
            for child_id, relation_type in list(social.relations.items()):
                if relation_type == "parent":
                    children.append(child_id)
                    if len(children) >= 100:  # 限制上限
                        break

            # 向子女传承知识
            for child_id in children:
                child_knowledge = world.get_component(child_id, KnowledgeComponent)
                if child_knowledge:
                    # 传承部分技术知识
                    inherited_techs = knowledge.known_technologies.copy()
                    # 简化：子女继承80%的技术
                    import random
                    inherited_techs = set(random.sample(list(inherited_techs),
                                                      int(len(inherited_techs) * 0.8)))
                    child_knowledge.known_technologies.update(inherited_techs)

    def _apply_technology_effects(self, world: World):
        """应用技术效果：将已解锁技术转换为全局数值加成"""
        modifier = self._get_or_create_modifier_component(world)
        if modifier is None:
            return

        # 每轮重新计算，避免重复叠加
        modifier.harvest_multiplier = 1.0
        modifier.gather_multiplier = 1.0
        modifier.healthcare_multiplier = 1.0
        modifier.construction_efficiency = 1.0

        for tech_name in self.discovered_technologies:
            technology = self.TECHNOLOGIES[tech_name]
            for feature in technology.unlocked_features:
                self._apply_feature_effect(feature, modifier)

    def _get_or_create_modifier_component(self, world: World) -> Optional[TechnologyModifierComponent]:
        """获取或创建世界实体的技术修正组件"""
        modifier = world.get_world_component(TechnologyModifierComponent)
        if modifier is None:
            world_entity = world.get_world_entity()
            if world_entity is None:
                return None
            modifier = TechnologyModifierComponent()
            world.add_component(world_entity, modifier)
        return modifier

    def _apply_feature_effect(self, feature: str, modifier: TechnologyModifierComponent):
        """应用具体功能效果到全局修正组件"""
        if feature == "plant_cultivation":
            modifier.harvest_multiplier += 0.2
        elif feature == "crop_rotation":
            modifier.harvest_multiplier += 0.1
        elif feature == "irrigation":
            modifier.harvest_multiplier += 0.3
        elif feature == "selective_breeding":
            modifier.harvest_multiplier += 0.2
        elif feature == "metal_axes":
            modifier.gather_multiplier += 0.3
        elif feature == "metal_picks":
            modifier.gather_multiplier += 0.3
        elif feature == "improved_tools":
            modifier.gather_multiplier += 0.2
        elif feature == "basic_healing":
            modifier.healthcare_multiplier += 0.2
        elif feature == "disease_prevention":
            modifier.healthcare_multiplier += 0.2
        elif feature == "stone_houses":
            modifier.construction_efficiency += 0.2
        elif feature == "workshops":
            modifier.construction_efficiency += 0.2
        elif feature == "storage_facilities":
            modifier.construction_efficiency += 0.1

    def _boost_agriculture_yield(self, world: World, multiplier: float):
        """（旧接口保留）通过全局修正组件提高农业产量"""
        modifier = self._get_or_create_modifier_component(world)
        if modifier is not None:
            modifier.harvest_multiplier *= multiplier

    def _boost_gathering_efficiency(self, world: World, resource_type: str, multiplier: float):
        """（旧接口保留）通过全局修正组件提高采集效率"""
        modifier = self._get_or_create_modifier_component(world)
        if modifier is not None:
            modifier.gather_multiplier *= multiplier

    def _improve_healthcare(self, world: World, multiplier: float):
        """（旧接口保留）通过全局修正组件提高医疗效果"""
        modifier = self._get_or_create_modifier_component(world)
        if modifier is not None:
            modifier.healthcare_multiplier *= multiplier

    def _get_relevant_skills(self, tech_type: TechnologyType) -> List[str]:
        """获取相关技能"""
        skill_map = {
            TechnologyType.AGRICULTURE: ['farming', 'gathering'],
            TechnologyType.METALWORKING: ['crafting', 'mining'],
            TechnologyType.CONSTRUCTION: ['construction', 'crafting'],
            TechnologyType.MEDICINE: ['medicine', 'gathering'],
            TechnologyType.WEAPONRY: ['crafting', 'combat'],
            TechnologyType.TRANSPORTATION: ['crafting', 'construction']
        }
        return skill_map.get(tech_type, [])

    def _get_potential_technologies(self, knowledge: KnowledgeComponent) -> List[str]:
        """获取潜在研究技术"""
        potential = []
        for tech_name, technology in self.TECHNOLOGIES.items():
            if (tech_name not in self.discovered_technologies and
                technology.prerequisites.issubset(knowledge.known_technologies)):
                potential.append(tech_name)
        return potential

    def _check_global_resource_availability(self, resource: str, amount: float, world: World) -> bool:
        """检查全球资源可用性"""
        # 简化实现：总是返回True，实际应该检查所有人类的总资源
        return True

    def _trigger_technology_events(self, tech_name: str, technology: Technology, world: World):
        """触发技术解锁事件"""
        # 这里可以触发社会事件、成就等
        pass