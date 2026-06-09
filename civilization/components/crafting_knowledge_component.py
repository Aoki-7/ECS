#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CraftingKnowledgeComponent — 制作知识组件（自然演化版）

v3.0.1 新增

核心设计原则：
- 无硬编码配方，配方从实践中自然涌现
- 技术不是"解锁"的，而是"发现"的
- 同一文明可能发展出完全不同的技术路线
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import random

from core.component import Component


@dataclass(slots=True)
class CraftingKnowledgeComponent(Component):
    """
    制作知识组件

    记录个体/文明通过实践积累的制作经验。
    配方不是预设的，而是从成功尝试中自然形成的。
    """

    # 材料组合 -> 产出记录（从实践中学习）
    # key: "材料A+材料B+..." value: {产出物: 成功次数, 失败次数, 质量统计}
    material_experiments: Dict[str, Dict[str, Dict]] = field(default_factory=dict)

    # 已知制作技巧（从成功中提炼）
    # key: 技巧名 value: 熟练度(0-1)
    techniques: Dict[str, float] = field(default_factory=dict)

    # 成功案例记录（用于传授给他人）
    # [(输入材料, 产出物, 质量, 环境条件), ...]
    success_records: List[Dict] = field(default_factory=list)

    # 失败案例记录（避免重复错误）
    failure_records: List[Dict] = field(default_factory=list)

    # 探索倾向（0=保守，1=激进）— 影响尝试新配方的概率
    exploration_tendency: float = 0.3

    def record_attempt(
        self,
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
        key = self._material_key(inputs)
        record = {
            "inputs": inputs.copy(),
            "output": output,
            "quality": quality,
            "conditions": conditions or {},
        }

        if key not in self.material_experiments:
            self.material_experiments[key] = {}

        if output:
            if output not in self.material_experiments[key]:
                self.material_experiments[key][output] = {
                    "success": 0, "failure": 0,
                    "quality_sum": 0.0, "quality_count": 0,
                }

            if success:
                self.material_experiments[key][output]["success"] += 1
                self.material_experiments[key][output]["quality_sum"] += quality
                self.material_experiments[key][output]["quality_count"] += 1
                self.success_records.append(record)
            else:
                self.material_experiments[key][output]["failure"] += 1
                self.failure_records.append(record)

    def get_known_recipes(self, min_confidence: float = 0.5) -> List[Dict]:
        """
        获取已知的可靠配方

        从实验记录中提取高成功率的组合。
        """
        recipes = []
        for material_key, outputs in self.material_experiments.items():
            for output, stats in outputs.items():
                total = stats["success"] + stats["failure"]
                if total == 0:
                    continue
                success_rate = stats["success"] / total
                if success_rate >= min_confidence and total >= 2:
                    avg_quality = (
                        stats["quality_sum"] / stats["quality_count"]
                        if stats["quality_count"] > 0 else 0.0
                    )
                    recipes.append({
                        "materials": self._parse_material_key(material_key),
                        "output": output,
                        "success_rate": success_rate,
                        "avg_quality": avg_quality,
                        "attempts": total,
                    })
        # 按成功率排序
        recipes.sort(key=lambda r: r["success_rate"], reverse=True)
        return recipes

    def suggest_experiment(self, available_materials: Dict[str, float]) -> Optional[Dict]:
        """
        建议下一个实验

        基于已有知识和探索倾向，建议尝试新的材料组合。
        """
        # 如果探索倾向高，尝试随机组合
        if random.random() < self.exploration_tendency:
            return self._suggest_random_combo(available_materials)

        # 否则，基于已知成功配方做变体
        known = self.get_known_recipes(min_confidence=0.3)
        if not known:
            return self._suggest_random_combo(available_materials)

        # 选择一个成功配方，尝试添加/替换一种材料
        base = random.choice(known[:3])  # 从前3个成功配方中选
        return self._suggest_variant(base, available_materials)

    def improve_technique(self, technique: str, amount: float = 0.05) -> None:
        """提升某项技术的熟练度"""
        current = self.techniques.get(technique, 0.0)
        self.techniques[technique] = min(1.0, current + amount * (1.0 - current))

    def get_technique_level(self, technique: str) -> float:
        """获取技术熟练度"""
        return self.techniques.get(technique, 0.0)

    def _material_key(self, materials: Dict[str, float]) -> str:
        """将材料字典转为排序后的字符串键"""
        return "+".join(sorted(f"{k}:{v:.1f}" for k, v in materials.items()))

    def _parse_material_key(self, key: str) -> Dict[str, float]:
        """解析材料键"""
        result = {}
        for part in key.split("+"):
            if ":" in part:
                k, v = part.split(":")
                result[k] = float(v)
        return result

    def _suggest_random_combo(self, materials: Dict[str, float]) -> Optional[Dict]:
        """建议随机材料组合"""
        if len(materials) < 1:
            return None
        # 随机选择 1-3 种材料
        n = min(random.randint(1, 3), len(materials))
        chosen = random.sample(list(materials.keys()), n)
        combo = {k: min(materials[k], random.uniform(1.0, 5.0)) for k in chosen}
        return {"materials": combo, "reason": "exploration"}

    def _suggest_variant(
        self, base_recipe: Dict, available: Dict[str, float]
    ) -> Optional[Dict]:
        """基于成功配方建议变体"""
        base_materials = base_recipe["materials"].copy()

        # 随机添加一种新材料
        new_materials = set(available.keys()) - set(base_materials.keys())
        if new_materials and random.random() < 0.5:
            new_mat = random.choice(list(new_materials))
            base_materials[new_mat] = min(available[new_mat], random.uniform(1.0, 3.0))
            return {"materials": base_materials, "reason": "variant_add"}

        # 或改变比例
        if base_materials:
            mat = random.choice(list(base_materials.keys()))
            base_materials[mat] *= random.uniform(0.5, 2.0)
            return {"materials": base_materials, "reason": "variant_ratio"}

        return None


@dataclass(slots=True)
class CulturalTechPoolComponent(Component):
    """
    文明技术池组件

    记录整个文明（部落/社会）共享的技术知识。
    不同于个体的 CraftingKnowledge，这是群体层面的技术积累。
    """

    # 群体共享的配方（由个体成功案例汇聚）
    shared_recipes: Dict[str, Dict] = field(default_factory=dict)

    # 技术传统（该文明偏好的技术方向）
    # 从实践中自然形成，非预设
    tech_traditions: Dict[str, float] = field(default_factory=dict)

    # 知识传播记录（谁教给了谁）
    knowledge_transfers: List[Dict] = field(default_factory=list)

    # 技术多样性指数（越高说明该文明技术路线越独特）
    diversity_index: float = 0.0

    def integrate_individual_knowledge(self, individual_knowledge: CraftingKnowledgeComponent) -> None:
        """
        将个体的制作知识整合到群体技术池中

        只有经过多次验证的配方才会被群体接受。
        """
        recipes = individual_knowledge.get_known_recipes(min_confidence=0.6)
        for recipe in recipes:
            key = self._recipe_key(recipe["materials"], recipe["output"])
            if key not in self.shared_recipes:
                self.shared_recipes[key] = {
                    "materials": recipe["materials"],
                    "output": recipe["output"],
                    "success_rate": recipe["success_rate"],
                    "avg_quality": recipe["avg_quality"],
                    "contributors": 1,
                    "attempts": recipe["attempts"],
                }
            else:
                # 更新群体知识（加权平均）
                existing = self.shared_recipes[key]
                total_attempts = existing["attempts"] + recipe["attempts"]
                existing["success_rate"] = (
                    existing["success_rate"] * existing["attempts"] +
                    recipe["success_rate"] * recipe["attempts"]
                ) / total_attempts
                existing["avg_quality"] = (
                    existing["avg_quality"] * existing["attempts"] +
                    recipe["avg_quality"] * recipe["attempts"]
                ) / total_attempts
                existing["attempts"] = total_attempts
                existing["contributors"] += 1

        self._update_diversity()

    def _recipe_key(self, materials: Dict[str, float], output: str) -> str:
        mat_key = "+".join(sorted(materials.keys()))
        return f"{mat_key}->{output}"

    def _update_diversity(self) -> None:
        """更新技术多样性指数"""
        if not self.shared_recipes:
            self.diversity_index = 0.0
            return

        # 计算输出类型的多样性
        outputs = set(r["output"] for r in self.shared_recipes.values())
        self.diversity_index = min(1.0, len(outputs) / 10.0)
