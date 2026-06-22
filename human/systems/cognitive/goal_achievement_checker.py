#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:goal_achievement_checker.py
@说明:目标达成检查器

职责：
    - 检查当前目标是否已达成
    - 检查目标是否已过期（人生阶段改变）
'''

from typing import Optional

from human.components.cognitive.goal_component import GoalComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.economic.economy_component import EconomyComponent


class GoalAchievementChecker:
    """目标达成检查器"""

    def is_goal_achieved(self, goal: GoalComponent,
                        relation: Optional[RelationshipComponent],
                        economy: Optional[EconomyComponent]) -> bool:
        """
        检查当前目标是否已达成

        Args:
            goal: 目标组件
            relation: 关系组件
            economy: 经济组件

        Returns:
            bool: 是否已达成
        """
        if not goal.current_goal:
            return True

        current = goal.current_goal

        # 检查各类目标的达成条件
        if "寻找" in current or "伴侣" in current:
            # 寻找伴侣目标：如果已婚或恋爱中，则达成
            if relation and relation.status in ["married", "in_relationship"]:
                return True

        elif "财富" in current or "资金" in current or "赚取" in current:
            # 财富目标：如果财富超过一定阈值，则达成
            if economy and economy.wealth >= 200:
                return True

        elif "家庭" in current or "幸福" in current:
            # 家庭目标：如果已婚且有孩子，则达成
            if relation and relation.status == "married" and relation.children_count > 0:
                return True

        elif "健康" in current:
            # 健康目标：如果健康值高，则达成
            if hasattr(goal, 'health') and goal.health > 80:
                return True

        elif "学习" in current or "技能" in current:
            # 学习目标：如果技能数量超过阈值，则达成
            if hasattr(goal, 'skills') and len(goal.skills) >= 3:
                return True

        elif "探索" in current or "发现" in current:
            # 探索目标：如果已探索地点数量超过阈值，则达成
            if hasattr(goal, 'explored_locations') and len(goal.explored_locations) >= 5:
                return True

        elif "建造" in current or "改进" in current:
            # 建造目标：如果已建造设施数量超过阈值，则达成
            if hasattr(goal, 'built_structures') and len(goal.built_structures) >= 2:
                return True

        elif "社交" in current or "朋友" in current:
            # 社交目标：如果朋友数量超过阈值，则达成
            if hasattr(goal, 'friends') and len(goal.friends) >= 3:
                return True

        elif "传承" in current or "知识" in current:
            # 传承目标：如果已教导人数超过阈值，则达成
            if hasattr(goal, 'students_taught') and goal.students_taught >= 2:
                return True

        # 默认：目标未达成
        return False

    def is_goal_obsolete(self, goal: GoalComponent, current_life_stage: str) -> bool:
        """
        检查目标是否已过期（人生阶段改变导致目标不再适用）

        Args:
            goal: 目标组件
            current_life_stage: 当前人生阶段

        Returns:
            bool: 是否已过期
        """
        if not goal.current_goal:
            return True

        current = goal.current_goal

        # 儿童阶段目标在成年后过期
        if current_life_stage != "childhood" and ("玩耍" in current or "探索" in current):
            return True

        # 青少年阶段目标在成年后过期
        if current_life_stage == "adulthood" and "学习" in current and "技能" in current:
            return True

        # 成年阶段目标在老年后过期
        if current_life_stage == "elderhood" and ("赚取" in current or "工作" in current):
            return True

        # 默认：目标未过期
        return False
