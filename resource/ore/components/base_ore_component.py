#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石基础组件：所有矿石通用的核心属性
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
from resource.components.base_resource_component import BaseResourceComponent

class OreHardness(Enum):
    """矿石硬度等级"""
    VERY_SOFT = 1    # 极软：用手即可开采
    SOFT = 2         # 软：石镐可开采
    MEDIUM = 3       # 中等：青铜镐可开采
    HARD = 4         # 硬：铁镐可开采
    VERY_HARD = 5    # 极硬：钢镐可开采

class OreRarity(Enum):
    """矿石稀有度"""
    COMMON = "common"        # 常见：石矿/煤矿
    UNCOMMON = "uncommon"    # 少见：铜矿/铁矿
    RARE = "rare"            # 稀有：金矿/银矿
    EPIC = "epic"            # 史诗：钻石/翡翠
    LEGENDARY = "legendary"  # 传说：特殊矿石

@dataclass(slots=True)
class BaseOreComponent(BaseResourceComponent):
    """
    矿石基础组件：所有矿石通用的核心属性
    不包含特定矿石的属性，仅包含通用的储量、开采、位置等属性
    """

    # ===== 通用储量属性 =====
    total_reserves: float = 100.0      # 总储量
    current_amount: float = 100.0      # 当前剩余量
    base_harvest_rate: float = 2.0     # 基础开采速度（单位/次）

    # ===== 通用开采属性 =====
    hardness: OreHardness = OreHardness.MEDIUM  # 硬度
    rarity: OreRarity = OreRarity.COMMON        # 稀有度
    depth: float = 1.0               # 埋藏深度（0~10，越深越难发现/开采）
    discovery_difficulty: float = 1.0  # 发现难度（0~1，越高越难发现）

    # ===== 通用状态 =====
    is_discovered: bool = False      # 是否已被发现
    is_depleted: bool = False        # 是否已耗尽
    depletion_time: float = 0.0      # 耗尽时间

    def can_harvest(self) -> bool:
        """是否可开采"""
        return not self.is_depleted and self.current_amount > 0.1

    def harvest(self, amount: float = None) -> float:
        """开采矿石，返回实际开采量"""
        if not self.can_harvest():
            return 0.0
        harvest_amount = amount if amount is not None else self.base_harvest_rate
        actual = min(harvest_amount, self.current_amount)
        self.current_amount -= actual
        # 检查是否耗尽
        if self.current_amount <= 0.1:
            self.is_depleted = True
        return actual

    def get_remaining_ratio(self) -> float:
        """获取剩余储量比例"""
        if self.total_reserves <= 0:
            return 0.0
        return self.current_amount / self.total_reserves