#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:goal_generator.py
@说明:目标生成器

职责：
    - 根据人生阶段生成适当的目标
    - 考虑性格、性别、关系、经济状况
'''

from typing import List, Optional

from human.components.cognitive.personality_component import PersonalityComponent
from biology.components.gender_component import GenderComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.economic.economy_component import EconomyComponent


class GoalGenerator:
    """目标生成器"""

    def generate_goal_for_stage(
        self, life_stage: str, personality: Optional[PersonalityComponent],
        gender: Optional[GenderComponent], relation: Optional[RelationshipComponent],
        economy: Optional[EconomyComponent]
    ) -> str:
        """
        根据人生阶段生成适当的目标

        Args:
            life_stage: 人生阶段
            personality: 性格组件
            gender: 性别组件
            relation: 关系组件
            economy: 经济组件

        Returns:
            str: 目标描述
        """
        goals = []

        if life_stage == "childhood":
            # 儿童阶段：探索和学习
            goals.extend([
                "探索周围环境",
                "学习基本生存技能",
                "与其他儿童玩耍"
            ])

        elif life_stage == "adolescence":
            # 青少年阶段：发展技能和社交
            goals.extend([
                "学习工作技能",
                "建立友谊",
                "探索个人兴趣"
            ])

            # 性格影响
            if personality and personality.extraversion > 60:
                goals.append("扩展社交圈子")
            if personality and personality.curiosity > 60:
                goals.append("尝试新事物")

        elif life_stage == "adulthood":
            # 成年阶段：事业和家庭
            goals.extend([
                "积累资源和财富",
                "建立稳定的生活"
            ])

            # 根据关系状态调整
            if relation and relation.status == RelationshipStatus.SINGLE:
                goals.append("寻找合适的伴侣")
            elif relation and relation.status == RelationshipStatus.MARRIED:
                goals.append("建立幸福的家庭")
                goals.append("为家庭提供保护")

            # 根据经济状况调整
            if economy and economy.wealth < 100:
                goals.insert(0, "赚取足够的资金")

            # 根据性格调整
            if personality:
                if personality.discipline > 70:
                    goals.append("建造和改进设施")
                if personality.curiosity > 70:
                    goals.append("发现新的地方")

        elif life_stage == "elderhood":
            # 老年阶段：安享晚年和留下遗产
            goals.extend([
                "维持稳定的生活",
                "照顾家庭成员",
                "传承知识给年轻一代",
                "享受生活中的美好"
            ])

        # 通用的长期目标
        goals.extend([
            "保持健康",
            "维持与朋友的关系",
            "寻求安全和稳定"
        ])

        # 根据性格调整
        if personality:
            # 高成就需求
            if personality.discipline > 75:
                goals.append("成为社区的重要成员")
            # 高社交需求
            if personality.kindness > 75:
                goals.append("成为社交的中心")

        # 从目标列表中随机选择（或选择第一个）
        if goals:
            return goals[0]
        else:
            return "活着"
