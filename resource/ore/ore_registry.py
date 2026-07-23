#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石注册表：管理所有矿石类型的配置，支持零代码扩展新矿石
"""
from dataclasses import dataclass
from typing import Dict, Optional
from resource.ore.components.base_ore_component import OreHardness, OreRarity

@dataclass
class OreConfig:
    """矿石配置"""
    name: str                     # 矿石名称
    description: str              # 描述
    hardness: OreHardness         # 硬度
    rarity: OreRarity             # 稀有度
    base_purity: float            # 基础纯度
    smelting_yield: float         # 冶炼产出率
    required_mining_tech: str     # 开采所需科技
    required_smelting_tech: str   # 冶炼所需科技
    output_metal_type: str        # 冶炼产物类型
    base_reserve: float           # 基础储量
    generation_probability: float # 生成概率
    preferred_terrain: list       # 偏好地形
    depth_range: tuple            # 深度范围

class OreRegistry:
    """矿石注册表单例"""
    _instance = None
    _ore_configs: Dict[str, OreConfig] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_default_ores()
        return cls._instance

    def _init_default_ores(self):
        """初始化默认矿石类型"""
        # 石矿
        self.register_ore("stone_ore", OreConfig(
            name="石矿",
            description="最常见的矿石，用于建筑和工具",
            hardness=OreHardness.SOFT,
            rarity=OreRarity.COMMON,
            base_purity=0.9,
            smelting_yield=1.0,
            required_mining_tech="basic_farming",
            required_smelting_tech="basic_construction",
            output_metal_type="stone",
            base_reserve=500.0,
            generation_probability=0.5,
            preferred_terrain=["plain", "hill", "mountain"],
            depth_range=(0.5, 1.5),
        ))
        # 煤矿
        self.register_ore("coal_ore", OreConfig(
            name="煤矿",
            description="燃料矿石，用于冶炼和取暖",
            hardness=OreHardness.SOFT,
            rarity=OreRarity.COMMON,
            base_purity=0.8,
            smelting_yield=0.9,
            required_mining_tech="basic_farming",
            required_smelting_tech="bronze_smelting",
            output_metal_type="coal",
            base_reserve=300.0,
            generation_probability=0.3,
            preferred_terrain=["hill", "mountain"],
            depth_range=(1.0, 2.0),
        ))
        # 铜矿
        self.register_ore("copper_ore", OreConfig(
            name="铜矿",
            description="用于制作青铜的矿石",
            hardness=OreHardness.MEDIUM,
            rarity=OreRarity.UNCOMMON,
            base_purity=0.7,
            smelting_yield=0.8,
            required_mining_tech="metal_tools",
            required_smelting_tech="bronze_smelting",
            output_metal_type="copper",
            base_reserve=150.0,
            generation_probability=0.25,
            preferred_terrain=["hill", "plain"],
            depth_range=(1.0, 2.0),
        ))
        # 铁矿
        self.register_ore("iron_ore", OreConfig(
            name="铁矿",
            description="用于制作铁器的矿石",
            hardness=OreHardness.HARD,
            rarity=OreRarity.UNCOMMON,
            base_purity=0.6,
            smelting_yield=0.7,
            required_mining_tech="metal_tools",
            required_smelting_tech="iron_smelting",
            output_metal_type="iron",
            base_reserve=200.0,
            generation_probability=0.4,
            preferred_terrain=["mountain", "hill"],
            depth_range=(1.0, 3.0),
        ))
        # 金矿
        self.register_ore("gold_ore", OreConfig(
            name="金矿",
            description="稀有的贵金属矿石",
            hardness=OreHardness.MEDIUM,
            rarity=OreRarity.RARE,
            base_purity=0.5,
            smelting_yield=0.9,
            required_mining_tech="metal_tools",
            required_smelting_tech="bronze_smelting",
            output_metal_type="gold",
            base_reserve=50.0,
            generation_probability=0.1,
            preferred_terrain=["mountain"],
            depth_range=(2.0, 5.0),
        ))

    def register_ore(self, ore_type_id: str, config: OreConfig):
        """注册新的矿石类型"""
        self._ore_configs[ore_type_id] = config

    def get_ore_config(self, ore_type_id: str) -> Optional[OreConfig]:
        """获取矿石配置"""
        return self._ore_configs.get(ore_type_id)

    def get_all_ore_types(self) -> list:
        """获取所有矿石类型ID"""
        return list(self._ore_configs.keys())

# 全局矿石注册表单例
ore_registry = OreRegistry()