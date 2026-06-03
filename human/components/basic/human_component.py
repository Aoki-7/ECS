#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:human_component.py
@说明:人类标识组件 - 标记实体为人类的简单组件
@时间:2026/04/18 10:00:00
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from core.component import Component


@dataclass(slots=True)
class HumanComponent(Component):
    """
    人类标识组件

    这是一个简单的标记组件，用于标识实体是否为人类。
    不包含任何数据，只是作为一个类型标记。
    """
    pass