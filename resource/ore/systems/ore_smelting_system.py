#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矿石冶炼系统：将矿石冶炼成金属（新版，支持扩展）
"""
import logging
from core.system import System
from core.world import World
from resource.ore.components.ore_property_component import OrePropertyComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.basic.human_component import HumanComponent
from civilization.systems.technology_system import TechnologySystem

logger = logging.getLogger(__name__)

class OreSmeltingSystem(System):
    """矿石冶炼系统"""
    tick_interval = 20  # 每20帧检查一次冶炼

    def update(self, world: World, dt: float) -> None:
        """更新矿石冶炼"""
        tech_system = world.get_system("TechnologySystem")
        if tech_system is None:
            return

        # 获取所有有库存的人类
        humans = world.get_components(HumanComponent, InventoryComponent)
        # 获取所有矿石属性组件，用于查询冶炼信息
        ore_props = {e.id: prop for e, (prop,) in world.get_components(OrePropertyComponent)}

        for human_entity, (human, inventory) in humans:
            # 遍历库存中的所有矿石
            for item_key, amount in list(inventory.items.items()):
                if amount <= 0:
                    continue
                # 查找对应的矿石类型
                # 这里简化处理：遍历所有矿石类型，匹配hash
                for ore_type_id, prop in ore_props.items():
                    if hash(ore_type_id) == item_key:
                        # 检查科技是否解锁
                        if prop.required_smelting_tech not in tech_system.discovered_technologies:
                            break

                        # 冶炼10单位矿石
                        smelt_amount = min(10.0, amount)
                        if smelt_amount <= 0:
                            break

                        # 计算产出金属量
                        output_amount = smelt_amount * prop.purity * prop.smelting_yield
                        metal_key = hash(prop.output_metal_type)

                        # 扣除矿石，添加金属
                        inventory.items[item_key] = amount - smelt_amount
                        current_metal = inventory.items.get(metal_key, 0.0)
                        inventory.items[metal_key] = current_metal + output_amount
                        logger.info(f"[OreSmelting] 实体{human_entity.id} 冶炼了 {smelt_amount:.1f} 单位 {prop.name}，产出 {output_amount:.1f} 单位 {prop.output_metal_type}")
                        break
