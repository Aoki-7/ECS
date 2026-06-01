
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:__init__.py
@说明:人类组件包初始化文件
@时间:2026/03/13 13:58:36
@作者:Sherry
@版本:1.0
'''

"""
    Human包含的组件说明，按类别组织

    === 基础属性 (Basic Attributes) ===
    LifeCycleComponent: 年龄+生命阶段 - 跟踪实体的年龄，影响生育能力和行为
    GenderComponent: 性别组件 - 定义实体的性别，用于配对和繁衍逻辑
    IdentityComponent: 身份组件 - 实体的基本身份信息，如姓名
    MorphologyComponent: 身体组件 - 实体的身体特征，如身高、体重
    HumanComponent: 人类标识组件 - 标记实体是否为人类的标识

    === 生理需求 (Physiological Needs) ===
    PhysiologyNeedsComponent: 生理需求组件 - 跟踪饥饿、口渴、疲劳等基本需求
    HealthStatusComponent: 健康组件 - 实体的健康状态和生命值

    === 认知与行为 (Cognition and Behavior) ===
    BrainComponent: 思维组件 - 实体的思维能力和决策逻辑
    IntentComponent: 意图组件 - 实体的当前意图和目标
    TaskComponent: 任务组件 - 实体的当前任务状态
    GoalComponent: 目标组件 - 实体的长期目标
    MemoryComponent: 记忆组件 - 实体的记忆和经验存储
    PersonalityComponent: 个性组件 - 实体的性格特征
    KnowledgeComponent: 知识组件 - 实体的知识和技能学习

    === 社交与关系 (Social and Relationships) ===
    SocialComponent: 社交组件 - 实体的社交状态和关系网络
    RelationshipComponent: 关系组件 - 跟踪伴侣和婚姻状态
    ReproductionComponent: 繁衍组件 - 处理怀孕和生育逻辑

    === 能力与技能 (Abilities and Skills) ===
    SkillComponent: 技能组件 - 实体的技能水平和能力
    SearchComponent: 搜索组件 - 实体的搜索和发现能力
    VisionComponent: 视野组件 - 实体的视觉感知范围
    VelocityComponent: 速度组件 - 实体的移动速度

    === 经济与物品 (Economy and Items) ===
    EconomyComponent: 经济组件 - 实体的经济状态和资源
    InventoryComponent: 物品组件 - 实体的物品背包和装备

    === 行动与控制 (Actions and Control) ===
    ActionComponent: 行动组件 - 实体的当前行动和行为队列

    === 损伤 (Damage) ===
    HealthStatusComponent: 损伤组件 - 统一伤口记录与持续伤害
"""

"""
human/components/
├── __init__.py              # 更新：包含所有组件的导入和中文说明
├── basic/                   # 基础属性
│   ├── 生命周期组件（合并）     # 年龄+生命阶段
│   ├── gender_component.py  # 性别组件
│   ├── identity_component.py # 身份组件
│   ├── body_component.py    # 身体组件
│   └── human_component.py   # 人类标识组件
├── physiological/           # 生理需求
│   ├── physiology_needs_component.py # 生理需求组件
│   └── health_component.py  # 健康组件
├── cognitive/               # 认知与行为
│   ├── brain_component.py   # 思维组件
│   ├── intent_component.py  # 意图组件
│   ├── task_component.py    # 任务组件
│   ├── goal_component.py    # 目标组件
│   ├── memory_component.py  # 记忆组件
│   ├── personality_component.py # 个性组件
│   └── knowledge_component.py # 知识组件
├── social/                  # 社交与关系
│   ├── social_component.py  # 社交组件
│   ├── relationship_component.py # 关系组件
│   └── reproduction_component.py # 繁衍组件
├── abilities/               # 能力与技能
│   ├── skill_component.py   # 技能组件
│   ├── search_component.py  # 搜索组件
│   ├── vision_component.py  # 视野组件
│   └── velocity_component.py # 速度组件
├── economic/                # 经济与物品
│   ├── economy_component.py # 经济组件
│   └── inventory/           # 物品组件文件夹
├── action/                  # 行动与控制
│   └── action_component.py  # 行动组件

"""


# 基础属性
from biology.components.life_cycle_component import LifeCycleComponent
from .basic.gender_component import GenderComponent
from .basic.identity_component import IdentityComponent
from biology.components.morphology_component import MorphologyComponent
from .basic.human_component import HumanComponent

# 生理需求
from .physiological.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent

# 认知与行为
from .cognitive.brain_component import BrainComponent
from .cognitive.intent_component import IntentComponent
from .cognitive.task_component import TaskComponent
from .cognitive.goal_component import GoalComponent
from .cognitive.memory_component import MemoryComponent
from .cognitive.personality_component import PersonalityComponent
from .cognitive.knowledge_component import KnowledgeComponent

# 社交与关系
from .social.social_component import SocialComponent
from .social.relationship_component import RelationshipComponent
from .social.reproduction_component import ReproductionComponent

# 社会扩展组件
from .society.reputation_component import ReputationComponent, FameComponent, SocialStandingComponent
from .society.role_component import RoleComponent, IdentityShiftComponent, ResponsibilityComponent

from dataclasses import dataclass

@dataclass
class SocietyComponents:
    """
    社会扩展组件的便捷初始化
    """
    reputation: ReputationComponent
    role: RoleComponent

# 能力与技能
from .abilities.skill_component import SkillComponent
from .abilities.search_component import SearchComponent
from .abilities.vision_component import VisionComponent
from .abilities.velocity_component import VelocityComponent

# 经济与物品
from .economic.economy_component import EconomyComponent
from .economic.inventory.inventory_component import InventoryComponent

# 行动与控制
from .action.action_component import ActionComponent

# 损伤
from biology.components.health_status_component import HealthStatusComponent