#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结构化感官描述

非量化、模糊、可缺失的感官属性。
例如：生物A可能记得形状但忘了颜色。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SensoryDescription:
    """
    结构化感官描述

    所有字段均为 Optional，表示记忆可能缺失某些属性。
    使用自然语言描述而非数值，体现"不可量化"特性。
    """
    shape: Optional[str] = None        # "圆形", "方形", "不规则", "细长"
    color: Optional[str] = None        # "灰色", "暗红色", "斑驳"
    texture: Optional[str] = None      # "光滑", "粗糙", "有鳞片", "多孔"
    size: Optional[str] = None         # "小", "中等", "巨大", "比拳头大"
    smell: Optional[str] = None        # "无味", "腥味", "花香", "霉味"
    sound: Optional[str] = None        # "无声", "低沉", "尖锐", "沙沙响"
    temperature: Optional[str] = None  # "冰凉", "温暖", "灼热", "常温"

    def to_text(self) -> str:
        """转为自然语言描述（用于叙述传播）"""
        parts = []
        if self.shape:
            parts.append(f"{self.shape}的")
        if self.color:
            parts.append(f"{self.color}的")
        if self.texture:
            parts.append(f"{self.texture}")
        if self.size:
            parts.append(f"{self.size}")
        return "".join(parts) if parts else "某物"

    def to_dict(self) -> dict:
        """序列化为字典"""
        return {
            "shape": self.shape,
            "color": self.color,
            "texture": self.texture,
            "size": self.size,
            "smell": self.smell,
            "sound": self.sound,
            "temperature": self.temperature,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SensoryDescription":
        """从字典反序列化"""
        return cls(
            shape=data.get("shape"),
            color=data.get("color"),
            texture=data.get("texture"),
            size=data.get("size"),
            smell=data.get("smell"),
            sound=data.get("sound"),
            temperature=data.get("temperature"),
        )

    def merge_with(self, other: "SensoryDescription", weight: float = 0.5) -> "SensoryDescription":
        """
        与另一个感官描述合并。
        weight: 0=保留自身, 1=完全采用other, 0.5=平均
        """
        def pick(a, b):
            if a and b:
                return b if weight > 0.5 else a
            return a or b

        return SensoryDescription(
            shape=pick(self.shape, other.shape),
            color=pick(self.color, other.color),
            texture=pick(self.texture, other.texture),
            size=pick(self.size, other.size),
            smell=pick(self.smell, other.smell),
            sound=pick(self.sound, other.sound),
            temperature=pick(self.temperature, other.temperature),
        )