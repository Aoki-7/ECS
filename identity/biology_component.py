#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@文件:biology_component.py
@说明:生物属性组件（V2）
@时间:2026/03/19 13:21:44
@作者:Sherry
@版本:2.0

优化内容：
1. 增强类型安全（Literal / Final）
2. 增加生命周期阶段判断
3. 增加年龄合法性校验
4. 增加生理状态支持
5. 增加死亡状态支持
6. 增加物种分类扩展能力
7. 使用 slots 降低 ECS 内存占用
8. 增加序列化支持
9. 增强可维护性与扩展性
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Final

from core.component import Component


# =========================================================
# 类型定义
# =========================================================

SpeciesType = Literal[
    "Human",
    "Animal",
    "Monster",
    "Robot",
    "Unknown",
]

GenderType = Literal[
    "Male",
    "Female",
    "Other",
    "Unknown",
]

LifeStageType = Literal[
    "Embryo",
    "Infant",
    "Child",
    "Teen",
    "Adult",
    "MiddleAged",
    "Elderly",
]

HealthStateType = Literal[
    "Healthy",
    "Injured",
    "Sick",
    "Critical",
    "Dead",
]


# =========================================================
# 生命周期阈值
# （默认以 Human 为基准）
# =========================================================

INFANT_MAX_AGE: Final[float] = 3
CHILD_MAX_AGE: Final[float] = 12
TEEN_MAX_AGE: Final[float] = 18
ADULT_MAX_AGE: Final[float] = 45
MIDDLE_MAX_AGE: Final[float] = 65


# =========================================================
# 生物组件
# =========================================================

@dataclass(slots=True)
class BiologyComponent(Component):
    """
    生物属性组件

    用于描述：
    - 生物学身份
    - 生命周期
    - 性别属性
    - 年龄成长
    - 生理状态
    - 死亡状态

    适用于：
    - 人类
    - 动物
    - 怪物
    - NPC
    - 可扩展生命体
    """

    # =====================================================
    # 基础生物属性
    # =====================================================

    species: SpeciesType = "Human"

    gender: GenderType = "Unknown"

    age: float = 0.0

    # =====================================================
    # 生理状态
    # =====================================================

    health_state: HealthStateType = "Healthy"

    is_alive: bool = True

    fertility: float = 1.0
    """
    生育能力（0~1）
    """

    body_temperature: float = 36.5
    """
    默认体温（摄氏度）
    """

    # =====================================================
    # 生命周期
    # =====================================================

    def __post_init__(self) -> None:
        """
        初始化校验
        """

        if self.age < 0:
            raise ValueError(
                f"age cannot be negative: {self.age}"
            )

        self.fertility = max(0.0, min(1.0, self.fertility))

        if self.health_state == "Dead":
            self.is_alive = False

    # =====================================================
    # 生命周期阶段
    # =====================================================

    @property
    def life_stage(self) -> LifeStageType:
        """
        获取生命周期阶段
        """

        age = self.age

        if age < 0:
            return "Embryo"

        if age <= INFANT_MAX_AGE:
            return "Infant"

        if age <= CHILD_MAX_AGE:
            return "Child"

        if age <= TEEN_MAX_AGE:
            return "Teen"

        if age <= ADULT_MAX_AGE:
            return "Adult"

        if age <= MIDDLE_MAX_AGE:
            return "MiddleAged"

        return "Elderly"

    # =====================================================
    # 生命状态
    # =====================================================

    def kill(self) -> None:
        """
        设置死亡
        """

        self.is_alive = False
        self.health_state = "Dead"

    def revive(self) -> None:
        """
        复活
        """

        self.is_alive = True

        if self.health_state == "Dead":
            self.health_state = "Critical"

    # =====================================================
    # 年龄成长
    # =====================================================

    def grow(self, years: float) -> None:
        """
        年龄增长
        """

        if years < 0:
            raise ValueError(
                "grow years cannot be negative"
            )

        self.age += years

    # =====================================================
    # 状态判断
    # =====================================================

    @property
    def is_child(self) -> bool:
        return self.life_stage in ("Infant", "Child")

    @property
    def is_adult(self) -> bool:
        return self.life_stage in (
            "Adult",
            "MiddleAged",
        )

    @property
    def is_elderly(self) -> bool:
        return self.life_stage == "Elderly"

    # =====================================================
    # 序列化
    # =====================================================

    def to_dict(self) -> dict:
        """
        转为字典
        """

        return {
            "species": self.species,
            "gender": self.gender,
            "age": self.age,
            "life_stage": self.life_stage,
            "health_state": self.health_state,
            "is_alive": self.is_alive,
            "fertility": self.fertility,
            "body_temperature": self.body_temperature,
        }

    # =====================================================
    # Debug
    # =====================================================

    def __str__(self) -> str:
        return (
            f"{self.species}("
            f"age={self.age:.1f}, "
            f"stage={self.life_stage}"
            f")"
        )

    def __repr__(self) -> str:
        return (
            f"BiologyComponent("
            f"species='{self.species}', "
            f"gender='{self.gender}', "
            f"age={self.age:.1f}, "
            f"alive={self.is_alive}"
            f")"
        )