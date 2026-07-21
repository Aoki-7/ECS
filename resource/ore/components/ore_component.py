#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石组件：可开采的矿石资源
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict
from resource.components.base_resource_component import BaseResourceComponent

class OreType(Enum):
    """矿石类型"""
    IRON_ORE = "iron_ore"        # 铁矿：最常见，用于制作铁器
    COPPER_ORE = "copper_ore"    # 铜矿：用于制作青铜
    GOLD_ORE = "gold_ore"        # 金矿：稀有，用于贸易和高级工具
    COAL_ORE = "coal_ore"        # 煤矿：燃料，用于冶炼
    STONE_ORE = "stone_ore"      # 石矿：基础建筑材料

class OreQuality(Enum):
    """矿石品质"""
    POOR = "poor"        # 贫瘠：纯度30%~50%
    NORMAL = "normal"    # 普通：纯度50%~70%
    RICH = "rich"        # 富矿：纯度70%~90%
    EXCEPTIONAL = "exceptional"  # 极品：纯度90%~100%

@dataclass(slots=True)
class OreComponent(BaseResourceComponent):
    """
    矿石组件（可被开采的资源）

    ===== 核心设计 =====
    - 支持多次开采，有总储量限制
    - 需要对应工具（镐）开采
    - 不同矿石需要不同科技解锁
    - 可冶炼成金属，冶炼效率受科技影响
    """

    # ===== 矿石属性 =====
    ore_type: OreType = OreType.IRON_ORE
    ore_quality: OreQuality = OreQuality.NORMAL
    purity: float = 0.6  # 纯度（0~1）

    # ===== 储量 =====
    total_reserves: float = 100.0   # 总储量
    current_amount: float = 100.0   # 当前剩余量
    harvest_size: float = 2.0       # 每次开采量（受工具影响）

    # ===== 开采难度 =====
    hardness: float = 1.0           # 硬度（1~5，越高越难开采）
    required_tech: str = "metal_tools"  # 开采所需科技

    # ===== 冶炼属性 =====
    smelting_yield: float = 0.7     # 冶炼产出率（1单位矿石产出0.7单位金属）
    smelting_required_tech: str = "bronze_smelting"  # 冶炼所需科技

    # ===== 分布属性 =====
    depth: float = 1.0              # 埋藏深度（影响开采难度和发现概率）

    def __post_init__(self):
        """初始化时根据品质调整纯度和储量"""
        # 父类初始化
        self.amount = max(0.0, min(self.amount, self.max_amount))
        self.quality = max(0.0, min(self.quality, 1.0))

        purity_map = {
            OreQuality.POOR: 0.3,
            OreQuality.NORMAL: 0.6,
            OreQuality.RICH: 0.8,
            OreQuality.EXCEPTIONAL: 0.95,
        }
        self.purity = purity_map[self.ore_quality]

        # 富矿储量更高
        reserve_multiplier = {
            OreQuality.POOR: 0.7,
            OreQuality.NORMAL: 1.0,
            OreQuality.RICH: 1.5,
            OreQuality.EXCEPTIONAL: 2.0,
        }[self.ore_quality]
        self.total_reserves *= reserve_multiplier
        self.current_amount = self.total_reserves

    def can_harvest(self) -> bool:
        """是否可开采"""
        return self.current_amount > 0.1

    def harvest(self, amount: float = None) -> float:
        """开采矿石，返回实际开采量"""
        if not self.can_harvest():
            return 0.0
        harvest_amount = amount if amount is not None else self.harvest_size
        actual = min(harvest_amount, self.current_amount)
        self.current_amount -= actual
        return actual

    def get_smelted_metal_amount(self) -> float:
        """计算可冶炼出的金属量"""
        return self.current_amount * self.purity * self.smelting_yield
