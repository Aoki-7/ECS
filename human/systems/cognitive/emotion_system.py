#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
情绪系统

提供 EmotionComponent 的静态操作方法。
"""

from typing import Dict

from core.system import System
from core.world import World
from human.components.cognitive.emotion_component import EmotionComponent


class EmotionSystem(System):
    """情绪系统 - ECS System 版本"""
    tick_interval = 1
    priority = 30

    def update(self, world: World, dt: float = 1.0):
        """遍历所有带 EmotionComponent 的实体，执行情绪衰减"""
        for entity, (emotion,) in world.get_components(EmotionComponent):
            # 情绪自然衰减：向中性状态回归
            decay = 0.01 * dt
            emotion.happiness = max(0.0, emotion.happiness - decay)
            emotion.anger = max(0.0, emotion.anger - decay)
            emotion.fear = max(0.0, emotion.fear - decay)
            emotion.joy = max(0.0, emotion.joy - decay)
            emotion.sadness = max(0.0, emotion.sadness - decay)
            emotion.disgust = max(0.0, emotion.disgust - decay)
            emotion.surprise = max(0.0, emotion.surprise - decay)
            emotion.stress = max(0.0, emotion.stress - decay)
            emotion.calmness = min(1.0, emotion.calmness + decay)

    @staticmethod
    def adjust_emotion(emotion: EmotionComponent, emotion_name: str, delta: float) -> None:
        """调整某种情绪的值（限制在 0-1）"""
        if hasattr(emotion, emotion_name):
            new_value = max(0.0, min(1.0, getattr(emotion, emotion_name) + delta))
            setattr(emotion, emotion_name, new_value)

    @staticmethod
    def get_dominant_emotion(emotion: EmotionComponent) -> str:
        """获取当前主导情绪"""
        emotions = {
            "happiness": emotion.happiness,
            "anger": emotion.anger,
            "fear": emotion.fear,
            "joy": emotion.joy,
            "sadness": emotion.sadness,
            "disgust": emotion.disgust,
            "surprise": emotion.surprise,
        }
        dominant = max(emotions, key=emotions.get)
        return dominant if emotions[dominant] > 0.3 else "neutral"

    @staticmethod
    def get_mood_score(emotion: EmotionComponent) -> float:
        """获取心情综合评分 (-1 到 1)"""
        positive = emotion.happiness + emotion.joy + emotion.calmness + emotion.excitement + emotion.hope
        negative = emotion.anger + emotion.fear + emotion.sadness + emotion.disgust + emotion.stress + emotion.frustration + emotion.loneliness
        score = (positive - negative) / 7.0
        return max(-1.0, min(1.0, score))

    @staticmethod
    def get_mood_label(emotion: EmotionComponent) -> str:
        """获取心情标签"""
        score = EmotionSystem.get_mood_score(emotion)
        if score > 0.6:
            return "非常开心"
        elif score > 0.2:
            return "愉快"
        elif score > -0.2:
            return "平静"
        elif score > -0.6:
            return "低落"
        else:
            return "非常低落"

    @staticmethod
    def is_stressed(emotion: EmotionComponent, threshold: float = 0.6) -> bool:
        """是否处于压力状态"""
        return emotion.stress >= threshold

    @staticmethod
    def is_happy(emotion: EmotionComponent, threshold: float = 0.6) -> bool:
        """是否处于快乐状态"""
        return emotion.happiness >= threshold