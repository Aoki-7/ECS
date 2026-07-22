#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:human_entity.py
@说明:基础的human实体模板
@时间:2026/03/15 20:21:46
@作者:Sherry
@版本:1.0
'''

from typing import List, Type
from core.component import Component
from core.world import World
from core.entity import Entity

# 导入所有组件
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from biology.components.gender_component import GenderComponent
from human.components.basic.identity_component import IdentityComponent

from human.components.basic.human_component import HumanComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent

from human.components.health.disease_component_v4 import DiseaseManagerComponent as DiseaseComponent
from human.components.combat.combat_stats_component import CombatStatsComponent
from human.components.social.dialogue_component import DialogueComponent
from human.components.social.conflict_component import ConflictComponent
from human.components.abilities.velocity_component import VelocityComponent
from human.components.perception.vision_component import VisionComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.abilities.search_component import SearchComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.brain_component import BrainComponent
from human.components.cognitive.intent_component import IntentComponent
from human.components.cognitive.task_component import TaskComponent
from human.components.cognitive.goal_component import GoalComponent
from human.components.cognitive.memory_component_v4 import MemoryManagerComponent as MemoryComponent
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.emotion_component_v4 import EmotionComponent
from human.components.social.social_component_v4 import SocialManagerComponent as SocialComponent
from human.components.skill.human_tech_skill_component import HumanTechSkillComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.social.reproduction_component import ReproductionComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from human.components.action.action_component import ActionComponent
from space.space_component import SpaceComponent


class HumanEntity:
    """
    Human实体模板
    定义一个完整的Human实体应该包含的所有组件
    """

    # 基础组件 (Basic Components)
    BASIC_COMPONENTS: List[Type[Component]] = [
        SpaceComponent,           # 空间位置
        HumanComponent,           # 人类标识
        IdentityComponent,        # 身份信息
        MorphologyComponent,      # 身体特征
        LifeCycleComponent,             # 年龄
        GenderComponent,          # 性别
    ]

    # 生理组件 (Physiological Components)
    PHYSIOLOGICAL_COMPONENTS: List[Type[Component]] = [
        HealthStatusComponent,          # 健康状态
        PhysiologyNeedsComponent, # 生理需求
        DiseaseComponent,         # 疾病状态
    ]

    # 能力组件 (Ability Components)
    ABILITY_COMPONENTS: List[Type[Component]] = [
        VelocityComponent,        # 移动速度
        VisionComponent,          # 视觉感知
        SkillComponent,           # 技能水平
        SearchComponent,          # 搜索能力
        CombatStatsComponent,     # 战斗属性
    ]

    # 经济组件 (Economic Components)
    ECONOMIC_COMPONENTS: List[Type[Component]] = [
        EconomyComponent,         # 经济状态
        InventoryComponent,       # 物品背包
    ]

    # 认知组件 (Cognitive Components)
    COGNITIVE_COMPONENTS: List[Type[Component]] = [
        BrainComponent,           # 思维能力
        IntentComponent,          # 当前意图
        TaskComponent,            # 当前任务
        GoalComponent,            # 长期目标
        MemoryComponent,          # 记忆存储
        KnowledgeComponent,       # 知识库
        PersonalityComponent,     # 性格特征
        EmotionComponent,         # 情绪状态
        HumanTechSkillComponent,  # 技术技能掌握
    ]

    # 社交组件 (Social Components)
    SOCIAL_COMPONENTS: List[Type[Component]] = [
        SocialComponent,          # 社交状态
        RelationshipComponent,    # 关系状态
        ReproductionComponent,    # 繁衍状态
        TribeMembershipComponent, # 部落成员身份
        DialogueComponent,        # 对话状态
        ConflictComponent,        # 冲突状态
    ]

    # 行动组件 (Action Components)
    ACTION_COMPONENTS: List[Type[Component]] = [
        ActionComponent,          # 行动队列
    ]

    # 所有组件的完整列表
    ALL_COMPONENTS: List[Type[Component]] = (
        BASIC_COMPONENTS +
        PHYSIOLOGICAL_COMPONENTS +
        ABILITY_COMPONENTS +
        ECONOMIC_COMPONENTS +
        COGNITIVE_COMPONENTS +
        SOCIAL_COMPONENTS +
        ACTION_COMPONENTS
    )

    @classmethod
    def get_component_categories(cls) -> dict[str, List[Type[Component]]]:
        """
        获取组件分类字典
        """
        return {
            "basic": cls.BASIC_COMPONENTS,
            "physiological": cls.PHYSIOLOGICAL_COMPONENTS,
            "ability": cls.ABILITY_COMPONENTS,
            "economic": cls.ECONOMIC_COMPONENTS,
            "cognitive": cls.COGNITIVE_COMPONENTS,
            "social": cls.SOCIAL_COMPONENTS,
            "action": cls.ACTION_COMPONENTS,
        }

    @classmethod
    def create_components(cls, world: World, entity: Entity, **kwargs):
        """
        为实体创建并添加所有组件

        Args:
            world: World实例
            entity: 要添加组件的实体
            **kwargs: 组件初始化参数，例如 name, x, y 等
        """
        # 提取常用参数
        name = kwargs.get('name', 'Unknown')
        x = kwargs.get('x', 0)
        y = kwargs.get('y', 0)

        # 基础组件
        world.add_component(entity, HumanComponent())
        world.add_component(entity, SpaceComponent(x=x, y=y))
        world.add_component(entity, IdentityComponent(name=name))
        world.add_component(entity, MorphologyComponent(
            height=kwargs.get('height', 170),
            weight=kwargs.get('weight', 70),
            strength=kwargs.get('strength', 1.0),
            agility=kwargs.get('agility', 1.0),
            endurance=kwargs.get('endurance', 1.0),
        ))
        world.add_component(entity, GenderComponent(kwargs.get('gender', None)))
        world.add_component(entity, LifeCycleComponent(
            current_age=kwargs.get('age', 18),
            max_age=kwargs.get('max_age', 25.0)  # 默认 25 年，确保能在可观测模拟周期内看到生老病死
        ))

        # 生理组件
        world.add_component(entity, HealthStatusComponent())
        world.add_component(entity, PhysiologyNeedsComponent())
        world.add_component(entity, DiseaseComponent())

        # 能力组件
        world.add_component(entity, VelocityComponent(speed=kwargs.get('speed', 2.5)))
        world.add_component(entity, VisionComponent(radius=kwargs.get('vision_radius', 15)))
        world.add_component(entity, SkillComponent())
        world.add_component(entity, SearchComponent())
        world.add_component(entity, CombatStatsComponent(
            attack_power=kwargs.get('attack_power', 10.0),
            defense_power=kwargs.get('defense_power', 5.0),
            aggression=kwargs.get('aggression', 0.5),
        ))

        # 经济组件
        world.add_component(entity, EconomyComponent())
        world.add_component(entity, InventoryComponent())

        # 认知组件
        world.add_component(entity, BrainComponent())
        world.add_component(entity, IntentComponent())
        world.add_component(entity, TaskComponent())
        world.add_component(entity, GoalComponent())
        world.add_component(entity, MemoryComponent())
        world.add_component(entity, KnowledgeComponent())
        world.add_component(entity, PersonalityComponent())
        world.add_component(entity, EmotionComponent())

        # 生态组件：人类作为杂食动物参与食物链
        from biology.ecology.components.food_chain_component import FoodChainComponent
        world.add_component(entity, FoodChainComponent(
            trophic_level=2,
            niche="omnivore",
            energy_transfer_efficiency=0.1,
        ))

        # 分类组件：标记为人类
        from identity.category_component import CategoryComponent
        from identity.category import EntityCategory
        from identity.subcategory import HumanSubCategory
        world.add_component(entity, CategoryComponent(
            category=EntityCategory.HUMAN,
            subcategory=HumanSubCategory.CIVILIAN,
        ))

        # 社交组件
        world.add_component(entity, SocialComponent())
        world.add_component(entity, RelationshipComponent())
        world.add_component(entity, ReproductionComponent())
        world.add_component(entity, TribeMembershipComponent())
        world.add_component(entity, DialogueComponent())
        world.add_component(entity, ConflictComponent())

        # 行动组件
        world.add_component(entity, ActionComponent())

    @classmethod
    def create_batch(cls, world, count: int, **kwargs):
        """
        批量创建Human实体

        Args:
            world: World实例
            count: 要创建的实体数量
            **kwargs: 组件初始化参数

        Returns:
            List[Entity]: 创建的实体列表
        """
        entities = []
        for i in range(count):
            entity = world.create_entity()
            # 为每个实体生成唯一名称（如果未提供）
            name = kwargs.get('name', 'Human_{i}')
            # 如果提供了名称模板，添加索引
            if '{i}' in name:
                name = name.format(i=i)

            cls.create_components(world, entity, name=name, **kwargs)
            entities.append(entity)

        return entities

