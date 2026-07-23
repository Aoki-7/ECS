#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石开采系统：人类可以用镐开采矿石（新版，支持扩展）
"""
import logging
from core.system import System
from core.world import World
from resource.ore.components.base_ore_component import BaseOreComponent
from resource.ore.components.ore_type_component import OreTypeComponent
from resource.ore.components.ore_property_component import OrePropertyComponent
from civilization.tools.components.tool_inventory_component import ToolInventoryComponent
from civilization.tools.components.tool_type import ToolType
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from human.components.economic.inventory.inventory_component import InventoryComponent

logger = logging.getLogger(__name__)

class OreMiningSystem(System):
    """矿石开采系统"""
    tick_interval = 10  # 每10帧检查一次开采

    def update(self, world: World, dt: float) -> None:
        """更新矿石开采"""
        # 获取所有人类
        humans = world.get_components(HumanComponent, SpaceComponent, ToolInventoryComponent, InventoryComponent)
        # 获取所有矿石
        ores = list(world.get_components(BaseOreComponent, OreTypeComponent, SpaceComponent))

        for human_entity, (human, human_pos, tool_inv, item_inv) in humans:
            # 检查是否有镐子
            if not tool_inv.has_tool(ToolType.PICKAXE):
                continue

            # 查找附近的矿石（范围5单位）
            nearby_ores = []
            for ore_entity, (ore, ore_type, ore_pos) in ores:
                distance = ((human_pos.x - ore_pos.x)**2 + (human_pos.y - ore_pos.y)**2)**0.5
                if distance <= 5.0 and ore.can_harvest():
                    nearby_ores.append((ore_entity, ore, ore_type, distance))

            if not nearby_ores:
                continue

            # 选择最近的矿石开采
            nearby_ores.sort(key=lambda x: x[3])
            ore_entity, ore, ore_type, distance = nearby_ores[0]

            # 获取镐子效率加成
            pickaxe = tool_inv.get_tool(ToolType.PICKAXE)
            efficiency = pickaxe.efficiency_bonus if pickaxe else 1.0

            # 计算开采量
            harvest_amount = ore.base_harvest_rate * efficiency
            mined_amount = ore.harvest(harvest_amount)

            if mined_amount > 0:
                # 将矿石加入库存
                ore_key = hash(ore_type.ore_type_id)
                current_amount = item_inv.items.get(ore_key, 0.0)
                item_inv.items[ore_key] = current_amount + mined_amount
                logger.debug(f"[OreMining] 实体{human_entity.id} 开采了 {mined_amount:.1f} 单位 {ore_type.ore_type_id}")