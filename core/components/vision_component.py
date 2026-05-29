#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:vision_component.py
@说明:感知范围组件
@时间:2026/03/28 17:27:08
@作者:Sherry
@版本:1.0
'''

# 已从 human/components/abilities/vision_component.py 迁移至此
# 向后兼容导入: from human.components.abilities.vision_component import VisionComponent
from dataclasses import dataclass, field
from core.component import Component


@dataclass
class VisionComponent(Component):
    """感知范围组件"""
    radius: int = 12

    entities: list = field(default_factory=list)
    entity_ids: list = field(default_factory=list)
