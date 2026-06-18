#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
大脑系统

提供 BrainComponent 的静态操作方法。
"""

from human.components.cognitive.brain_component import BrainComponent


class BrainSystem:
    """大脑系统 - 静态方法操作 BrainComponent"""

    @staticmethod
    def set_thought(brain: BrainComponent, thought: str) -> None:
        """设置当前思维"""
        brain.thought = thought
        brain.last_thought = thought
        brain.thought_count += 1

    @staticmethod
    def update_mental_state(brain: BrainComponent, state: str) -> None:
        """更新心理状态"""
        brain.mental_state = state
