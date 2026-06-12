"""
组件包 — 纯数据组件定义

依赖：
    - core/
    - biology/
    - space/
    - environment/
    - animal/
    - plant/
    - resource/
    - civilization/
    - memory_layer/

版本：v4.0

"""
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
    GenderComponent: 性别组件 - 定义实体的性别，用于配对和繁衍逻辑
    IdentityComponent: 身份组件 - 实体的基本身份信息，如姓名
    HumanComponent: 人类标识组件 - 标记实体是否为人类的标识

    === 生理需求 (Physiological Needs) ===
    PhysiologyNeedsComponent: 生理需求组件 - 跟踪饥饿、口渴、疲劳等基本需求

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
    SearchComponent: 搜索组件 v2.0 - 智能目标发现与策略管理
        · 递进式策略：visual → memory → explore → random
        · 搜索历史：避免在同一区域重复搜索
        · 概率评估：根据历史成功率动态调整信心
        · 发现即记忆：找到目标后立即写入 discoveries，供记忆系统读取
    VisionComponent: 视野组件 v2.0 - 锥形 FOV + 注意力机制
        · 锥形视野：fov_angle（默认 120°）+ fov_direction，非 360° 雷达
        · 昼夜差异：acuity_day / acuity_night，模拟人类暗视觉下降
        · 注意力机制：attention_capacity（默认 3），只关注最重要的 N 个目标
        · 感知统计：entities_seen_this_tick / last_perception_tick
    VelocityComponent: 速度组件 - 实体的移动速度

    === 经济与物品 (Economy and Items) ===
    EconomyComponent: 经济组件 - 实体的经济状态和资源
    InventoryComponent: 物品组件 - 实体的物品背包和装备

    === 行动与控制 (Actions and Control) ===
    ActionComponent: 行动组件 - 实体的当前行动和行为队列

    注意：
        - LifeCycleComponent、MorphologyComponent、HealthStatusComponent 属于 biology 包
        - 请直接从 biology.components 导入，而非从 human.components
"""

# 基础属性
from .basic.gender_component import GenderComponent
from .basic.identity_component import IdentityComponent
from .basic.human_component import HumanComponent

# 生理需求
from .physiological.physiology_needs_component import PhysiologyNeedsComponent

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

@dataclass(slots=True)
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

