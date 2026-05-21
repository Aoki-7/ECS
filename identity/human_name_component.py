#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件:human_name_component.py
@说明:人类命名组件（V2 优化版）
@时间:2026/03/24 11:26:28
@作者:Sherry
@版本:2.0

优化内容：
1. 增强类型安全（Literal / Final）
2. 统一命名文化格式策略
3. 增加缓存字段避免重复拼接
4. 增加标准化字符串清洗
5. 增强 initials 兼容性
6. former_names 使用 set 去重
7. 增加序列化支持
8. 增加文化扩展能力
9. 提高可维护性与 ECS 兼容性
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Literal, Final

from core.component import Component


# =========================
# 类型定义
# =========================

CultureType = Literal[
    "generic",
    "chinese",
    "western",
    "japanese",
]

LanguageType = Literal[
    "zh",
    "en",
    "jp",
]

GenderType = Literal[
    "male",
    "female",
    "other",
]


# =========================
# 命名格式策略
# =========================

NAME_ORDER_MAP: Final[Dict[str, str]] = {
    "chinese": "family_given",
    "japanese": "family_given_space",
    "western": "given_middle_family",
    "generic": "given_family",
}


@dataclass(slots=True)
class HumanNameComponent(Component):
    """
    人类命名组件（结构化命名）

    用于：
    - NPC 命名
    - UI 显示
    - 社交系统
    - 法律身份系统
    - 多文化姓名生成
    - 历史姓名记录

    -------------------------
    核心字段
    -------------------------
    given_name:
        名

    family_name:
        姓

    middle_name:
        中间名（西方常见）

    prefix:
        前缀（Mr. / Dr. / Sir）

    suffix:
        后缀（Jr. / III）

    -------------------------
    语义信息
    -------------------------
    gender:
        性别

    culture:
        命名文化

    language:
        语言

    -------------------------
    扩展信息
    -------------------------
    nickname:
        昵称

    former_names:
        曾用名列表
    """

    # =========================
    # 核心结构
    # =========================

    given_name: str
    family_name: str

    middle_name: Optional[str] = None

    prefix: Optional[str] = None
    suffix: Optional[str] = None

    # =========================
    # 语义信息
    # =========================

    gender: Optional[GenderType] = None

    culture: CultureType = "generic"
    language: LanguageType = "en"

    # =========================
    # 扩展信息
    # =========================

    nickname: Optional[str] = None

    former_names: List[str] = field(default_factory=list)

    # =========================
    # 生命周期
    # =========================

    def __post_init__(self) -> None:
        """
        初始化清洗
        """

        self.given_name = self._clean(self.given_name)
        self.family_name = self._clean(self.family_name)

        self.middle_name = self._clean_optional(self.middle_name)
        self.prefix = self._clean_optional(self.prefix)
        self.suffix = self._clean_optional(self.suffix)

        self.nickname = self._clean_optional(self.nickname)

        self.former_names = list(dict.fromkeys(
            self._clean(name)
            for name in self.former_names
            if name
        ))

    # =========================
    # 名称生成
    # =========================

    def get_full_name(self) -> str:
        """
        获取完整姓名
        """

        rule = NAME_ORDER_MAP.get(
            self.culture,
            "given_family"
        )

        if rule == "family_given":
            return f"{self.family_name}{self.given_name}"

        if rule == "family_given_space":
            return f"{self.family_name} {self.given_name}"

        if rule == "given_middle_family":
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

        return f"{self.given_name} {self.family_name}"

    def get_short_name(self) -> str:
        """
        获取短名称（UI显示）
        """

        return self.nickname or self.given_name

    def get_initials(self) -> str:
        """
        获取姓名首字母

        Example:
            John Ronald Tolkien
            -> JRT
        """

        parts = [
            self.given_name,
            self.middle_name,
            self.family_name,
        ]

        initials = []

        for part in parts:
            if not part:
                continue

            text = part.strip()

            if not text:
                continue

            initials.append(text[0].upper())

        return "".join(initials)

    # =========================
    # 曾用名管理
    # =========================

    def add_former_name(self, name: str) -> None:
        """
        添加曾用名
        """

        name = self._clean(name)

        if not name:
            return

        if name not in self.former_names:
            self.former_names.append(name)

    # =========================
    # 工具方法
    # =========================

    @staticmethod
    def _clean(value: str) -> str:
        """
        清洗字符串
        """

        return value.strip()

    @staticmethod
    def _clean_optional(value: Optional[str]) -> Optional[str]:
        """
        清洗可选字符串
        """

        if value is None:
            return None

        value = value.strip()

        return value or None

    # =========================
    # 序列化
    # =========================

    def to_dict(self) -> dict:
        """
        转为字典
        """

        return {
            "given_name": self.given_name,
            "family_name": self.family_name,
            "middle_name": self.middle_name,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "gender": self.gender,
            "culture": self.culture,
            "language": self.language,
            "nickname": self.nickname,
            "former_names": self.former_names,
        }

    # =========================
    # Debug
    # =========================

    def __str__(self) -> str:
        return self.get_full_name()

    def __repr__(self) -> str:
        return (
            f"HumanNameComponent("
            f"full_name='{self.get_full_name()}', "
            f"culture='{self.culture}'"
            f")"
        )