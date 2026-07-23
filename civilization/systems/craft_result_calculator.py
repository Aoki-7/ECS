#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作结果计算器

职责：
    - 从材料属性自然推导产出类型和质量
    - 计算成功率
    - 获取环境条件
"""

import random
from typing import Dict, Optional

from core.world import World
from human.components.abilities.skill_component import SkillComponent
from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent
from civilization.systems.crafting_knowledge_system import CraftingKnowledgeSystem
from space.space_component import SpaceComponent

from civilization.systems.material_scanner import MaterialScanner


class CraftResultCalculator:
    """制作结果计算器"""

    def __init__(self):
        self._scanner = MaterialScanner()

    def calculate_craft_result(
        self,
        materials: Dict[str, int],
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
            mat_prop = self._scanner.MATERIAL_PROPERTIES.get(mat_name, {})
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
        knowledge_bonus = CraftingKnowledgeSystem.get_technique_level(knowledge, f"craft_{output_type}") * 0.2

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
            return random.choice(["container", "tool_handle", "building_material"])
        else:
            return random.choice(["misc_item", "decoration", "unknown_craft"])

    def get_environment_conditions(self, world: World, entity) -> Dict:
        """获取环境条件（温度、湿度等）"""
        conditions = {
            "temperature": 20.0,
            "humidity": 0.5,
            "lighting": 1.0,
        }

        # 尝试获取环境组件
        try:
            from environment.environment_component import EnvironmentComponent
            env = world.get_environment()
            if env:
                conditions["temperature"] = getattr(env, 'temperature', 20.0)
                conditions["humidity"] = getattr(env, 'humidity', 0.5)
        except Exception:
            pass

        # 尝试获取空间组件（光照）
        space = world.get_component(entity, SpaceComponent)
        if space:
            # 简化：假设白天光照好
            conditions["lighting"] = 1.0

        return conditions