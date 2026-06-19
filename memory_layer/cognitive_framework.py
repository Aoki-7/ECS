#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认知框架

模拟不同主体的认知偏差和感知滤镜。
不同物种/个体对同一事物有不同的认知框架，导致记忆形成时的系统性偏差。
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .sensory_description import SensoryDescription


@dataclass
class CognitiveFramework:
    """
    认知框架

    定义主体如何"看世界"的滤镜。
    影响：
    1. 注意力分配（哪些属性更容易被注意到）
    2. 解释偏差（如何解释感知到的信息）
    3. 记忆重构（回忆时如何填补空白）
    """
    # 注意力权重：哪些感官属性更容易被注意到
    attention_weights: Dict[str, float] = field(default_factory=lambda: {
        "shape": 1.0,
        "color": 1.0,
        "texture": 1.0,
        "size": 1.0,
        "smell": 1.0,
        "sound": 1.0,
        "temperature": 1.0,
    })

    # 解释偏差：对某些特征的系统性误解
    interpretation_bias: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)
    # 例如：{"color": {"灰色": ["暗色", "灰白色"]}}

    # 恐惧滤镜：对威胁相关特征的高敏感度
    threat_sensitivity: float = 0.5  # 0.0~1.0

    # 好奇滤镜：对新奇特征的高敏感度
    curiosity_level: float = 0.5  # 0.0~1.0

    # 文化/物种背景影响
    background_knowledge: List[str] = field(default_factory=list)
    # 例如：["知道火是危险的", "认为圆形石头可以滚动"]

    def apply_attention_filter(
        self,
        description: SensoryDescription,
        base_attention: float = 0.5,
    ) -> SensoryDescription:
        """
        应用注意力滤镜。

        高权重的属性更容易被注意到，低权重的可能被忽略。
        """
        result = SensoryDescription()

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(description, field)
            if value is None:
                continue

            weight = self.attention_weights.get(field, 1.0)
            # 注意力权重越高，越不容易丢失信息
            missing_probability = 1.0 - (base_attention * weight)

            if random.random() > missing_probability:
                setattr(result, field, value)

        return result

    def apply_interpretation_bias(
        self,
        description: SensoryDescription,
    ) -> SensoryDescription:
        """
        应用解释偏差。

        根据认知框架重新解释感知到的信息。
        """
        result = SensoryDescription()

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(description, field)
            if value is None:
                continue

            # 检查是否有解释偏差
            field_bias = self.interpretation_bias.get(field, {})
            if value in field_bias:
                # 有偏差：从替代选项中随机选择
                alternatives = field_bias[value]
                setattr(result, field, random.choice(alternatives))
            else:
                # 无偏差：保持原值
                setattr(result, field, value)

        return result

    def apply_threat_filter(
        self,
        description: SensoryDescription,
        is_threat: bool = False,
    ) -> SensoryDescription:
        """
        应用威胁滤镜。

        高威胁敏感度时，威胁相关特征会被放大/扭曲。
        """
        if not is_threat or self.threat_sensitivity < 0.3:
            return description

        result = SensoryDescription()

        # 复制所有字段
        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(description, field)
            setattr(result, field, value)

        # 威胁滤镜：大小被夸大
        if result.size:
            size_exaggeration = {
                "小": "中等",
                "中等": "大",
                "大": "巨大",
                "巨大": "极其巨大",
            }
            if result.size in size_exaggeration:
                result.size = size_exaggeration[result.size]

        # 威胁滤镜：声音变得更可怕
        if result.sound:
            sound_distortion = {
                "无声": "低沉",
                "低沉": "威胁性低吼",
                "沙沙响": "刺耳",
            }
            if result.sound in sound_distortion:
                result.sound = sound_distortion[result.sound]

        return result

    def reconstruct_memory(
        self,
        partial_description: SensoryDescription,
    ) -> SensoryDescription:
        """
        记忆重构：用背景知识填补空白。

        当记忆不完整时，主体会用已有知识"填补"缺失的部分。
        """
        result = SensoryDescription()

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(partial_description, field)
            if value is not None:
                setattr(result, field, value)
                continue

            # 缺失：尝试用背景知识填补
            reconstructed = self._reconstruct_field(field, partial_description)
            if reconstructed:
                setattr(result, field, reconstructed)

        return result

    def _reconstruct_field(
        self,
        field: str,
        context: SensoryDescription,
    ) -> Optional[str]:
        """基于上下文重构单个字段"""
        # 简化版：基于常见关联推断
        associations = {
            "shape": {
                "圆形": {"color": "灰色", "texture": "光滑"},
                "四足": {"texture": "毛茸茸", "sound": "脚步声"},
            },
            "color": {
                "灰色": {"texture": "粗糙", "temperature": "冰凉"},
                "绿色": {"texture": "有机", "smell": "草味"},
            },
        }

        # 查找已知字段的关联
        for known_field in ["shape", "color", "texture"]:
            known_value = getattr(context, known_field)
            if known_value and known_field in associations:
                if known_value in associations[known_field]:
                    field_associations = associations[known_field][known_value]
                    if field in field_associations:
                        return field_associations[field]

        return None


def create_animal_framework(species: str = "basic") -> CognitiveFramework:
    """创建动物的认知框架"""
    framework = CognitiveFramework()

    if species == "predator":
        # 捕食者：对运动和大小敏感
        framework.attention_weights = {
            "shape": 0.8,
            "color": 0.5,
            "texture": 0.6,
            "size": 1.2,  # 特别关注大小（判断是否是猎物）
            "smell": 1.0,
            "sound": 1.1,  # 关注声音（追踪猎物）
            "temperature": 0.7,
        }
        framework.threat_sensitivity = 0.3  # 低威胁敏感度（自己是威胁）
        framework.curiosity_level = 0.7

    elif species == "prey":
        # 猎物：对威胁特征高度敏感
        framework.attention_weights = {
            "shape": 1.0,
            "color": 0.6,
            "texture": 0.7,
            "size": 1.3,  # 特别关注大小（判断是否是捕食者）
            "smell": 1.2,  # 关注气味（捕食者的气味）
            "sound": 1.2,  # 关注声音（捕食者的声音）
            "temperature": 0.5,
        }
        framework.threat_sensitivity = 0.9  # 高威胁敏感度
        framework.curiosity_level = 0.3  # 低好奇心（谨慎）

    else:
        # 默认框架
        pass

    return framework


def create_human_framework(culture: str = "default") -> CognitiveFramework:
    """创建人类的认知框架"""
    framework = CognitiveFramework()

    # 人类：对颜色和形状敏感（用于识别和分类）
    framework.attention_weights = {
        "shape": 1.1,
        "color": 1.2,
        "texture": 0.9,
        "size": 0.8,
        "smell": 0.7,
        "sound": 0.8,
        "temperature": 0.5,
    }

    # 人类有文化解释偏差
    framework.interpretation_bias = {
        "color": {
            "红色": ["暗红色", "血红色", "鲜艳的红"],
            "黑色": ["深黑色", "暗色", "漆黑"],
        },
        "shape": {
            "不规则": ["奇特形状", "怪异形状", "独特形状"],
        },
    }

    framework.threat_sensitivity = 0.6
    framework.curiosity_level = 0.8

    return framework
