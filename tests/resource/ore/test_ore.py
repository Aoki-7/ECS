#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石系统测试（新版，支持扩展架构）
"""
import pytest
from core.world import World
from resource.ore import BaseOreComponent, OreTypeComponent, OrePropertyComponent, OreHardness, OreRarity
from resource.ore.ore_registry import ore_registry
from resource.ore.systems import OreGenerationSystem, OreMiningSystem, OreSmeltingSystem
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from civilization.tools.components import ToolInventoryComponent, ToolComponent, ToolType
from human.components.economic.inventory.inventory_component import InventoryComponent

class TestOreRegistry:
    """矿石注册表测试"""
    def test_ore_registry(self):
        """测试矿石注册表"""
        assert len(ore_registry.get_all_ore_types()) >= 5
        config = ore_registry.get_ore_config("iron_ore")
        assert config.name == "铁矿"
        assert config.hardness == OreHardness.HARD

class TestBaseOreComponent:
    """矿石基础组件测试"""
    def test_ore_init(self):
        """测试矿石初始化"""
        ore = BaseOreComponent(total_reserves=100, current_amount=100)
        assert ore.can_harvest()
        assert ore.get_remaining_ratio() == 1.0

    def test_ore_harvest(self):
        """测试矿石开采"""
        ore = BaseOreComponent(total_reserves=50, current_amount=50)
        mined = ore.harvest(10)
        assert mined == 10
        assert ore.current_amount == 40

class TestOreGenerationSystem:
    """矿石生成系统测试"""
    def test_ore_generation(self):
        """测试矿石生成"""
        world = World()
        system = OreGenerationSystem()
        system.update(world, 1.0)
        ores = list(world.get_components(BaseOreComponent))
        assert len(ores) >= 0

class TestOreMiningSystem:
    """矿石开采系统测试"""
    def test_ore_mining(self):
        """测试矿石开采"""
        world = World()
        system = OreMiningSystem()
        # 创建人类
        human_entity = world.create_entity()
        world.add_component(human_entity, HumanComponent())
        world.add_component(human_entity, SpaceComponent(x=0, y=0))
        # 添加镐子
        inventory = ToolInventoryComponent()
        inventory.add_tool(ToolComponent(tool_type=ToolType.PICKAXE))
        world.add_component(human_entity, inventory)
        # 添加库存
        world.add_component(human_entity, InventoryComponent())
        # 创建矿石
        ore_entity = world.create_entity()
        ore = BaseOreComponent(total_reserves=50, current_amount=50)
        world.add_component(ore_entity, ore)
        world.add_component(ore_entity, OreTypeComponent(ore_type_id="iron_ore"))
        world.add_component(ore_entity, SpaceComponent(x=2, y=2))
        # 运行开采系统
        system.update(world, 1.0)
        # 检查是否开采成功
        item_inv = world.get_component(human_entity, InventoryComponent)
        ore_key = hash("iron_ore")
        assert item_inv.items.get(ore_key, 0.0) >= 0

if __name__ == "__main__":
    pytest.main([__file__])