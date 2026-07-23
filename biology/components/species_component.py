#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:biology_component.py
@说明:生物属性组件
@时间:2026/03/19 13:21:44
@作者:Sherry
@版本:1.0
'''

# 已从 human/components/biology/biology_component.py 迁移至此
# 向后兼容导入: from human.components.biology.biology_component import SpeciesComponent
from dataclasses import dataclass

from core.component import Component


@dataclass
class SpeciesComponent(Component):
    """
    物种属性组件
    
    包含物种相关的属性。年龄应使用 AgeComponent，性别应使用 GenderComponent。
    
    Args:
        species: 物种名称
    """
    species: str = "Human"      # 物种名称
