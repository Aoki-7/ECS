#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_component.py
@说明:情绪组件 v2.0
@时间:2026/04/15
@作者:Sherry
@版本:2.0

增强版情绪系统：
- 基础情绪（快乐、愤怒、恐惧、喜悦、悲伤、厌恶、惊讶）
- 复合情绪/心情（压力、平静、信任、孤独、兴奋）
- 情绪状态综合评估
'''

from core.component import Component
from dataclasses import dataclass

@dataclass
class EmotionComponent(Component):
    """
    描述情绪状态的组件。
    包括基础情绪和复合情绪/心情。
    """
    # === 基础情绪 (0-1) ===
    happiness: float = 0.5   # 快乐程度
    anger: float = 0.0       # 愤怒程度
    fear: float = 0.0        # 恐惧程度
    joy: float = 0.0         # 喜悦程度
    sadness: float = 0.0     # 悲伤程度
    disgust: float = 0.0     # 厌恶程度
    surprise: float = 0.0    # 惊讶程度

    # === 复合情绪/心情 (0-1) ===
    stress: float = 0.0      # 压力（口渴+饥饿+疲劳综合）
    calmness: float = 0.5    # 平静度
    trust: float = 0.5       # 对周围环境的信任
    loneliness: float = 0.0  # 孤独感
    excitement: float = 0.0  # 兴奋度
    hope: float = 0.5        # 希望感
    frustration: float = 0.0 # 挫败感

    # === 情绪变化记录 ===
    last_mood_change: str = ""  # 上次情绪变化原因

    def adjust_emotion(self, emotion: str, delta: float):
        """调整某种情绪的值（限制在 0-1）"""
        if hasattr(self, emotion):
            new_value = max(0.0, min(1.0, getattr(self, emotion) + delta))
            setattr(self, emotion, new_value)

    def get_dominant_emotion(self) -> str:
        """获取当前主导情绪"""
        emotions = {
            "happiness": self.happiness,
            "anger": self.anger,
            "fear": self.fear,
            "joy": self.joy,
            "sadness": self.sadness,
            "disgust": self.disgust,
            "surprise": self.surprise,
        }
        dominant = max(emotions, key=emotions.get)
        return dominant if emotions[dominant] > 0.3 else "neutral"

    def get_mood_score(self) -> float:
        """
        获取心情综合评分 (-1 到 1)
        正值表示积极，负值表示消极
        """
        positive = self.happiness + self.joy + self.calmness + self.excitement + self.hope
        negative = self.anger + self.fear + self.sadness + self.disgust + self.stress + self.frustration + self.loneliness
        # 归一化到 -1 ~ 1
        score = (positive - negative) / 7.0
        return max(-1.0, min(1.0, score))

    def get_mood_label(self) -> str:
        """获取心情标签"""
        score = self.get_mood_score()
        if score > 0.6:
            return "非常开心"
        elif score > 0.2:
            return "愉快"
        elif score > -0.2:
            return "平静"
        elif score > -0.6:
            return "低落"
        else:
            return "痛苦"

    def is_stressed(self) -> bool:
        """是否处于压力状态"""
        return self.stress > 0.6 or self.fear > 0.5

    def is_happy(self) -> bool:
        """是否处于快乐状态"""
        return self.get_mood_score() > 0.3
