#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@文件:base_resource_component.py
@说明:资源组件基类 - 纯数据版

提取 food/metal/stone/wood 的公共字段和方法，
减少重复代码。
'''

from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum, auto

from core.component import Component
from core.component_serializer import register_component


class ResourceState(Enum):
    """资源状态枚举"""
    AVAILABLE = auto()      # 可用
    DEPLETED = auto()       # 耗尽
    LOCKED = auto()         # 锁定
    REGENERATING = auto()   # 再生中


@register_component
@dataclass(slots=True)
class BaseResourceComponent(Component):
    """
    资源组件基类 - 纯数据版

    所有资源组件的公共字段：
    - amount: 当前数量
    - max_amount: 最大容量
    - quality: 质量 0-1
    - state: 资源状态
    - metadata: 元数据
    """
    amount: float = 1.0
    max_amount: float = 100.0
    quality: float = 1.0
    state: ResourceState = ResourceState.AVAILABLE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "amount": self.amount,
            "max_amount": self.max_amount,
            "quality": self.quality,
            "state": self.state.name,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BaseResourceComponent":
        state = ResourceState.AVAILABLE
        state_name = data.get("state", "AVAILABLE")
        try:
            state = ResourceState[state_name]
        except KeyError:
            state = ResourceState.AVAILABLE
        return cls(
            amount=data.get("amount", 1.0),
            max_amount=data.get("max_amount", 100.0),
            quality=data.get("quality", 1.0),
            state=state,
            metadata=data.get("metadata", {}),
        )

    def __post_init__(self):
        """初始化后验证"""
        self.amount = max(0.0, min(self.amount, self.max_amount))
        self.quality = max(0.0, min(self.quality, 1.0))