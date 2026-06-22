#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:emotion_component.py
@说明:情绪组件 - 纯数据版

情绪维度（基于 OCC 模型简化）：
- 快乐/悲伤（目标达成/失败）
- 愤怒/恐惧（威胁应对）
- 焦虑/平静（不确定性）
- 惊讶/期待（新奇/预期）
'''

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass(slots=True)
class EmotionComponent(Component):
    """
    情绪组件 - 纯数据版

    Attributes:
        happiness: 快乐度 [-1.0, 1.0]
        sadness: 悲伤度 [-1.0, 1.0]
        anger: 愤怒度 [-1.0, 1.0]
        fear: 恐惧度 [-1.0, 1.0]
        anxiety: 焦虑度 [-1.0, 1.0]
        calmness: 平静度 [-1.0, 1.0]
        surprise: 惊讶度 [-1.0, 1.0]
        anticipation: 期待度 [-1.0, 1.0]
        intensity: 情绪强度 [0.0, 1.0]
        dominant_emotion: 主导情绪名称
        recent_events: 最近引发情绪的事件列表
    """
    happiness: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    anxiety: float = 0.0
    calmness: float = 0.0
    surprise: float = 0.0
    anticipation: float = 0.0
    intensity: float = 0.0
    dominant_emotion: str = "neutral"
    recent_events: List[str] = field(default_factory=list)

    def __post_init__(self):
        # 限制所有情绪值在 [-1.0, 1.0] 范围内
        for attr in ['happiness', 'sadness', 'anger', 'fear', 
                     'anxiety', 'calmness', 'surprise', 'anticipation']:
            value = getattr(self, attr)
            setattr(self, attr, max(-1.0, min(1.0, value)))
        self.intensity = max(0.0, min(1.0, self.intensity))
