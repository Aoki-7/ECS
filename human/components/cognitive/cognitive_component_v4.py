#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:cognitive_component.py
@说明:认知组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto

from core.component import Component


class LearningStyle(Enum):
    """学习风格"""
    VISUAL = auto()         # 视觉学习
    AUDITORY = auto()       # 听觉学习
    KINESTHETIC = auto()    # 动觉学习
    READING = auto()        # 阅读学习
    SOCIAL = auto()         # 社交学习
    SOLITARY = auto()       # 独立学习
    BALANCED = auto()       # 平衡学习


class DecisionStyle(Enum):
    """决策风格"""
    RATIONAL = auto()       # 理性决策
    INTUITIVE = auto()      # 直觉决策
    IMPULSIVE = auto()      # 冲动决策
    CAUTIOUS = auto()       # 谨慎决策
    BALANCED = auto()       # 平衡决策


class RiskPreference(Enum):
    """风险偏好"""
    CONSERVATIVE = auto()   # 保守
    BALANCED = auto()       # 平衡
    ADVENTUROUS = auto()    # 冒险


class ProblemSolvingStage(Enum):
    """问题解决阶段"""
    IDENTIFICATION = auto()  # 问题识别
    GENERATION = auto()      # 方案生成
    EVALUATION = auto()      # 评估选择
    IMPLEMENTATION = auto()  # 实施
    MONITORING = auto()      # 监控


@dataclass(slots=True)
class LearningProgress:
    """学习进度"""
    skill_type: str
    proficiency: float = 0.0        # 熟练度 (0-1)
    experience: float = 0.0         # 经验值
    learning_rate: float = 0.1      # 学习速率
    last_practice: float = 0.0      # 最后练习时间
    practice_count: int = 0         # 练习次数
    
    def practice(self, amount: float = 0.1):
        """练习"""
        self.experience += amount
        self.practice_count += 1
        self.proficiency = min(1.0, self.proficiency + self.learning_rate * amount)
        self.last_practice = 0.0  # 实际应用中应该使用真实时间戳


@dataclass(slots=True)
class Decision:
    """决策"""
    decision_id: int
    problem: str                    # 问题描述
    options: List[str]              # 可选方案
    chosen_option: Optional[str] = None  # 选择的方案
    confidence: float = 0.5         # 信心 (0-1)
    reasoning: str = ""             # 推理过程
    outcome: Optional[float] = None  # 结果 (0-1)
    decision_time: float = 0.0      # 决策时间
    
    def is_made(self) -> bool:
        """是否已做出决策"""
        return self.chosen_option is not None


@dataclass(slots=True)
class Problem:
    """问题"""
    problem_id: int
    description: str                # 问题描述
    complexity: float = 0.5         # 复杂度 (0-1)
    urgency: float = 0.5            # 紧急度 (0-1)
    current_stage: ProblemSolvingStage = ProblemSolvingStage.IDENTIFICATION
    solutions: List[str] = field(default_factory=list)  # 解决方案
    chosen_solution: Optional[str] = None  # 选择的解决方案
    
    def is_solved(self) -> bool:
        """是否已解决"""
        return self.chosen_solution is not None


@dataclass(slots=True)
class CognitiveComponent(Component):
    """
    认知组件 v4.0 - 细化版
    包括学习、决策、问题解决、理解等细化功能。
    """
    
    # === 学习系统 ===
    learning_style: LearningStyle = LearningStyle.BALANCED  # 学习风格
    learning_ability: float = 0.5  # 学习能力 (0-1)
    skills: Dict[str, LearningProgress] = field(default_factory=dict)  # 技能学习进度
    knowledge: Dict[str, float] = field(default_factory=dict)  # 知识掌握程度
    
    # === 决策系统 ===
    decision_style: DecisionStyle = DecisionStyle.BALANCED  # 决策风格
    risk_preference: RiskPreference = RiskPreference.BALANCED  # 风险偏好
    decision_history: List[Decision] = field(default_factory=list)  # 决策历史
    next_decision_id: int = 0
    
    # === 问题解决 ===
    active_problems: Dict[int, Problem] = field(default_factory=dict)  # 活跃问题
    next_problem_id: int = 0
    problem_solving_ability: float = 0.5  # 问题解决能力 (0-1)
    
    # === 理解系统 ===
    comprehension_level: float = 0.5  # 理解水平 (0-1)
    abstraction_ability: float = 0.5  # 抽象能力 (0-1)
    logical_thinking: float = 0.5  # 逻辑思维 (0-1)
    creative_thinking: float = 0.5  # 创造性思维 (0-1)
    
    # === 注意力 ===
    attention_span: float = 0.5  # 注意力持续时间 (0-1)
    focus_ability: float = 0.5  # 专注能力 (0-1)
    current_focus: Optional[str] = None  # 当前关注点
    
    # === 元认知 ===
    metacognition: float = 0.5  # 元认知能力 (0-1)
    self_awareness: float = 0.5  # 自我意识 (0-1)
    learning_strategy: str = "adaptive"  # 学习策略
    
    def learn_skill(self, skill_type: str, practice_amount: float = 0.1):
        """学习技能"""
        if skill_type not in self.skills:
            self.skills[skill_type] = LearningProgress(skill_type=skill_type)
        
        self.skills[skill_type].practice(practice_amount)
    
    def get_skill_proficiency(self, skill_type: str) -> float:
        """获取技能熟练度"""
        if skill_type in self.skills:
            return self.skills[skill_type].proficiency
        return 0.0
    
    def add_knowledge(self, knowledge_type: str, level: float = 0.1):
        """添加知识"""
        if knowledge_type not in self.knowledge:
            self.knowledge[knowledge_type] = 0.0
        
        self.knowledge[knowledge_type] = min(1.0, self.knowledge[knowledge_type] + level)
    
    def get_knowledge_level(self, knowledge_type: str) -> float:
        """获取知识水平"""
        return self.knowledge.get(knowledge_type, 0.0)
    
    def make_decision(self, problem: str, options: List[str]) -> int:
        """做出决策"""
        decision_id = self.next_decision_id
        self.next_decision_id += 1
        
        decision = Decision(
            decision_id=decision_id,
            problem=problem,
            options=options
        )
        
        # 根据决策风格选择方案
        if self.decision_style == DecisionStyle.RATIONAL:
            # 理性决策：选择最优方案
            decision.chosen_option = options[0]  # 简化实现
            decision.confidence = 0.8
        elif self.decision_style == DecisionStyle.INTUITIVE:
            # 直觉决策：凭直觉选择
            import random
            decision.chosen_option = random.choice(options)
            decision.confidence = 0.6
        elif self.decision_style == DecisionStyle.IMPULSIVE:
            # 冲动决策：快速选择
            decision.chosen_option = options[0]
            decision.confidence = 0.4
        elif self.decision_style == DecisionStyle.CAUTIOUS:
            # 谨慎决策：仔细考虑
            decision.chosen_option = options[0]  # 简化实现
            decision.confidence = 0.9
        else:  # BALANCED
            # 平衡决策：综合考虑
            decision.chosen_option = options[0]  # 简化实现
            decision.confidence = 0.7
        
        self.decision_history.append(decision)
        return decision_id
    
    def solve_problem(self, description: str, complexity: float = 0.5, urgency: float = 0.5) -> int:
        """解决问题"""
        problem_id = self.next_problem_id
        self.next_problem_id += 1
        
        problem = Problem(
            problem_id=problem_id,
            description=description,
            complexity=complexity,
            urgency=urgency
        )
        
        # 生成解决方案
        problem.solutions = self._generate_solutions(description, complexity)
        
        # 选择解决方案
        if problem.solutions:
            problem.chosen_solution = problem.solutions[0]  # 简化实现
            problem.current_stage = ProblemSolvingStage.IMPLEMENTATION
        
        self.active_problems[problem_id] = problem
        return problem_id
    
    def _generate_solutions(self, description: str, complexity: float) -> List[str]:
        """生成解决方案"""
        # 简化实现：根据问题复杂度生成不同数量的解决方案
        num_solutions = max(1, int(5 * (1.0 - complexity)))
        solutions = []
        
        for i in range(num_solutions):
            solutions.append(f"方案{i+1}: {description[:20]}...")
        
        return solutions
    
    def update_cognition(self, dt: float):
        """更新认知状态"""
        # 更新技能学习
        for skill in self.skills.values():
            # 技能自然衰减
            decay_rate = 0.01 * dt
            skill.proficiency = max(0.0, skill.proficiency - decay_rate)
        
        # 更新注意力
        self.attention_span = max(0.0, min(1.0, 
            self.attention_span + (0.5 - self.attention_span) * 0.01 * dt))
        
        # 更新理解水平
        self.comprehension_level = max(0.0, min(1.0,
            self.comprehension_level + (0.5 - self.comprehension_level) * 0.005 * dt))
    
    def get_cognitive_summary(self) -> Dict:
        """获取认知摘要"""
        return {
            'learning_style': self.learning_style.name,
            'learning_ability': self.learning_ability,
            'skills_count': len(self.skills),
            'knowledge_count': len(self.knowledge),
            'decision_style': self.decision_style.name,
            'risk_preference': self.risk_preference.name,
            'decisions_made': len(self.decision_history),
            'active_problems': len(self.active_problems),
            'problem_solving_ability': self.problem_solving_ability,
            'comprehension_level': self.comprehension_level,
            'attention_span': self.attention_span
        }
