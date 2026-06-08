#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情感标签

可组合的情感标记，包含主情感、强度和原因。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EmotionalTag:
    """
    情感标签

    Attributes:
        primary: 主情感，如 "fear", "joy", "disgust", "trust", "neutral"
        intensity: 情感强度 0.0~1.0
        reason: 产生该情感的原因描述
    """
    primary: str = "neutral"
    intensity: float = 0.5
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "primary": self.primary,
            "intensity": self.intensity,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmotionalTag":
        return cls(
            primary=data.get("primary", "neutral"),
            intensity=data.get("intensity", 0.5),
            reason=data.get("reason"),
        )

    def transfer_with_loss(self, loss_factor: float = 0.3) -> "EmotionalTag":
        """
        情感传递时的损失。
        叙述传播时，接收者感受到的情感强度会减弱。
        """
        return EmotionalTag(
            primary=self.primary,
            intensity=max(0.0, self.intensity * (1.0 - loss_factor)),
            reason=f"听说: {self.reason}" if self.reason else None,
        )
