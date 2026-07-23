#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具系统测试
"""
import pytest
from core.world import World
from civilization.tools import ToolComponent, ToolInventoryComponent, ToolType, ToolMaterial, ToolQuality
from civilization.tools.systems import ToolCraftSystem, ToolUsageSystem
from human.components.basic.human_component import HumanComponent

class TestToolComponent:
    """工具组件测试"""
    def test_tool_init(self):
        """测试工具初始化"""
        tool = ToolComponent(tool_type=ToolType.AXE, material=ToolMaterial.STONE)
        assert tool.max_durability == 100
        assert tool.efficiency_bonus == 1.5

    def test_tool_use(self):
        """测试工具使用"""
        tool = ToolComponent(tool_type=ToolType.AXE, material=ToolMaterial.STONE)
        assert tool.use(10) == True
        assert tool.durability == 90
        assert tool.use(100) == False
        assert tool.is_broken() == True

class TestToolInventory:
    """工具背包测试"""
    def test_add_tool(self):
        """测试添加工具"""
        inventory = ToolInventoryComponent()
        tool = ToolComponent(tool_type=ToolType.AXE)
        inventory.add_tool(tool)
        assert inventory.has_tool(ToolType.AXE)
        assert inventory.get_active_tool() == tool

class TestToolCraftSystem:
    """工具制作系统测试"""
    def test_craft_system(self):
        """测试工具制作"""
        world = World()
        craft_system = ToolCraftSystem()
        # 创建人类实体
        entity = world.create_entity()
        world.add_component(entity, HumanComponent())
        world.add_component(entity, ToolInventoryComponent())
        # 运行系统
        craft_system.update(world, 1.0)
        # 没有解锁科技，不应该制作工具
        inventory = world.get_component(entity, ToolInventoryComponent)
        assert not inventory.has_tool(ToolType.AXE)

if __name__ == "__main__":
    pytest.main([__file__])