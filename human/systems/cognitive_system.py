#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:cognitive_system.py
@说明:认知系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional
from core.system import System
from core.world import World
from human.components.cognitive.cognitive_component_v4 import CognitiveComponent, LearningStyle, DecisionStyle
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType

logger = logging.getLogger(__name__)


class CognitiveSystem(System):
    """认知系统 v4.0 - 细化版"""
    tick_interval = 15  # 每15帧更新一次

    def __init__(self):
        self.learning_probability = 0.2  # 学习概率
        self.decision_probability = 0.1  # 决策概率

    def update(self, world: World, dt: float):
        """更新认知系统"""
        for e, (cognitive, human, intent) in world.get_components(
            CognitiveComponent, HumanComponent, IntentComponent
        ):
            entity_id = e.id
            
            # 更新认知状态
            cognitive.update_cognition(dt)
            
            # 处理学习
            self._handle_learning(cognitive, intent, entity_id)
            
            # 处理决策
            self._handle_decision_making(cognitive, intent, entity_id)
            
            # 处理问题解决
            self._handle_problem_solving(cognitive, intent, entity_id)

    def _handle_learning(self, cognitive: CognitiveComponent, intent: IntentComponent, entity_id: int):
        """处理学习"""
        if random.random() < self.learning_probability:
            # 根据意图选择学习内容
            if intent.intent == IntentType.WORK:
                # 工作技能学习
                skill_type = intent.goal_type or "general_work"
                cognitive.learn_skill(skill_type, practice_amount=0.1)
                logger.debug(f"[Cognitive] 实体{entity_id} 学习技能: {skill_type}")
            
            elif intent.intent == IntentType.SOCIALIZE:
                # 社交技能学习
                cognitive.learn_skill("social_interaction", practice_amount=0.1)
                cognitive.add_knowledge("social_norms", level=0.05)
                logger.debug(f"[Cognitive] 实体{entity_id} 学习社交技能")
            
            elif intent.intent == IntentType.EXPLORE:
                # 探索学习
                cognitive.add_knowledge("environment", level=0.1)
                cognitive.learn_skill("navigation", practice_amount=0.1)
                logger.debug(f"[Cognitive] 实体{entity_id} 学习探索技能")
            
            elif intent.intent == IntentType.BUILD:
                # 建造技能学习
                cognitive.learn_skill("construction", practice_amount=0.1)
                cognitive.add_knowledge("engineering", level=0.1)
                logger.debug(f"[Cognitive] 实体{entity_id} 学习建造技能")

    def _handle_decision_making(self, cognitive: CognitiveComponent, intent: IntentComponent, entity_id: int):
        """处理决策"""
        if random.random() < self.decision_probability:
            # 根据当前情况做出决策
            if intent.intent == IntentType.IDLE:
                # 空闲时做出下一步决策
                problem = "接下来做什么？"
                options = ["工作", "社交", "探索", "休息"]
                
                decision_id = cognitive.make_decision(problem, options)
                decision = cognitive.decision_history[-1]
                
                # 根据决策结果调整意图
                if decision.chosen_option == "工作":
                    intent.intent = IntentType.WORK
                elif decision.chosen_option == "社交":
                    intent.intent = IntentType.SOCIALIZE
                elif decision.chosen_option == "探索":
                    intent.intent = IntentType.EXPLORE
                else:
                    intent.intent = IntentType.REST
                
                logger.debug(f"[Cognitive] 实体{entity_id} 做出决策: {decision.chosen_option}")

    def _handle_problem_solving(self, cognitive: CognitiveComponent, intent: IntentComponent, entity_id: int):
        """处理问题解决"""
        # 检查是否有活跃问题
        if not cognitive.active_problems:
            # 随机生成问题
            if random.random() < 0.05:  # 5%概率生成问题
                problems = [
                    "如何提高效率？",
                    "如何改善关系？",
                    "如何解决冲突？",
                    "如何学习新技能？",
                    "如何适应环境？"
                ]
                
                problem_description = random.choice(problems)
                complexity = random.uniform(0.3, 0.8)
                urgency = random.uniform(0.2, 0.7)
                
                problem_id = cognitive.solve_problem(problem_description, complexity, urgency)
                logger.debug(f"[Cognitive] 实体{entity_id} 面对问题: {problem_description}")

    def get_cognitive_statistics(self, world: World) -> Dict:
        """获取认知统计"""
        total_entities = 0
        total_skills = 0
        total_knowledge = 0
        total_decisions = 0
        total_problems = 0
        
        for e, (cognitive, human) in world.get_components(CognitiveComponent, HumanComponent):
            total_entities += 1
            total_skills += len(cognitive.skills)
            total_knowledge += len(cognitive.knowledge)
            total_decisions += len(cognitive.decision_history)
            total_problems += len(cognitive.active_problems)
        
        return {
            'total_entities': total_entities,
            'total_skills': total_skills,
            'total_knowledge': total_knowledge,
            'total_decisions': total_decisions,
            'total_problems': total_problems,
            'average_skills_per_entity': total_skills / total_entities if total_entities > 0 else 0.0,
            'average_knowledge_per_entity': total_knowledge / total_entities if total_entities > 0 else 0.0
        }
