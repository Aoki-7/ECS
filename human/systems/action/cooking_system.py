#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
烹饪系统

v3.0.1 新增 — P1

核心设计原则：
- 无硬编码食谱，食物效果从加工方式自然计算
- 生食/熟食/烧焦的效果从温度/时间计算
- 烹饪知识从实践中积累
"""

import random
from typing import Dict

from core.system import System
from core.world import World

from human.components.action.action_component import ActionComponent, ActionType, ActionStatus
from human.components.cognitive.task_component import TaskComponent, TaskType, TaskStatus
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.abilities.skill_component import SkillComponent
from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent

import logging

logger = logging.getLogger(__name__)


class CookingSystem(System):
    """
    烹饪系统

    处理食物加工行为。
    无硬编码食谱，食物效果从加工参数自然计算。
    """

    tick_interval = 1

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理烹饪行为"""
        for entity, (action, task, inventory) in world.get_components(
            ActionComponent, TaskComponent, InventoryComponent
        ):
            if action.current_action != ActionType.EAT:
                # 检查是否是烹饪行为（通过 target_recipe 判断）
                if not hasattr(action, 'target_recipe') or action.target_recipe is None:
                    continue

            self._process_cooking(world, entity, action, task, inventory)

    def _process_cooking(
        self, world, entity, action, task, inventory
    ) -> None:
        """处理单个烹饪行为"""
        # 获取烹饪知识
        knowledge = world.get_component(entity, CraftingKnowledgeComponent)
        if knowledge is None:
            knowledge = CraftingKnowledgeComponent()
            world.add_component(entity, knowledge)

        # 获取原料
        raw_food = action.target_entity
        if raw_food is None:
            self._fail(action, task, "无原料")
            return

        # 获取环境条件
        env = world.get_environment()
        temp = getattr(env, "air_temperature", 20.0) if env else 20.0

        # 获取技能
        skill = world.get_component(entity, SkillComponent)
        skill_level = skill.exp.get("cooking", 0) * 0.01 if skill else 0.0

        # 计算烹饪结果
        result = self._calculate_cooking_result(
            raw_food, temp, action.progress, skill_level
        )

        # 记录知识
        knowledge.record_attempt(
            inputs={"food": 1.0, "heat": temp},
            output=result["state"],
            quality=result["quality"],
            success=result["edible"],
        )

        if result["edible"]:
            action.status = ActionStatus.SUCCESS
            task.status = TaskStatus.DONE
            action.progress = 1.0
            logger.debug(
                f"[Cooking] E{entity.id} 烹饪完成: {result['state']} "
                f"(质量:{result['quality']:.2f})"
            )
        else:
            self._fail(action, task, result["reason"])

    def _calculate_cooking_result(
        self, raw_food, temperature: float, cook_time: float, skill: float
    ) -> Dict:
        """
        计算烹饪结果

        从温度和烹饪时间自然计算食物状态。
        """
        # 烹饪程度 = 温度 × 时间 × 技能
        cook_level = temperature * cook_time * (0.5 + skill)

        if cook_level < 30:
            # 未充分加热
            return {
                "state": "raw",
                "quality": 0.3,
                "edible": True,
                "nutrition": 0.5,
                "reason": "未充分加热",
            }
        elif cook_level < 100:
            # 完美烹饪
            quality = min(1.0, 0.7 + skill * 0.3)
            return {
                "state": "cooked",
                "quality": quality,
                "edible": True,
                "nutrition": 1.0,
                "reason": "",
            }
        elif cook_level < 150:
            # 过熟
            return {
                "state": "overcooked",
                "quality": 0.4,
                "edible": True,
                "nutrition": 0.6,
                "reason": "过熟",
            }
        else:
            # 烧焦
            return {
                "state": "burnt",
                "quality": 0.0,
                "edible": False,
                "nutrition": 0.0,
                "reason": "烧焦了",
            }

    def _fail(self, action, task, reason: str) -> None:
        """标记失败"""
        action.status = ActionStatus.FAILED
        task.status = TaskStatus.FAILED
        action.progress = 0.0
        logger.debug(f"[Cooking] 失败: {reason}")
