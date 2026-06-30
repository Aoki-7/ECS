#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作系统（自然演化版）v3.0.2

v3.0.2 拆分：
- 材料扫描与分类 -> MaterialScanner
- 制作结果计算 -> CraftResultCalculator
- 产出物创建 -> ProductCreator
"""

import random
import math
from typing import Dict, List, Optional, Tuple

from core.system import System
from core.world import World

from human.components.abilities.skill_component import SkillComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent
from civilization.systems.crafting_knowledge_system import CraftingKnowledgeSystem
from space.space_component import SpaceComponent

from civilization.systems.material_scanner import MaterialScanner
from civilization.systems.craft_result_calculator import CraftResultCalculator
from civilization.systems.product_creator import ProductCreator

import logging

logger = logging.getLogger(__name__)


class CraftingSystem(System):
    """
    制作系统

    职责：
        - 处理制作行为（ActionType.CRAFT）
        - 根据材料组合和环境计算产出
        - 记录成功/失败到 CraftingKnowledgeComponent
        - 支持技术自然演化（无硬编码配方）
    """

    tick_interval = 2  # 每2帧执行一次（制作行为不需要每帧）

    def __init__(self):
        super().__init__()
        self._scanner = MaterialScanner()
        self._calculator = CraftResultCalculator()
        self._product_creator = ProductCreator()

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理制作行为"""
        from human.components.action.action_component import ActionComponent, ActionType, ActionStatus

        for entity, (action, task, inventory, skill) in world.get_components(
            ActionComponent, TaskComponent, InventoryComponent, SkillComponent
        ):
            if action.current_action != ActionType.CRAFT:
                continue

            self._process_crafting(world, entity, action, task, inventory, skill)

    def _process_crafting(
        self, world, entity, action, task, inventory, skill
    ) -> None:
        """处理单个制作行为"""
        # 获取制作知识
        knowledge = world.get_component(entity, CraftingKnowledgeComponent)
        if knowledge is None:
            knowledge = CraftingKnowledgeComponent()
            world.add_component(entity, knowledge)

        # 获取目标配方（从知识中选取，或探索新配方）
        target_recipe = action.target_recipe if hasattr(action, 'target_recipe') else None

        if target_recipe is None:
            # 自主探索：基于已有知识建议实验
            available = self._scanner.scan_inventory(inventory)
            suggestion = knowledge.suggest_experiment(available)
            if suggestion:
                target_recipe = suggestion["materials"]
            else:
                self._fail_crafting(action, task, "无可用材料")
                return

        # 检查材料是否充足
        if not self._scanner.has_materials(inventory, target_recipe):
            self._fail_crafting(action, task, "材料不足")
            return

        # 消耗材料
        self._scanner.consume_materials(inventory, target_recipe)

        # 计算制作结果（核心：从材料属性自然推导产出）
        result = self._calculator.calculate_craft_result(
            target_recipe, skill, knowledge, world, entity
        )

        # 记录结果
        knowledge.record_attempt(
            inputs=target_recipe,
            output=result["output"],
            quality=result["quality"],
            success=result["success"],
            conditions=self._calculator.get_environment_conditions(world, entity),
        )

        if result["success"]:
            # 创建产出物
            self._product_creator.create_product(world, entity, result)
            action.status = ActionStatus.SUCCESS
            task.status = TaskStatus.DONE
            action.progress = 1.0

            # 提升相关技术
            if result["output"]:
                tech_name = f"craft_{result['output']}"
                knowledge.improve_technique(tech_name)
                skill.exp["crafting"] = skill.exp.get("crafting", 0) + 1

            logger.debug(
                f"[Crafting] E{entity.id} 成功制作 {result['output']} "
                f"(质量:{result['quality']:.2f})"
            )
        else:
            action.status = ActionStatus.FAILED
            task.status = TaskStatus.FAILED
            action.progress = 0.0
            logger.debug(
                f"[Crafting] E{entity.id} 制作失败: {result.get('reason', '未知原因')}"
            )

    # 向后兼容的委托属性
    @property
    def MATERIAL_PROPERTIES(self):
        return self._scanner.MATERIAL_PROPERTIES

    def _determine_output_type(self, props):
        return self._calculator._determine_output_type(props)

    def _calculate_craft_result(self, materials, skill, knowledge, world, entity):
        return self._calculator.calculate_craft_result(materials, skill, knowledge, world, entity)

    def _fail_crafting(self, action, task, reason: str) -> None:
        """标记制作失败"""
        from human.components.action.action_component import ActionStatus
        from human.components.cognitive.task_component import TaskStatus

        action.status = ActionStatus.FAILED
        task.status = TaskStatus.FAILED
        action.progress = 0.0
        if logger.isEnabledFor(logging.DEBUG):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[Crafting] 失败: {reason}")
