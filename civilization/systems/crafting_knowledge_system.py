#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作知识系统

提供 CraftingKnowledgeComponent 的静态操作方法。
"""

from typing import Dict, List, Optional
import random

from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent


class CraftingKnowledgeSystem:
    """制作知识系统 - 静态方法操作 CraftingKnowledgeComponent"""

    @staticmethod
    def improve_technique(knowledge: CraftingKnowledgeComponent, technique: str, amount: float) -> None:
        """提升技术熟练度"""
        current = knowledge.techniques.get(technique, 0.0)
        # 递减增长
        knowledge.techniques[technique] = min(1.0, current + amount * (1.0 - current * 0.5))

    @staticmethod
    def get_technique_level(knowledge: CraftingKnowledgeComponent, technique: str) -> float:
        """获取技术熟练度"""
        return knowledge.techniques.get(technique, 0.0)

    @staticmethod
    def _material_key(inputs: Dict[str, float]) -> str:
        """生成材料组合键"""
        sorted_items = sorted(inputs.items(), key=lambda x: x[0])
        return "+".join(f"{k}:{v:.1f}" for k, v in sorted_items)

    @staticmethod
    def record_attempt(
        knowledge: CraftingKnowledgeComponent,
        inputs: Dict[str, float],
        output: Optional[str],
        quality: float = 0.0,
        success: bool = True,
        conditions: Optional[Dict] = None,
    ) -> None:
        """
        记录一次制作尝试

        从实践中学习，逐步形成配方知识。
        """
        key = CraftingKnowledgeSystem._material_key(inputs)
        record = {
            "inputs": inputs.copy(),
            "output": output,
            "quality": quality,
            "conditions": conditions or {},
        }

        if key not in knowledge.material_experiments:
            knowledge.material_experiments[key] = {}

        if output:
            if output not in knowledge.material_experiments[key]:
                knowledge.material_experiments[key][output] = {
                    "success": 0, "failure": 0,
                    "quality_sum": 0.0, "quality_count": 0,
                }

            if success:
                knowledge.material_experiments[key][output]["success"] += 1
                knowledge.material_experiments[key][output]["quality_sum"] += quality
                knowledge.material_experiments[key][output]["quality_count"] += 1
                knowledge.success_records.append(record)
            else:
                knowledge.material_experiments[key][output]["failure"] += 1
                knowledge.failure_records.append(record)

    @staticmethod
    def get_known_recipes(knowledge: CraftingKnowledgeComponent, min_confidence: float = 0.5) -> List[Dict]:
        """
        获取已知的可靠配方

        confidence = 成功次数 / (成功次数 + 失败次数)
        """
        recipes = []
        for material_key, outputs in knowledge.material_experiments.items():
            for output, stats in outputs.items():
                total = stats["success"] + stats["failure"]
                if total == 0:
                    continue
                confidence = stats["success"] / total
                if confidence >= min_confidence:
                    avg_quality = (
                        stats["quality_sum"] / stats["quality_count"]
                        if stats["quality_count"] > 0 else 0.0
                    )
                    recipes.append({
                        "materials": material_key,
                        "output": output,
                        "confidence": confidence,
                        "avg_quality": avg_quality,
                        "success_count": stats["success"],
                        "success_rate": confidence,
                    })
        return sorted(recipes, key=lambda x: x["confidence"], reverse=True)

    @staticmethod
    def get_best_recipe(knowledge: CraftingKnowledgeComponent, available_materials: Dict[str, float]) -> Optional[Dict]:
        """
        根据可用材料获取最佳配方
        """
        candidates = []
        for recipe in CraftingKnowledgeSystem.get_known_recipes(knowledge, min_confidence=0.3):
            materials = recipe["materials"].split("+")
            material_names = [m.split(":")[0] for m in materials]
            if all(m in available_materials for m in material_names):
                candidates.append(recipe)

        if not candidates:
            return None
        return max(candidates, key=lambda x: x["confidence"] * x["avg_quality"])

    @staticmethod
    def integrate_individual_knowledge(pool, knowledge: CraftingKnowledgeComponent, min_confidence: float = 0.6) -> None:
        """将个体知识整合到文明技术池"""
        recipes = CraftingKnowledgeSystem.get_known_recipes(knowledge, min_confidence=min_confidence)
        for recipe in recipes:
            key = recipe["materials"] + "->" + recipe["output"]
            if key not in pool.shared_recipes:
                # 复制配方并添加 contributors 字段
                recipe_copy = dict(recipe)
                recipe_copy["contributors"] = 1
                pool.shared_recipes[key] = recipe_copy
            else:
                # 确保 contributors 字段存在并递增
                existing = pool.shared_recipes[key]
                existing["contributors"] = existing.get("contributors", 1) + 1

        # 更新多样性指数
        if pool.shared_recipes:
            pool.diversity_index = len(pool.shared_recipes) / 100.0

    @staticmethod
    def suggest_exploration(knowledge: CraftingKnowledgeComponent, available: Optional[Dict[str, float]] = None) -> Optional[Dict[str, float]]:
        """
        建议一次探索性尝试

        基于历史失败案例，建议新的材料组合。
        """
        if not knowledge.failure_records:
            return None
        
        # 从失败记录中提取材料，尝试微调
        record = random.choice(knowledge.failure_records)
        materials = record["inputs"].copy()

        # 随机调整一种材料的比例
        if materials:
            key = random.choice(list(materials.keys()))
            materials[key] *= random.uniform(0.5, 2.0)

        return materials

    @staticmethod
    def teach(knowledge: CraftingKnowledgeComponent, student_knowledge: "CraftingKnowledgeComponent", max_recipes: int = 3) -> int:
        """
        传授知识给另一个个体

        返回传授的配方数量。
        """
        recipes = CraftingKnowledgeSystem.get_known_recipes(knowledge, min_confidence=0.7)
        taught = 0

        for recipe in recipes[:max_recipes]:
            if recipe["materials"] not in student_knowledge.material_experiments:
                student_knowledge.material_experiments[recipe["materials"]] = {}

            output = recipe["output"]
            if output not in student_knowledge.material_experiments[recipe["materials"]]:
                student_knowledge.material_experiments[recipe["materials"]][output] = {
                    "success": 1, "failure": 0,
                    "quality_sum": recipe["avg_quality"],
                    "quality_count": 1,
                }
                taught += 1

        return taught

    @staticmethod
    def integrate_individual_knowledge(pool: "CulturalTechPoolComponent", knowledge: CraftingKnowledgeComponent) -> None:
        """将个体知识整合到文明技术池"""
        recipes = CraftingKnowledgeSystem.get_known_recipes(knowledge, min_confidence=0.6)
        for recipe in recipes:
            key = recipe["materials"] + "->" + recipe["output"]
            if key not in pool.shared_recipes:
                pool.shared_recipes[key] = recipe

        # 更新多样性指数
        if pool.shared_recipes:
            pool.diversity_index = len(pool.shared_recipes) / 100.0