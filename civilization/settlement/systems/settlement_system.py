#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定居点系统：管理村庄/城镇的创建、人口、建筑
"""
import logging
from core.system import System
from core.world import World
from civilization.settlement.components.settlement_component import SettlementComponent, SettlementType, BuildingType
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent
from civilization.tools.components.tool_inventory_component import ToolInventoryComponent
from civilization.tools.components.tool_type import ToolType

logger = logging.getLogger(__name__)

class SettlementSystem(System):
    """定居点系统"""
    tick_interval = 20  # 每20帧更新一次

    def update(self, world: World, dt: float) -> None:
        """更新定居点系统"""
        # 检查是否有足够的人口形成新的定居点
        self._check_new_settlement(world)
        # 更新现有定居点
        self._update_existing_settlements(world, dt)

    def _check_new_settlement(self, world: World):
        """检查是否满足条件创建新的定居点"""
        # 当有10个人类聚集在一定范围内，且有工具时，自动创建定居点
        humans = world.get_components(HumanComponent, SpaceComponent, ToolInventoryComponent)
        # 简化逻辑：如果人口>=5且有斧头工具，就创建一个定居点
        human_list = list(humans)
        logger.info(f"[SettlementSystem] 发现 {len(human_list)} 个人类")
        if len(human_list) >= 5:
            # 检查是否有工具
            has_tool = any(inv.has_tool(ToolType.AXE) for _, (_, _, inv) in human_list)
            if has_tool and len(list(world.get_components(SettlementComponent))) == 0:
                # 创建第一个定居点
                # 取第一个人类的位置作为中心
                first_entity, (_, pos, _) = human_list[0]
                settlement = SettlementComponent(
                    name="First Village",
                    center_x=pos.x,
                    center_y=pos.y,
                    radius=20.0,
                )
                # 将所有附近人类加入定居点
                for entity, (_, pos, _) in human_list:
                    settlement.add_resident(entity.id)
                # 创建定居点实体
                settlement_entity = world.create_entity()
                world.add_component(settlement_entity, settlement)
                logger.info(f"[SettlementSystem] 创建定居点: {settlement.name}, 人口: {settlement.get_population()}")

    def _update_existing_settlements(self, world: World, dt: float):
        """更新现有定居点"""
        for settlement_entity, (settlement,) in world.get_components(SettlementComponent):
            # 清理死亡/不存在的居民
            # 简化：暂不清理死亡居民，后续实现
            settlement._update_type()

            # 人口>=10时自动添加房屋建筑
            if settlement.get_population() >= 10 and not any(b["type"] == BuildingType.HOUSE for b in settlement.buildings):
                settlement.add_building(BuildingType.HOUSE, settlement.center_x, settlement.center_y)
                logger.info(f"[SettlementSystem] 定居点 {settlement.name} 建造了第一栋房屋")

            # 人口>=20时自动添加仓库
            if settlement.get_population() >= 20 and not any(b["type"] == BuildingType.STORAGE for b in settlement.buildings):
                settlement.add_building(BuildingType.STORAGE, settlement.center_x + 5, settlement.center_y + 5)
                logger.info(f"[SettlementSystem] 定居点 {settlement.name} 建造了仓库")