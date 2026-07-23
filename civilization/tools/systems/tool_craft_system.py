#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具制作系统：根据已解锁的科技制作工具
"""
import logging
from core.system import System
from core.world import World
from civilization.tools.components.tool_component import ToolComponent
from civilization.tools.components.tool_inventory_component import ToolInventoryComponent
from civilization.tools.components.tool_type import ToolType, ToolMaterial, ToolQuality
from human.components.abilities.skill_component import SkillComponent

logger = logging.getLogger(__name__)

class ToolCraftSystem(System):
    """工具制作系统"""
    tick_interval = 50  # 每50帧检查一次

    # 工具解锁条件：工具类型 -> (所需科技, 所需资源, 所需技能等级)
    TOOL_UNLOCKS = {
        ToolType.AXE: {
            "required_tech": "basic_farming",
            "required_resources": {"wood": 5, "stone": 3},
            "required_skill": 1,
        },
        ToolType.PICKAXE: {
            "required_tech": "metal_tools",
            "required_resources": {"wood": 3, "metal": 5},
            "required_skill": 2,
        },
        ToolType.SICKLE: {
            "required_tech": "advanced_farming",
            "required_resources": {"wood": 2, "metal": 3},
            "required_skill": 2,
        },
        ToolType.WEAPON: {
            "required_tech": "basic_weaponry",
            "required_resources": {"metal": 10, "wood": 2},
            "required_skill": 3,
        },
        ToolType.HAMMER: {
            "required_tech": "basic_construction",
            "required_resources": {"wood": 4, "metal": 2},
            "required_skill": 2,
        },
        ToolType.PLOW: {
            "required_tech": "advanced_farming",
            "required_resources": {"wood": 6, "metal": 4},
            "required_skill": 3,
        },
    }

    def update(self, world: World, dt: float) -> None:
        """更新工具制作系统"""
        # 获取所有人类
        humans = world.get_components(ToolInventoryComponent)
        tech_system = world.get_system("TechnologySystem")
        if tech_system is None:
            return

        for entity, (inventory,) in humans:
            # 检查每个可解锁的工具
            for tool_type, unlock_info in self.TOOL_UNLOCKS.items():
                # 已经有工具则跳过
                if inventory.has_tool(tool_type):
                    continue

                # 检查科技是否解锁
                if unlock_info["required_tech"] not in tech_system.discovered_technologies:
                    continue

                # 检查技能等级
                skill = world.get_component(entity, SkillComponent)
                if skill is None or skill.level < unlock_info["required_skill"]:
                    continue

                # 检查资源（简化：暂时忽略资源，后续实现资源系统后再添加）
                # 制作工具
                new_tool = self._create_tool(tool_type, tech_system)
                inventory.add_tool(new_tool)
                logger.info(f"[ToolCraft] 实体{entity.id} 制作了 {tool_type.value} ({new_tool.material.value})")

    def _create_tool(self, tool_type: ToolType, tech_system) -> ToolComponent:
        """根据科技水平创建对应材质的工具"""
        # 根据科技选择材质
        if "steelmaking" in tech_system.discovered_technologies:
            material = ToolMaterial.STEEL
        elif "iron_smelting" in tech_system.discovered_technologies:
            material = ToolMaterial.IRON
        elif "bronze_smelting" in tech_system.discovered_technologies:
            material = ToolMaterial.BRONZE
        else:
            material = ToolMaterial.STONE

        return ToolComponent(tool_type=tool_type, material=material, quality=ToolQuality.NORMAL)