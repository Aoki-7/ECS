#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gathering_component.py
@说明:
@时间:2026/04/15 13:10:30
@作者:Sherry
@版本:1.0
'''


from core.component import Component

from dataclasses import dataclass

@dataclass
class GatheringComponent(Component):
    """
    描述采集行为的组件。
    包括采集资源的类型和数量。
    """
    resource_type: str = ""  # 采集的资源类型（如树木、果实）
    amount: float = 0.0       # 采集的资源数量

    def gather(self, resource_type: str, amount: float):
        """采集资源"""
        self.resource_type = resource_type
        self.amount += amount