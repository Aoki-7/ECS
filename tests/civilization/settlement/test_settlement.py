#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定居点系统测试
"""
import pytest
from core.world import World
from civilization.settlement import SettlementComponent, SettlementType, BuildingType
from civilization.settlement.systems import SettlementSystem
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from civilization.tools.components import ToolInventoryComponent, ToolComponent, ToolType

class TestSettlementComponent:
    """定居点组件测试"""
    def test_settlement_init(self):
        """测试定居点初始化"""
        settlement = SettlementComponent(name="Test Village")
        assert settlement.settlement_type == SettlementType.CAMP
        assert settlement.get_population() == 0

    def test_add_resident(self):
        """测试添加居民"""
        settlement = SettlementComponent()
        settlement.add_resident(1)
        assert settlement.get_population() == 1
        # 添加10个人口，变成村庄
        for i in range(2, 12):
            settlement.add_resident(i)
        assert settlement.settlement_type == SettlementType.VILLAGE

class TestSettlementSystem:
    """定居点系统测试"""
    def test_create_settlement(self):
        """测试创建定居点"""
        world = World()
        system = SettlementSystem()
        # 创建5个人类，其中一个人有斧头
        for i in range(5):
            entity = world.create_entity()
            world.add_component(entity, HumanComponent())
            world.add_component(entity, SpaceComponent(x=i, y=i))
            inventory = ToolInventoryComponent()
            if i == 0:
                inventory.add_tool(ToolComponent(tool_type=ToolType.AXE))
            world.add_component(entity, inventory)
        # 运行系统
        system.update(world, 1.0)
        # 应该创建了一个定居点
        settlements = list(world.get_components(SettlementComponent))
        assert len(settlements) == 1
        settlement = settlements[0][1][0]
        assert settlement.get_population() == 5

if __name__ == "__main__":
    pytest.main([__file__])