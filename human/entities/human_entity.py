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
from biology.components.age_component import AgeComponent
from biology.components.gender_component import GenderComponent
from human.components.basic.identity_component import IdentityComponent
from biology.components.body_component import BodyComponent
from human.components.basic.human_component import HumanComponent
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_component import HealthComponent
from biology.components.temperature_component import TemperatureComponent
from biology.components.disease_component import DiseaseComponent
from human.components.combat.combat_stats_component import CombatStatsComponent
from human.components.social.dialogue_component import DialogueComponent
from human.components.social.conflict_component import ConflictComponent
from core.components.velocity_component import VelocityComponent
from core.components.vision_component import VisionComponent
from human.components.abilities.skill_component import SkillComponent
from human.components.abilities.search_component import SearchComponent
from human.components.economic.economy_component import EconomyComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.brain_component import BrainComponent
from human.components.cognitive.intent_component import IntentComponent
from human.components.cognitive.task_component import TaskComponent
from human.components.cognitive.goal_component import GoalComponent
from human.components.cognitive.memory_component import MemoryComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.social.social_component import SocialComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.social.reproduction_component import ReproductionComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from core.components.action_component import ActionComponent
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
        BodyComponent,            # 身体特征
        AgeComponent,             # 年龄
        GenderComponent,          # 性别
    ]

    # 生理组件 (Physiological Components)
    PHYSIOLOGICAL_COMPONENTS: List[Type[Component]] = [
        HealthComponent,          # 健康状态
        PhysiologyNeedsComponent, # 生理需求
        TemperatureComponent,     # 体感温度
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
        PersonalityComponent,     # 性格特征
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
        world.add_component(entity, BodyComponent(kwargs.get('height', 170), kwargs.get('weight', 70)))
        world.add_component(entity, GenderComponent(kwargs.get('gender', None)))
        world.add_component(entity, AgeComponent(kwargs.get('age', 18)))

        # 生理组件
        world.add_component(entity, HealthComponent())
        world.add_component(entity, PhysiologyNeedsComponent())
        world.add_component(entity, TemperatureComponent())
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
        world.add_component(entity, PersonalityComponent())
        world.add_component(entity, EmotionComponent())

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


