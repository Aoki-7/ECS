#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具使用系统：为采集/战斗/建造等活动提供工具加成
"""
import logging
from core.system import System
from core.world import World
from civilization.tools.components.tool_inventory_component import ToolInventoryComponent
from civilization.tools.components.tool_type import ToolType

logger = logging.getLogger(__name__)

class ToolUsageSystem(System):
    """工具使用系统"""
    tick_interval = 10  # 每10帧更新一次

    # 活动类型对应工具类型
    ACTIVITY_TOOL_MAP = {
        "chop_wood": ToolType.AXE,
        "mine_stone": ToolType.PICKAXE,
        "mine_metal": ToolType.PICKAXE,
        "harvest_crop": ToolType.SICKLE,
        "fight": ToolType.WEAPON,
        "build": ToolType.HAMMER,
        "farm": ToolType.PLOW,
    }

    def update(self, world: World, dt: float) -> None:
        """更新工具使用系统"""
        # 为所有有工具的人类应用加成
        for entity, (inventory,) in world.get_components(ToolInventoryComponent):
            active_tool = inventory.get_active_tool()
            if active_tool is None:
                continue

            # 应用加成（简化：直接将加成存入世界临时数据，各业务系统查询使用）
            # 实际使用中，各采集/战斗系统会查询这个加成
            world.set_entity_metadata(entity, "tool_bonus", active_tool.efficiency_bonus)
            world.set_entity_metadata(entity, "tool_damage_bonus", active_tool.damage_bonus)

            # 工具缓慢损耗
            if world.tick_count % 100 == 0:
                active_tool.use(0.1)  # 每100帧消耗0.1耐久
                if active_tool.is_broken():
                    inventory.remove_broken_tools()
                    logger.debug(f"[ToolUsage] 实体{entity.id} 的 {active_tool.tool_type.value} 已损坏")