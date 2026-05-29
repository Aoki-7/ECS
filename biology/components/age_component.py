#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:age_component.py
@说明:年龄组件
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

# 已从 human/components/basic/age_component.py 迁移至此
# 向后兼容导入: from human.components.basic.age_component import AgeComponent
from dataclasses import dataclass

from core.component import Component


@dataclass
class AgeComponent(Component):
    """
    年龄组件
    年龄以年为单位，影响生育能力和行为。
    """
    age: float = 18.0  # 初始年龄18岁

    # 生育年龄范围
    min_reproductive_age: float = 18.0
    max_reproductive_age: float = 50.0

    # 最大寿命（超过此年龄自然死亡）
    max_age: float = 80.0

    def is_reproductive_age(self) -> bool:
        return self.min_reproductive_age <= self.age <= self.max_reproductive_age