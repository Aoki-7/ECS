#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石属性组件：从注册表获取特定矿石的属性
"""
from dataclasses import dataclass
from core.component import Component
from resource.ore.ore_registry import ore_registry, OreConfig

@dataclass(slots=True)
class OrePropertyComponent(Component):
    """矿石属性组件，存储特定矿石的属性，从注册表动态获取"""
    ore_type_id: str = "stone_ore"

    @property
    def config(self) -> OreConfig:
        """获取矿石配置"""
        config = ore_registry.get_ore_config(self.ore_type_id)
        if config is None:
            # 默认返回石矿配置
            return ore_registry.get_ore_config("stone_ore")
        return config

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str:
        return self.config.description

    @property
    def purity(self) -> float:
        return self.config.base_purity

    @property
    def smelting_yield(self) -> float:
        return self.config.smelting_yield

    @property
    def required_mining_tech(self) -> str:
        return self.config.required_mining_tech

    @property
    def required_smelting_tech(self) -> str:
        return self.config.required_smelting_tech

    @property
    def output_metal_type(self) -> str:
        return self.config.output_metal_type
