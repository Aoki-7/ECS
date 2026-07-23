#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:goal_system.py
@说明:目标系统
@时间:2026/04/16
@作者:GitHub Copilot
@版本:2.0

v2.0 拆分：
- 人生阶段判断 -> LifeStageEvaluator
- 目标生成 -> GoalGenerator
- 目标达成检查 -> GoalAchievementChecker
'''

from core.system import System
from core.world import World

from human.components.cognitive.goal_component import GoalComponent
from human.components.cognitive.personality_component import PersonalityComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.gender_component import GenderComponent
from human.components.social.relationship_component import RelationshipComponent, RelationshipStatus
from human.components.economic.economy_component import EconomyComponent

from human.systems.cognitive.life_stage_evaluator import LifeStageEvaluator
from human.systems.cognitive.goal_generator import GoalGenerator
from human.systems.cognitive.goal_achievement_checker import GoalAchievementChecker


class GoalSystem(System):
    tick_interval = 5  # 每5帧执行一次
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

    def __init__(self):
        super().__init__()
        self._stage_evaluator = LifeStageEvaluator(
            childhood=self.CHILDHOOD,
            adolescence=self.ADOLESCENCE,
            adulthood=self.ADULTHOOD,
            elderhood=self.ELDERHOOD,
        )
        self._goal_generator = GoalGenerator()
        self._achievement_checker = GoalAchievementChecker()

    def update(self, world: World, dt: float):
        """
        更新所有实体的目标状态

        Args:
            world: World实例
            dt: 时间增量
        """
        for entity, (goal, age, personality, gender, relation, economy) in world.get_components(
            GoalComponent, LifeCycleComponent, PersonalityComponent, GenderComponent,
            RelationshipComponent, EconomyComponent
        ):
            self._update_goals(
                world, entity,
                goal, age, personality, gender, relation, economy,
                dt
            )

    def _update_goals(self, world: World, entity,
                     goal: GoalComponent, age: LifeCycleComponent,
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
        life_stage = self._stage_evaluator.get_life_stage(age.current_age)

        # 获取或创建当前目标
        if not goal.current_goal:
            goal.current_goal = self._goal_generator.generate_goal_for_stage(
                life_stage, personality, gender, relation, economy
            )

        # 定期检查并更新目标（每10小时检查一次）
        world_time = world.get_time()
        if world_time is None:
            return
        if not hasattr(goal, '_last_update_time'):
            goal._last_update_time = world_time.total_hours

        if world_time.total_hours - goal._last_update_time >= 10:
            # 检查当前目标是否已达成或过期
            if self._achievement_checker.is_goal_achieved(goal, relation, economy):
                # 目标已达成，生成新目标
                goal.current_goal = self._goal_generator.generate_goal_for_stage(
                    life_stage, personality, gender, relation, economy
                )
            elif self._achievement_checker.is_goal_obsolete(goal, life_stage):
                # 目标已过期（例如人生阶段改变），生成新目标
                goal.current_goal = self._goal_generator.generate_goal_for_stage(
                    life_stage, personality, gender, relation, economy
                )

            goal._last_update_time = world_time.total_hours