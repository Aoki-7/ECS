#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_component.py
@说明:情绪组件 - 统一入口（转发到v4版本）
@时间:2026/07/20
@版本:4.0

注意：此文件现在重定向到 emotion_component_v4.py，以实现版本统一。
旧的 v3 实现已备份到 emotion_component_legacy.py。
'''

from human.components.cognitive.emotion_component_v4 import (
    EmotionComponent,
    EmotionState,
    EmotionIntensity,
    EmotionDuration,
    BasicEmotion,
    ComplexEmotion,
)

__all__ = [
    "EmotionComponent",
    "EmotionState",
    "EmotionIntensity",
    "EmotionDuration",
    "BasicEmotion",
    "ComplexEmotion",
]