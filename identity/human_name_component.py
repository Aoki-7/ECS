#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:human_name_component.py
@说明:人类命名组件
@时间:2026/03/24 11:26:28
@作者:Sherry
@版本:1.0
'''



from dataclasses import dataclass, field
from typing import Optional, List

from core.component import Component


@dataclass
class HumanNameComponent(Component):
    """
    人类命名组件（结构化命名）

    Attributes:
        given_name: 名
        family_name: 姓
        middle_name: 中间名（西方）
        prefix: 前缀（Mr., Dr.）
        suffix: 后缀（Jr., III）

        gender: 性别（用于名字生成）
        culture: 文化（chinese / western / japanese 等）
        language: 语言（zh / en / jp）

        nickname: 昵称
        former_names: 曾用名（结婚/改名等）
    """

    # ===== 核心结构 =====
    given_name: str
    family_name: str

    middle_name: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    # ===== 语义信息 =====
    gender: Optional[str] = None
    culture: str = "generic"
    language: str = "en"

    # ===== 扩展信息 =====
    nickname: Optional[str] = None
    former_names: List[str] = field(default_factory=list)

    # ===== 核心方法 =====
    def get_full_name(self) -> str:
        """
        根据文化规则生成完整姓名
        """

        if self.culture == "chinese":
            # 中文：姓 + 名
            return f"{self.family_name}{self.given_name}"

        elif self.culture == "japanese":
            # 日文：姓 + 名（一般同中文）
            return f"{self.family_name} {self.given_name}"

        elif self.culture == "western":
            # 西方：名 + 中间名 + 姓
            parts = [self.given_name]

            if self.middle_name:
                parts.append(self.middle_name)

            parts.append(self.family_name)

            full = " ".join(parts)

            if self.prefix:
                full = f"{self.prefix} {full}"

            if self.suffix:
                full = f"{full}, {self.suffix}"

            return full

        # fallback
        return f"{self.given_name} {self.family_name}"

    def get_short_name(self) -> str:
        """
        简称（用于UI）
        """
        return self.given_name

    def get_initials(self) -> str:
        """
        获取首字母缩写
        """
        initials = []

        if self.given_name:
            initials.append(self.given_name[0].upper())

        if self.middle_name:
            initials.append(self.middle_name[0].upper())

        if self.family_name:
            initials.append(self.family_name[0].upper())

        return "".join(initials)

    def add_former_name(self, name: str):
        if name and name not in self.former_names:
            self.former_names.append(name)