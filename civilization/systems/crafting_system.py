#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作系统（自然演化版）

v3.0.1 新增

核心设计原则：
- 无硬编码配方，产出从材料属性和环境条件自然计算
- 每次制作都是实验，结果有随机性
- 成功/失败都产生学习数据
- 不同文明可能发现完全不同的"配方"
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
from space.space_component import SpaceComponent

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

    # 材料基础属性（物理属性，非配方）
    # 这些属性决定材料在制作中的行为，而非固定产出
    MATERIAL_PROPERTIES = {
        "wood": {
            "hardness": 0.3,
            "flexibility": 0.7,
            "durability": 0.4,
            "workability": 0.8,  # 易加工性
        },
        "stone": {
            "hardness": 0.9,
            "flexibility": 0.1,
            "durability": 0.8,
            "workability": 0.3,
        },
        "metal": {
            "hardness": 0.8,
            "flexibility": 0.5,
            "durability": 0.9,
            "workability": 0.4,
        },
        "bone": {
            "hardness": 0.5,
            "flexibility": 0.3,
            "durability": 0.5,
            "workability": 0.6,
        },
        "fiber": {
            "hardness": 0.1,
            "flexibility": 0.9,
            "durability": 0.2,
            "workability": 0.7,
        },
        "clay": {
            "hardness": 0.2,
            "flexibility": 0.4,
            "durability": 0.1,
            "workability": 0.9,
        },
    }

    def update(self, world: World, dt: float = 1.0) -> None:
        """处理制作行为"""
        from core.components.action_component import ActionComponent, ActionType, ActionStatus

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
            available = self._scan_inventory(inventory)
            suggestion = knowledge.suggest_experiment(available)
            if suggestion:
                target_recipe = suggestion["materials"]
            else:
                self._fail_crafting(action, task, "无可用材料")
                return

        # 检查材料是否充足
        if not self._has_materials(inventory, target_recipe):
            self._fail_crafting(action, task, "材料不足")
            return

        # 消耗材料
        self._consume_materials(inventory, target_recipe)

        # 计算制作结果（核心：从材料属性自然推导产出）
        result = self._calculate_craft_result(
            target_recipe, skill, knowledge, world, entity
        )

        # 记录结果
        knowledge.record_attempt(
            inputs=target_recipe,
            output=result["output"],
            quality=result["quality"],
            success=result["success"],
            conditions=self._get_environment_conditions(world, entity),
        )

        if result["success"]:
            # 创建产出物
            self._create_product(world, entity, result)
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
            self._fail_crafting(action, task, f"制作失败: {result['reason']}")

    def _calculate_craft_result(
        self,
        materials: Dict[str, float],
        skill: SkillComponent,
        knowledge: CraftingKnowledgeComponent,
        world: World,
        entity,
    ) -> Dict:
        """
        计算制作结果

        核心算法：从材料物理属性自然推导产出类型和质量。
        无硬编码映射，产出由材料组合 emergent 决定。
        """
        # 收集材料属性
        props = {"hardness": [], "flexibility": [], "durability": [], "workability": []}
        for mat_name, amount in materials.items():
            mat_prop = self.MATERIAL_PROPERTIES.get(mat_name, {})
            weight = amount / sum(materials.values())
            for key in props:
                props[key].append(mat_prop.get(key, 0.5) * weight)

        # 加权平均
        avg_props = {k: sum(v) for k, v in props.items()}

        # 根据材料属性决定产出类型（emergent，非预设）
        output_type = self._determine_output_type(avg_props)

        # 计算成功率
        base_success = 0.3
        workability_bonus = avg_props["workability"] * 0.3
        skill_bonus = min(0.3, skill.exp.get("crafting", 0) * 0.01)
        knowledge_bonus = knowledge.get_technique_level(f"craft_{output_type}") * 0.2

        success_rate = base_success + workability_bonus + skill_bonus + knowledge_bonus
        success_rate = min(0.95, max(0.05, success_rate))

        # 随机判定
        if random.random() > success_rate:
            return {
                "success": False,
                "output": None,
                "quality": 0.0,
                "reason": "手艺不精",
            }

        # 计算质量
        base_quality = avg_props["durability"] * 0.4 + avg_props["workability"] * 0.3
        skill_quality_bonus = skill_bonus * 0.5
        random_factor = random.uniform(-0.1, 0.1)
        quality = min(1.0, max(0.1, base_quality + skill_quality_bonus + random_factor))

        return {
            "success": True,
            "output": output_type,
            "quality": quality,
            "properties": avg_props,
        }

    def _determine_output_type(self, props: Dict[str, float]) -> str:
        """
        根据材料属性决定产出类型

        这是一个 emergent 映射：材料属性组合决定产出。
        不同文明可能发现完全不同的产出命名。
        """
        h = props["hardness"]
        f = props["flexibility"]
        d = props["durability"]
        w = props["workability"]

        # 基于属性组合决定产出类型
        if h > 0.7 and d > 0.7:
            if f < 0.3:
                return random.choice(["blade", "axe_head", "hammer"])
            else:
                return random.choice(["armor_plate", "shield"])
        elif h > 0.5 and f > 0.5:
            return random.choice(["spear", "pole", "handle"])
        elif f > 0.7 and h < 0.3:
            return random.choice(["rope", "fabric", "net"])
        elif w > 0.7 and h < 0.4:
            return random.choice(["pottery", "brick", "figurine"])
        elif d > 0.6 and h > 0.4:
            return random.choice(["container", "building_material"])
        else:
            # 通用产出
            return random.choice(["tool", "ornament", "utensil"])

    def _get_environment_conditions(self, world: World, entity) -> Dict:
        """获取环境条件（影响制作结果）"""
        env = world.get_environment()
        space = world.get_component(entity, SpaceComponent)
        conditions = {}

        if env:
            conditions["temperature"] = getattr(env, "air_temperature", 20.0)
            conditions["humidity"] = getattr(env, "relative_humidity", 50.0)

        if space:
            conditions["has_shelter"] = False  # 可扩展：检查是否在建筑内

        return conditions

    def _scan_inventory(self, inventory: InventoryComponent) -> Dict[str, float]:
        """扫描背包中的材料"""
        # 简化实现：返回材料类型和数量
        materials = {}
        # 这里需要根据实际 inventory 结构实现
        # 假设 inventory.items 存储了材料
        if hasattr(inventory, 'items'):
            for item_id in inventory.items:
                # 简化为通用材料分类
                mat_type = self._classify_material(item_id)
                if mat_type:
                    materials[mat_type] = materials.get(mat_type, 0) + 1
        return materials

    def _classify_material(self, item_id: int) -> Optional[str]:
        """将物品分类为材料类型"""
        # 简化实现，实际应根据物品组件判断
        # 这里使用 hash 模拟分类
        categories = ["wood", "stone", "metal", "bone", "fiber", "clay"]
        return categories[item_id % len(categories)]

    def _has_materials(self, inventory: InventoryComponent, materials: Dict[str, float]) -> bool:
        """检查是否有足够材料"""
        available = self._scan_inventory(inventory)
        for mat, amount in materials.items():
            if available.get(mat, 0) < amount:
                return False
        return True

    def _consume_materials(self, inventory: InventoryComponent, materials: Dict[str, float]) -> None:
        """消耗材料"""
        # 简化实现
        pass

    def _create_product(self, world: World, entity, result: Dict) -> None:
        """创建产出物"""
        from core.entity import Entity
        from space.space_component import SpaceComponent

        product = world.create_entity()
        space = world.get_component(entity, SpaceComponent)
        if space:
            world.add_component(product, SpaceComponent(
                x=space.x + random.randint(-1, 1),
                y=space.y + random.randint(-1, 1),
            ))

        # 产出物属性由制作结果决定
        # 可扩展：添加 ProductComponent 存储质量、制作者等

    def _fail_crafting(self, action, task, reason: str) -> None:
        """标记制作失败"""
        from core.components.action_component import ActionStatus
        from human.components.cognitive.task_component import TaskStatus

        action.status = ActionStatus.FAILED
        task.status = TaskStatus.FAILED
        action.progress = 0.0
        logger.debug(f"[Crafting] 失败: {reason}")
