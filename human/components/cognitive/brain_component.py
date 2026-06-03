#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:brain_component.py
@说明:思维组件 v2.0
@时间:2026/03/13
@作者:Sherry
@版本:2.0

增强版思维系统：
- 当前思维/内心独白
- 专注目标
- 心理状态（正常/压力/困惑/兴奋/抑郁）
- 决策信心
- 思维队列（最近的想法）
'''

from dataclasses import dataclass, field

from core.component import Component

@dataclass(slots=True)
class BrainComponent(Component):
    """
        思维组件
        整合情绪、记忆、目标，生成当前思维状态
    """
    # 当前思维/内心独白
    current_thought: str = ""
    
    # 专注目标实体ID
    focus_target: int = None
    
    # 心理状态
    mental_state: str = "normal"  # normal/stressed/confused/excited/depressed/calm
    
    # 决策信心 (0-1)
    decision_confidence: float = 1.0
    
    # 思维队列（最近的想法，用于调试和叙事）
    thought_history: list = field(default_factory=list)
    
    # 当前行为模式
    behavior_mode: str = "idle"  # idle/survival/social/explore/work/escape/rest
    
    def set_thought(self, thought: str):
        """设置当前思维，并记录到历史"""
        self.current_thought = thought
        self.thought_history.append(thought)
        # 只保留最近20条
        if len(self.thought_history) > 20:
            self.thought_history.pop(0)
    
    def update_mental_state(self, emotion_score: float, stress_level: float):
        """根据情绪评分和压力更新心理状态"""
        if stress_level > 0.7:
            self.mental_state = "stressed"
        elif emotion_score > 0.5:
            self.mental_state = "excited"
        elif emotion_score < -0.5:
            self.mental_state = "depressed"
        elif stress_level > 0.4:
            self.mental_state = "confused"
        elif emotion_score > 0.1:
            self.mental_state = "calm"
        else:
            self.mental_state = "normal"
