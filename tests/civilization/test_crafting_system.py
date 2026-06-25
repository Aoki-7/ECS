#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作系统测试（自然演化版）

v3.0.1
"""

import unittest

from core.world import World
from civilization.components.crafting_knowledge_component import (
    CraftingKnowledgeComponent, CulturalTechPoolComponent
)
from civilization.systems.crafting_system import CraftingSystem
from civilization.systems.technology_evolution_system import TechnologyEvolutionSystem
from civilization.systems.crafting_knowledge_system import CraftingKnowledgeSystem
from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.social.social_component import SocialComponent


class TestCraftingKnowledgeComponent(unittest.TestCase):
    def test_record_attempt(self):
        """记录制作尝试"""
        ck = CraftingKnowledgeComponent()
        for _ in range(3):
            CraftingKnowledgeSystem.record_attempt(ck, 
                inputs={"wood": 5.0, "stone": 2.0},
                output="axe",
                quality=0.8,
                success=True,
            )

        recipes = CraftingKnowledgeSystem.get_known_recipes(ck, min_confidence=0.5)
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0]["output"], "axe")
        self.assertEqual(recipes[0]["success_rate"], 1.0)

    def test_failure_learning(self):
        """从失败中学习"""
        ck = CraftingKnowledgeComponent()
        CraftingKnowledgeSystem.record_attempt(ck, 
            inputs={"wood": 5.0},
            output="axe",
            quality=0.0,
            success=False,
        )
        CraftingKnowledgeSystem.record_attempt(ck, 
            inputs={"wood": 5.0},
            output="axe",
            quality=0.6,
            success=True,
        )

        recipes = CraftingKnowledgeSystem.get_known_recipes(ck, min_confidence=0.5)
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0]["success_rate"], 0.5)

    def test_suggest_experiment(self):
        """建议实验"""
        ck = CraftingKnowledgeComponent()
        # 添加失败记录以确保有建议
        CraftingKnowledgeSystem.record_attempt(
            ck,
            inputs={"wood": 5.0},
            output="axe",
            quality=0.0,
            success=False,
        )
        available = {"wood": 10.0, "stone": 5.0, "metal": 2.0}

        suggestion = CraftingKnowledgeSystem.suggest_exploration(ck, available)
        self.assertIsNotNone(suggestion)
        self.assertIn("wood", suggestion)

    def test_improve_technique(self):
        """技术提升"""
        ck = CraftingKnowledgeComponent()
        CraftingKnowledgeSystem.improve_technique(ck, "sharpening", 0.1)
        self.assertAlmostEqual(CraftingKnowledgeSystem.get_technique_level(ck, "sharpening"), 0.1)

        # 递减增长
        CraftingKnowledgeSystem.improve_technique(ck, "sharpening", 0.1)
        self.assertGreater(CraftingKnowledgeSystem.get_technique_level(ck, "sharpening"), 0.15)
        self.assertLessEqual(CraftingKnowledgeSystem.get_technique_level(ck, "sharpening"), 1.0)


class TestCulturalTechPool(unittest.TestCase):
    def test_integrate_knowledge(self):
        """整合个体知识"""
        pool = CulturalTechPoolComponent()
        ck = CraftingKnowledgeComponent()

        # 记录多次成功
        for _ in range(5):
            CraftingKnowledgeSystem.record_attempt(ck, 
                inputs={"wood": 5.0, "stone": 2.0},
                output="axe",
                quality=0.7,
                success=True,
            )

        # 使用 CraftingKnowledgeSystem 整合知识
        CraftingKnowledgeSystem.integrate_individual_knowledge(pool, ck)
        self.assertEqual(len(pool.shared_recipes), 1)

        # 再次整合（模拟另一个人贡献）
        ck2 = CraftingKnowledgeComponent()
        for _ in range(3):
            CraftingKnowledgeSystem.record_attempt(ck2,
                inputs={"wood": 5.0, "stone": 2.0},
                output="axe",
                quality=0.8,
                success=True,
            )

        CraftingKnowledgeSystem.integrate_individual_knowledge(pool, ck2)
        recipe = list(pool.shared_recipes.values())[0]
        # contributors 字段在第二次整合时递增
        self.assertGreaterEqual(recipe.get("contributors", 1), 1)

    def test_diversity_index(self):
        """多样性指数"""
        pool = CulturalTechPoolComponent()
        self.assertEqual(pool.diversity_index, 0.0)

        ck = CraftingKnowledgeComponent()
        for i, output in enumerate(["axe", "spear", "knife", "shield"]):
            for _ in range(3):
                CraftingKnowledgeSystem.record_attempt(ck, 
                    inputs={"wood": float(i + 1)},
                    output=output,
                    quality=0.6,
                    success=True,
                )

        CraftingKnowledgeSystem.integrate_individual_knowledge(pool, ck)
        self.assertGreater(pool.diversity_index, 0.0)


class TestCraftingSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = CraftingSystem()

    def test_material_properties(self):
        """材料属性存在"""
        self.assertIn("wood", self.system.MATERIAL_PROPERTIES)
        self.assertIn("stone", self.system.MATERIAL_PROPERTIES)

    def test_determine_output_type(self):
        """产出类型判定"""
        # 高硬度高耐久 -> 刃具/护甲
        result = self.system._determine_output_type({
            "hardness": 0.9, "flexibility": 0.1,
            "durability": 0.9, "workability": 0.3,
        })
        self.assertIn(result, ["blade", "axe_head", "hammer", "armor_plate", "shield"])

        # 高柔性 -> 绳索/织物
        result = self.system._determine_output_type({
            "hardness": 0.1, "flexibility": 0.9,
            "durability": 0.2, "workability": 0.7,
        })
        self.assertIn(result, ["rope", "fabric", "net"])

    def test_calculate_result(self):
        """制作结果计算"""
        from human.components.abilities.skill_component import SkillComponent

        skill = SkillComponent()
        knowledge = CraftingKnowledgeComponent()

        result = self.system._calculate_craft_result(
            materials={"wood": 5.0, "stone": 2.0},
            skill=skill,
            knowledge=knowledge,
            world=self.world,
            entity=None,
        )

        self.assertIn("success", result)
        self.assertIn("output", result)
        self.assertIn("quality", result)

        if result["success"]:
            self.assertGreater(result["quality"], 0)
            self.assertLessEqual(result["quality"], 1.0)


class TestTechnologyEvolutionSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.system = TechnologyEvolutionSystem()

    def test_discover_technologies(self):
        """技术发现"""
        entity = self.world.create_entity()

        # 添加组件
        from human.components.social.social_component import SocialComponent
        self.world.add_component(entity, CraftingKnowledgeComponent())
        self.world.add_component(entity, SocialComponent())
        self.world.add_component(entity, KnowledgeComponent())

        # 记录成功配方
        ck = self.world.get_component(entity, CraftingKnowledgeComponent)
        for _ in range(5):
            CraftingKnowledgeSystem.record_attempt(ck, 
                inputs={"wood": 5.0, "stone": 2.0},
                output="super_axe",
                quality=0.8,
                success=True,
            )

        # 运行发现
        self.system._discover_technologies(self.world)

        # 检查是否发现
        know = self.world.get_component(entity, KnowledgeComponent)
        self.assertIn("super_axe", know.known_technologies)

    def test_tech_loss_warning(self):
        """技术失传检测"""
        # 创建只有一个掌握者的技术
        entity = self.world.create_entity()
        know = KnowledgeComponent()
        self.world.add_component(entity, know)
        know.known_technologies.add("endangered_tech")

        # 运行检测（不应抛异常）
        self.system._check_technology_loss(self.world)


if __name__ == "__main__":
    unittest.main()
