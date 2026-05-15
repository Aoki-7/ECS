#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_component.py
@说明:情绪组件
@时间:2026/04/15 10:38:10
@作者:Sherry
@版本:1.0
'''



from core.component import Component
from dataclasses import dataclass

@dataclass
class EmotionComponent(Component):
    """
    描述情绪状态的组件。
    包括快乐、愤怒、恐惧等情绪。
    """
    happiness: float = 0.5   # 快乐程度（0-1）
    anger: float = 0.0       # 愤怒程度（0-1）
    fear: float = 0.0        # 恐惧程度（0-1）
    joy: float = 0.0         # 喜悦程度（0-1）
    sadness: float = 0.0     # 悲伤程度（0-1）
    disgust: float = 0.0     # 厌恶程度（0-1）
    surprise: float = 0.0     # 惊讶程度（0-1）
    neutral: float = 0.0      # 中性程度（0-1）

    def adjust_emotion(self, emotion: str, delta: float):
        """调整某种情绪的值"""
        if hasattr(self, emotion):
            new_value = max(0.0, min(1.0, getattr(self, emotion) + delta))
            setattr(self, emotion, new_value)