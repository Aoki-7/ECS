#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:emotion_component.py
@说明:情绪组件 v3.0 - 纯数据版
@时间:2026/06/15
@版本:3.0
'''

from core.component import Component
from dataclasses import dataclass

@dataclass(slots=True)
class EmotionComponent(Component):
    """
    情绪组件 - 纯数据版
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