#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具组件，存储工具的属性和状态
"""
from dataclasses import dataclass
from core.component import Component
from .tool_type import ToolType, ToolMaterial, ToolQuality

@dataclass(slots=True)
class ToolComponent(Component):
    """工具组件"""
    tool_type: ToolType = ToolType.AXE
    material: ToolMaterial = ToolMaterial.STONE
    quality: ToolQuality = ToolQuality.NORMAL

    # 耐久度
    max_durability: float = 100.0
    durability: float = 100.0

    # 加成属性
    efficiency_bonus: float = 1.0  # 效率加成系数
    damage_bonus: float = 0.0      # 战斗伤害加成

    def __post_init__(self):
        """初始化时根据材质和品质计算属性"""
        # 基础耐久度
        base_durability = {
            ToolMaterial.STONE: 100,
            ToolMaterial.BRONZE: 200,
            ToolMaterial.IRON: 300,
            ToolMaterial.STEEL: 500,
        }[self.material]

        # 品质加成
        quality_multiplier = {
            ToolQuality.ROUGH: 0.8,
            ToolQuality.NORMAL: 1.0,
            ToolQuality.FINE: 1.5,
            ToolQuality.MASTER: 2.0,
        }[self.quality]

        # 材质效率加成
        material_bonus = {
            ToolMaterial.STONE: 1.0,
            ToolMaterial.BRONZE: 1.2,
            ToolMaterial.IRON: 1.4,
            ToolMaterial.STEEL: 1.6,
        }[self.material]

        # 工具类型基础效率
        type_bonus = {
            ToolType.AXE: 1.5,
            ToolType.PICKAXE: 1.5,
            ToolType.SICKLE: 1.3,
            ToolType.FISHING_ROD: 1.4,
            ToolType.WEAPON: 0.0,
            ToolType.BOW: 0.0,
            ToolType.HAMMER: 1.3,
            ToolType.PLOW: 1.6,
            ToolType.TORCH: 1.0,
        }[self.tool_type]

        # 战斗伤害加成
        if self.tool_type == ToolType.WEAPON:
            self.damage_bonus = material_bonus * 0.5
        elif self.tool_type == ToolType.BOW:
            self.damage_bonus = material_bonus * 0.4

        self.max_durability = base_durability * quality_multiplier
        self.durability = self.max_durability
        self.efficiency_bonus = type_bonus * material_bonus

    def is_broken(self) -> bool:
        """是否已损坏"""
        return self.durability <= 0

    def use(self, durability_cost: float = 1.0):
        """使用工具，消耗耐久度"""
        self.durability = max(0.0, self.durability - durability_cost)
        return not self.is_broken()

    def repair(self, amount: float):
        """修理工具，恢复耐久度"""
        self.durability = min(self.max_durability, self.durability + amount)
