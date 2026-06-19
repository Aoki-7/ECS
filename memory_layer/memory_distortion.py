#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆扭曲引擎

实现传话游戏效应：记忆在多次传播中的系统性失真。

核心算法：
1. 信息损失：叙述者无法完美表达记忆
2. 认知偏差：接收者基于自身框架重新解释
3. 情感传染：情感在传播中放大或减弱
4. 细节填充：缺失的细节被想象填补
"""

import random
from typing import Optional

from .sensory_description import SensoryDescription
from .emotional_tag import EmotionalTag
from .cognitive_framework import CognitiveFramework


class MemoryDistortionEngine:
    """
    记忆扭曲引擎

    模拟记忆在人际传播中的失真过程。
    """

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)

    def distort(
        self,
        original_description: SensoryDescription,
        original_emotion: EmotionalTag,
        narrator_confidence: float,
        receiver_framework: Optional[CognitiveFramework] = None,
        is_threat_context: bool = False,
    ) -> tuple[SensoryDescription, EmotionalTag, float]:
        """
        对记忆进行扭曲。

        Args:
            original_description: 原始感官描述
            original_emotion: 原始情感
            narrator_confidence: 叙述者确信度（影响信息保留率）
            receiver_framework: 接收者认知框架（影响解释偏差）
            is_threat_context: 是否威胁上下文（影响威胁滤镜）

        Returns:
            (扭曲后的描述, 扭曲后的情感, 新的确信度)
        """
        # 步骤1：信息损失（叙述者无法完美表达）
        after_loss = self._apply_information_loss(
            original_description, narrator_confidence
        )

        # 步骤2：认知偏差（接收者重新解释）
        if receiver_framework:
            after_bias = receiver_framework.apply_interpretation_bias(after_loss)
            after_attention = receiver_framework.apply_attention_filter(after_bias)
            after_threat = receiver_framework.apply_threat_filter(
                after_attention, is_threat_context
            )
            after_reconstruct = receiver_framework.reconstruct_memory(after_threat)
        else:
            after_reconstruct = after_loss

        # 步骤3：情感传染
        after_emotion = self._apply_emotion_contagion(
            original_emotion, narrator_confidence
        )

        # 步骤4：确信度衰减
        new_confidence = narrator_confidence * 0.5  # 间接记忆确信度减半

        return after_reconstruct, after_emotion, new_confidence

    def _apply_information_loss(
        self,
        description: SensoryDescription,
        confidence: float,
    ) -> SensoryDescription:
        """
        应用信息损失。

        确信度越低，丢失的信息越多。
        """
        loss_probability = 1.0 - confidence
        result = SensoryDescription()

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(description, field)
            if value is None:
                continue

            # 确信度越低，越可能丢失
            if self._rng.random() < loss_probability:
                continue  # 丢失此信息

            # 即使没丢失，也可能变得模糊
            if self._rng.random() < loss_probability * 0.5:
                value = self._make_vague(value)

            setattr(result, field, value)

        return result

    def _make_vague(self, value: str) -> str:
        """使描述变得模糊"""
        vague_prefixes = ["好像", "可能是", "看起来", "大概"]
        prefix = self._rng.choice(vague_prefixes)
        return f"{prefix}{value}"

    def _apply_emotion_contagion(
        self,
        emotion: EmotionalTag,
        narrator_confidence: float,
    ) -> EmotionalTag:
        """
        应用情感传染。

        情感在传播中会：
        - 强度减弱（无法完全传达情感）
        - 可能产生情感类型偏差（恐惧→好奇）
        """
        # 情感强度减弱
        new_intensity = emotion.intensity * narrator_confidence * 0.7

        # 小概率情感类型变化
        if self._rng.random() < 0.1:
            # 情感类型轻微偏移
            emotion_shifts = {
                "fear": ["caution", "unease"],
                "joy": ["contentment", "amusement"],
                "disgust": ["dislike", "aversion"],
                "anger": ["irritation", "frustration"],
            }
            if emotion.primary in emotion_shifts:
                new_primary = self._rng.choice(emotion_shifts[emotion.primary])
            else:
                new_primary = emotion.primary
        else:
            new_primary = emotion.primary

        return EmotionalTag(
            primary=new_primary,
            intensity=max(0.0, min(1.0, new_intensity)),
            reason=f"听说: {emotion.reason}" if emotion.reason else None,
        )

    def calculate_distortion_level(
        self,
        original: SensoryDescription,
        distorted: SensoryDescription,
    ) -> float:
        """
        计算两个描述之间的扭曲度。

        Returns:
            0.0~1.0，越高表示扭曲越严重
        """
        total_fields = 0
        mismatch_count = 0

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            orig_val = getattr(original, field)
            dist_val = getattr(distorted, field)

            if orig_val is None and dist_val is None:
                continue

            total_fields += 1

            if orig_val is None or dist_val is None:
                mismatch_count += 1
            elif orig_val != dist_val:
                mismatch_count += 1

        if total_fields == 0:
            return 0.0

        return mismatch_count / total_fields


def simulate_telephone_game(
    engine: MemoryDistortionEngine,
    original_description: SensoryDescription,
    original_emotion: EmotionalTag,
    chain_length: int = 5,
    initial_confidence: float = 0.95,
) -> list[tuple[SensoryDescription, EmotionalTag, float]]:
    """
    模拟传话游戏效应。

    返回传播链上每个节点的（描述, 情感, 确信度）。
    """
    chain = [(original_description, original_emotion, initial_confidence)]

    current_description = original_description
    current_emotion = original_emotion
    current_confidence = initial_confidence

    for _ in range(chain_length):
        new_desc, new_emotion, new_conf = engine.distort(
            current_description,
            current_emotion,
            current_confidence,
        )
        chain.append((new_desc, new_emotion, new_conf))

        current_description = new_desc
        current_emotion = new_emotion
        current_confidence = new_conf

    return chain
