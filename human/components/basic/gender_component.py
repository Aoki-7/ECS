#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:gender_component.py
@说明:性别组件
@时间:2026/04/14
@作者:GitHub Copilot
@版本:1.0
'''

from enum import Enum
from dataclasses import dataclass

from core.component import Component


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass
class GenderComponent(Component):
    """
    性别组件
    """
    gender: Gender | None = None

    def __post_init__(self):
        # 如果传入 None，默认设为男性
        if self.gender is None:
            self.gender = Gender.MALE

        # 可选：容错字符串输入（更通用）
        elif isinstance(self.gender, str):
            try:
                self.gender = Gender(self.gender.lower())
            except ValueError:
                raise ValueError(f"Invalid gender value: {self.gender}")