#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
世界配置组件 — v4.0 纯数据化

集中管理世界级别的硬编码参数，避免魔法值散布在各系统中。
"""

from dataclasses import dataclass

from core.component import Component
from core.component_serializer import register_component


@register_component
@dataclass(slots=True)
class WorldConfigComponent(Component):
    """
    世界全局配置组件 — 纯数据

    挂载到世界实体上，供各系统查询。
    所有业务逻辑由 WorldConfigSystem 处理。
    """
    map_width: int = 100       # 地图宽度（x 范围: 0 ~ map_width-1）
    map_height: int = 100      # 地图高度（y 范围: 0 ~ map_height-1）
    time_scale: float = 1.0    # 时间加速倍率：1.0 = 实时，>1.0 = 加速
    use_rl_intent: bool = False # 是否使用强化学习驱动的意图系统（默认使用规则驱动）
    rl_training: bool = True   # 是否RL训练模式（True=训练，False=推理）

    def to_dict(self) -> dict:
        return {
            "map_width": self.map_width,
            "map_height": self.map_height,
            "time_scale": self.time_scale,
            "use_rl_intent": self.use_rl_intent,
            "rl_training": self.rl_training,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorldConfigComponent":
        return cls(
            map_width=data.get("map_width", 100),
            map_height=data.get("map_height", 100),
            time_scale=data.get("time_scale", 1.0),
            use_rl_intent=data.get("use_rl_intent", False),
            rl_training=data.get("rl_training", True),
        )
