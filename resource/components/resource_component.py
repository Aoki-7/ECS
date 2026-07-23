#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:resource_component.py
@说明:通用资源组件（纯数据版）
@时间:2026/04/16 20:25:07
@作者:Sherry
@版本:3.0

设计原则：
- 纯数据容器，无业务逻辑
- 所有操作（consume/add/regenerate）移至 ResourceSystem
'''

from core.component import Component
from core.component_serializer import register_component
from dataclasses import dataclass, field
from typing import Dict, Any

from .base_resource_component import ResourceState


@register_component
@dataclass
class ResourceComponent(Component):
    """
    描述环境中的资源（纯数据版）。

    属性:
        resource_type: 资源类型（如树木、果实、动物）
        amount: 当前资源数量
        max_amount: 资源最大容量
        quality: 资源质量（0.0-1.0）
        regenerable: 是否可再生
        regen_rate: 再生速率（单位/时间）
        state: 资源当前状态
        metadata: 自定义元数据字典
    """
    resource_type: str
    amount: float = 0.0
    max_amount: float = 100.0
    quality: float = 1.0
    regenerable: bool = False
    regen_rate: float = 0.0
    state: ResourceState = ResourceState.AVAILABLE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "resource_type": self.resource_type,
            "amount": self.amount,
            "max_amount": self.max_amount,
            "quality": self.quality,
            "regenerable": self.regenerable,
            "regen_rate": self.regen_rate,
            "state": self.state.name,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResourceComponent":
        state = ResourceState.AVAILABLE
        state_name = data.get("state", "AVAILABLE")
        try:
            state = ResourceState[state_name]
        except KeyError:
            state = ResourceState.AVAILABLE
        return cls(
            resource_type=data.get("resource_type", ""),
            amount=data.get("amount", 0.0),
            max_amount=data.get("max_amount", 100.0),
            quality=data.get("quality", 1.0),
            regenerable=data.get("regenerable", False),
            regen_rate=data.get("regen_rate", 0.0),
            state=state,
            metadata=data.get("metadata", {}),
        )

    def __post_init__(self):
        """初始化后验证（仅数据验证，无业务逻辑）"""
        # 验证数量
        if self.amount < 0:
            self.amount = 0
        if self.max_amount <= 0:
            self.max_amount = 100.0
        if self.amount > self.max_amount:
            self.amount = self.max_amount
        
        # 验证质量
        if self.quality < 0.0:
            self.quality = 0.0
        elif self.quality > 1.0:
            self.quality = 1.0
        
        # 根据当前数量更新资源状态（仅状态同步，无业务逻辑）
        if self.state == ResourceState.LOCKED:
            return
        if self.amount <= 0:
            self.state = ResourceState.DEPLETED
        elif self.amount < self.max_amount and self.regenerable:
            self.state = ResourceState.REGENERATING
        else:
            self.state = ResourceState.AVAILABLE