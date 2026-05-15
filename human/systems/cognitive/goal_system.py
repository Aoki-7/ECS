#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:goal_system.py
@说明:目标系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:1.0
'''

from core.system import System
from core.world import World

from human.components.cognitive.goal_component import GoalComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.basic.age_component import AgeComponent
from human.components.basic.gender_component import GenderComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.economic.economy_component import EconomyComponent


class GoalSystem(System):
    """
    目标系统
    
    管理实体的长期目标，根据年龄阶段、性格和生活进度来动态调整。
    
    目标类型：
    - 生存目标：找到食物、保持健康
    - 发展目标：积累资源、学习技能、建造设施
    - 社交目标：建立友谊、寻找伴侣、组织家庭
    - 成就目标：成为领导、被尊敬、留下遗产
    """

    # 人生阶段定义（年龄）
    CHILDHOOD = (0, 12)          # 儿童：0-12岁
    ADOLESCENCE = (12, 18)        # 青少年：12-18岁
    ADULTHOOD = (18, 65)          # 成年：18-65岁
    ELDERHOOD = (65, 150)         # 老年：65+岁

    def update(self, world: World, dt: float):
        """
        更新所有实体的目标状态
        
        Args:
            world: World实例
            dt: 时间增量
        """
        for entity, (goal, age, personality, gender, relation, economy) in world.get_components(
            GoalComponent, AgeComponent, PersonalityComponent, GenderComponent, 
            RelationshipComponent, EconomyComponent
        ):
            self._update_goals(
                world, entity,
                goal, age, personality, gender, relation, economy,
                dt
            )

    def _update_goals(self, world: World, entity,
                     goal: GoalComponent, age: AgeComponent, 
                     personality: PersonalityComponent, gender: GenderComponent,
                     relation: RelationshipComponent, economy: EconomyComponent,
                     dt: float):
        """
        更新单个实体的目标
        
        Args:
            world: World实例
            entity: 实体ID
            goal: 目标组件
            age: 年龄组件
            personality: 性格组件
            gender: 性别组件
            relation: 关系组件
            economy: 经济组件
            dt: 时间增量
        """
        # 确定人生阶段
        life_stage = self._get_life_stage(age.age)
        
        # 获取或创建当前目标
        if not goal.current_goal:
            goal.current_goal = self._generate_goal_for_stage(
                world, entity, life_stage, personality, gender, relation, economy
            )
        
        # 定期检查并更新目标（每10小时检查一次）
        world_time = world.get_time()
        if not hasattr(goal, '_last_update_time'):
            goal._last_update_time = world_time.total_hours
        
        if world_time.total_hours - goal._last_update_time >= 10:
            # 检查当前目标是否已达成或过期
            if self._is_goal_achieved(world, entity, goal, relation, economy):
                # 目标已达成，生成新目标
                goal.current_goal = self._generate_goal_for_stage(
                    world, entity, life_stage, personality, gender, relation, economy
                )
            elif self._is_goal_obsolete(world, entity, goal, life_stage):
                # 目标已过期（例如人生阶段改变），生成新目标
                goal.current_goal = self._generate_goal_for_stage(
                    world, entity, life_stage, personality, gender, relation, economy
                )
            
            goal._last_update_time = world_time.total_hours

    def _get_life_stage(self, age: float) -> str:
        """
        根据年龄确定人生阶段
        
        Args:
            age: 年龄（岁）
            
        Returns:
            str: 人生阶段标识
        """
        if age < self.CHILDHOOD[1]:
            return "childhood"
        elif age < self.ADOLESCENCE[1]:
            return "adolescence"
        elif age < self.ADULTHOOD[1]:
            return "adulthood"
        else:
            return "elderhood"

    def _generate_goal_for_stage(self, world: World, entity,
                                life_stage: str, personality: PersonalityComponent,
                                gender: GenderComponent, relation: RelationshipComponent,
                                economy: EconomyComponent) -> str:
        """
        根据人生阶段生成适当的目标
        
        Args:
            world: World实例
            entity: 实体ID
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
            if personality and personality.openness > 60:
                goals.append("尝试新事物")
        
        elif life_stage == "adulthood":
            # 成年阶段：事业和家庭
            goals.extend([
                "积累资源和财富",
                "建立稳定的生活"
            ])
            
            # 根据关系状态调整
            if relation.status == RelationshipStatus.SINGLE:
                goals.append("寻找合适的伴侣")
            elif relation.status == RelationshipStatus.MARRIED:
                goals.append("建立幸福的家庭")
                goals.append("为家庭提供保护")
            
            # 根据经济状况调整
            if economy.money < 100:
                goals.insert(0, "赚取足够的资金")
            
            # 根据性格调整
            if personality:
                if personality.conscientiousness > 70:
                    goals.append("建造和改进设施")
                if personality.openness > 70:
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
            if personality.conscientiousness > 75:
                goals.append("成为社区的重要成员")
            # 高社交需求
            if personality.extraversion > 75:
                goals.append("成为社交的中心")
        
        # 从目标列表中随机选择（或选择第一个）
        if goals:
            return goals[0]
        else:
            return "活着"

    def _is_goal_achieved(self, world: World, entity, goal: GoalComponent,
                         relation: RelationshipComponent, economy: EconomyComponent) -> bool:
        """
        检查当前目标是否已达成
        
        Args:
            world: World实例
            entity: 实体ID
            goal: 目标组件
            relation: 关系组件
            economy: 经济组件
            
        Returns:
            bool: 是否已达成
        """
        if not goal.current_goal:
            return False
        
        current = goal.current_goal.lower()
        
        # 简化的目标达成判断
        if "伴侣" in current or "配偶" in current:
            return relation.status in [RelationshipStatus.MARRIED, RelationshipStatus.ENGAGED]
        
        if "资源" in current or "金钱" in current or "资金" in current:
            return economy.money >= 500
        
        # 其他目标判断可在这里添加
        
        return False

    def _is_goal_obsolete(self, world: World, entity, goal: GoalComponent,
                         current_life_stage: str) -> bool:
        """
        检查目标是否已过期
        
        Args:
            world: World实例
            entity: 实体ID
            goal: 目标组件
            current_life_stage: 当前人生阶段
            
        Returns:
            bool: 是否已过期
        """
        # 简化实现：不同人生阶段的目标可能需要改变
        # 这可以通过存储目标生成时的阶段来检查
        
        return False

