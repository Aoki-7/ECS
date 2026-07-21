#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石扩展示例：零代码添加新的矿石类型
"""
import pytest
from resource.ore.ore_registry import ore_registry, OreConfig
from resource.ore.components.base_ore_component import OreHardness, OreRarity

class TestOreExtension:
    """测试零代码扩展新矿石"""
    def test_add_diamond_ore(self):
        """测试添加钻石矿"""
        # 零代码添加新的矿石类型：钻石矿
        ore_registry.register_ore("diamond_ore", OreConfig(
            name="钻石矿",
            description="极其稀有的宝石矿石",
            hardness=OreHardness.VERY_HARD,
            rarity=OreRarity.EPIC,
            base_purity=0.4,
            smelting_yield=0.95,
            required_mining_tech="steelmaking",
            required_smelting_tech="steelmaking",
            output_metal_type="diamond",
            base_reserve=20.0,
            generation_probability=0.05,
            preferred_terrain=["mountain"],
            depth_range=(3.0, 5.0),
        ))
        # 验证新矿石已注册
        config = ore_registry.get_ore_config("diamond_ore")
        assert config.name == "钻石矿"
        assert config.rarity == OreRarity.EPIC
        assert "diamond_ore" in ore_registry.get_all_ore_types()

if __name__ == "__main__":
    pytest.main([__file__])
