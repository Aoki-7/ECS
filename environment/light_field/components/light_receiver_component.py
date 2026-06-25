#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:light_receive_component.py
@说明:光照接受组件
@时间:2026/03/11 14:41:13
@作者:Sherry
@版本:1.0
'''

"""
光照接收组件

任何位于空间中的实体都可以接收光照
例如：
- 植物
- 动物
- 地表
- 建筑
- 水面
"""

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class LightReceiverComponent(Component):

    # ===
    # 接收光照
    # ===

    received_direct: float = 0.0
    received_diffuse: float = 0.0
    received_total: float = 0.0

    # ===
    # 遮挡
    # ===

    shade_ratio: float = 0.0   # 0-1 遮挡比例

    # ===
    # 反射率（用于能量系统）
    # ===

    albedo: float = 0.2

    def to_dict(self):
        return {
            "直射光": self.received_direct,
            "散射光": self.received_diffuse,
            "总光": self.received_total,
            "遮挡": self.shade_ratio,
            "反射率": self.albedo
        }