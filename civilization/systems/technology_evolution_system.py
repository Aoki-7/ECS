#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术演化系统（自然演化版）

v3.0.1 新增

核心设计原则：
- 无预设技术树，技术从实践中自然涌现
- 技术传播通过社会学习（观察、模仿、教导）
- 技术可能失传，也可能独立发明
- 不同文明可能发展出完全不同的技术路线
"""

import random
import math
from typing import Dict, List, Optional, Set, Tuple

from core.system import System
from core.world import World

from human.components.cognitive.knowledge_component import KnowledgeComponent
from human.components.social.social_component import SocialComponent
from civilization.components.crafting_knowledge_component import (
    CraftingKnowledgeComponent, CulturalTechPoolComponent
)
from civilization.systems.crafting_knowledge_system import CraftingKnowledgeSystem

import logging

logger = logging.getLogger(__name__)


class TechnologyEvolutionSystem(System):
    """
    技术演化系统

    职责：
        - 从个体制作实践中发现新技术
        - 技术在社会中传播
        - 技术可能失传或复兴
        - 记录文明的技术特征
    """

    tick_interval = 50  # 每50帧执行一次（技术演化较慢）

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新技术演化"""
        # 1. 从个体知识中发现新技术
        self._discover_technologies(world)

        # 2. 技术在社会中传播
        self._spread_technologies(world)

        # 3. 检查技术失传
        self._check_technology_loss(world)

        # 4. 更新文明技术池
        self._update_cultural_tech_pools(world)

    def _discover_technologies(self, world: World) -> None:
        """从个体实践中发现新技术"""
        for entity, (knowledge, social) in world.get_components(
            CraftingKnowledgeComponent, SocialComponent
        ):
            # 获取高成功率的新配方
            new_recipes = CraftingKnowledgeSystem.get_known_recipes(knowledge, min_confidence=0.7)

            for recipe in new_recipes:
                # 检查是否是"新"技术（之前不知道）
                tech_name = recipe["output"]

                # 记录到个体知识
                know_comp = world.get_component(entity, KnowledgeComponent)
                if know_comp and tech_name not in know_comp.known_technologies:
                    know_comp.known_technologies.add(tech_name)
                    logger.info(
                        f"[TechEvolution] E{entity.id} 发现了 {tech_name} "
                        f"(成功率:{recipe['success_rate']:.1%}, "
                        f"质量:{recipe['avg_quality']:.2f})"
                    )

    def _spread_technologies(self, world: World) -> None:
        """技术在社会中传播 — 优化版：使用空间索引避免O(n²)"""
        from space.space_component import SpaceComponent
        from space.space_system import SpaceSystem

        # 获取空间系统
        space_system = world.get_system(SpaceSystem)
        
        # 获取所有有知识的个体
        knowledgeable = []
        for entity, (knowledge, space) in world.get_components(
            CraftingKnowledgeComponent, SpaceComponent
        ):
            recipes = CraftingKnowledgeSystem.get_known_recipes(knowledge, min_confidence=0.5)
            if recipes:
                knowledgeable.append((entity, space, recipes))

        # 使用空间索引避免O(n²)比较
        if space_system and hasattr(space_system, 'query_radius'):
            for teacher, t_space, t_recipes in knowledgeable:
                nearby_entities = space_system.query_radius(t_space.x, t_space.y, 5.0)
                for learner_id in nearby_entities:
                    if learner_id == teacher.id:
                        continue
                    learner = world.query_entity(learner_id)
                    if learner is None:
                        continue
                    learner_knowledge = world.get_component(learner, CraftingKnowledgeComponent)
                    if learner_knowledge is None:
                        continue
                    # 尝试传播知识
                    self._attempt_teach(world, teacher, learner, t_recipes)
        else:
            # 回退到O(n²)比较（空间索引不可用时）
            for i, (teacher, t_space, t_recipes) in enumerate(knowledgeable):
                for learner, l_space, _ in knowledgeable[i+1:]:
                    dist = math.hypot(t_space.x - l_space.x, t_space.y - l_space.y)
                    if dist > 5.0:  # 传播距离限制
                        continue
                    # 尝试传播知识
                    self._attempt_teach(world, teacher, learner, t_recipes)

    def _attempt_teach(
        self, world: World, teacher, learner, recipes: List[Dict]
    ) -> None:
        """尝试教导附近个体一个已知配方"""
        learner_knowledge = world.get_component(learner, CraftingKnowledgeComponent)
        if learner_knowledge is None:
            return

        # 随机选择一个配方传授
        recipe = random.choice(recipes)
        # recipe["materials"] 是 CraftingKnowledgeSystem 生成的字符串键，
        # 形如 "wood:1.0+stone:2.0"，需要解析回字典供 record_attempt 使用
        material_dict = {}
        for part in recipe["materials"].split("+"):
            if ":" in part:
                name, amount = part.split(":", 1)
                material_dict[name] = float(amount)

        # 学习者记录这次"学习"（成功率打折扣，学习不如亲自实验）
        CraftingKnowledgeSystem.record_attempt(
            learner_knowledge,
            inputs=material_dict,
            output=recipe["output"],
            quality=recipe.get("avg_quality", 0.0) * 0.7,
            success=True,
            conditions={"learned_from": teacher.id, "is_taught": True},
        )

        # 更新文化技术池
        cult_pool = world.get_component(learner, CulturalTechPoolComponent)
        if cult_pool:
            cult_pool.knowledge_transfers.append({
                "from": teacher.id,
                "to": learner.id,
                "tech": recipe["output"],
            })

    def _check_technology_loss(self, world: World) -> None:
        """检查技术是否失传"""
        # 如果某个技术只有少数人知道，可能失传
        tech_holders: Dict[str, List[int]] = {}

        for entity, (know_comp) in world.get_components(KnowledgeComponent):
            # 确保 know_comp 是组件实例而非列表
            if not hasattr(know_comp, 'known_technologies'):
                continue
            # 确保 known_technologies 是集合
            techs = know_comp.known_technologies
            if isinstance(techs, list):
                techs = set(techs)
            for tech in techs:
                if tech not in tech_holders:
                    tech_holders[tech] = []
                tech_holders[tech].append(entity.id)

        # 检查濒危技术
        for tech, holders in tech_holders.items():
            if len(holders) <= 1:
                logger.warning(
                    f"[TechEvolution] {tech} 濒临失传！仅剩 {len(holders)} 人掌握"
                )

    def _update_cultural_tech_pools(self, world: World) -> None:
        """更新文明技术池"""
        for entity, (cult_pool) in world.get_components(CulturalTechPoolComponent):
            # 整合周围个体的知识
            from space.space_component import SpaceComponent
            space = world.get_component(entity, SpaceComponent)
            if not space:
                continue

            # 收集附近个体的知识
            nearby_knowledge = []
            for other, (other_space, other_know) in world.get_components(
                SpaceComponent, CraftingKnowledgeComponent
            ):
                if other.id == entity.id:
                    continue
                dist = math.hypot(space.x - other_space.x, space.y - other_space.y)
                if dist <= 10.0:
                    nearby_knowledge.append(other_know)

            # 整合到群体知识
            for nk in nearby_knowledge:
                cult_pool.integrate_individual_knowledge(nk)

            # 更新技术传统（该文明最擅长的方向）
            if cult_pool.shared_recipes:
                outputs = {}
                for recipe in cult_pool.shared_recipes.values():
                    out = recipe["output"]
                    outputs[out] = outputs.get(out, 0) + recipe["success_rate"]

                # 找出最擅长的技术方向
                if outputs:
                    top_tech = max(outputs, key=outputs.get)
                    cult_pool.tech_traditions[top_tech] = outputs[top_tech]