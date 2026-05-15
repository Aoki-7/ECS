#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:identity_component.py
@说明:人物身份组件
@时间:2026/03/13 11:08:20
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass

from core.component import Component


@dataclass
class IdentityComponent(Component):
    """
    人物身份组件
    
    仅包含身份相关的信息，年龄和性别应分别使用 AgeComponent 和 GenderComponent。
    
    Args:
        name: 人物名称
        faction: 阵营/组织
    """
    name: str = ""              # 人物名称
    faction: str = ""           # 阵营/组织