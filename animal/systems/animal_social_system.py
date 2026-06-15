#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物社交系统

处理动物的群体行为：
    1. 群体形成：相近个体自动结群
    2. 群体角色分配：leader / member
    3. 配偶配对：异性成熟个体配对
    4. 亲子关系：父母与后代的关联维护
    5. 关系衰减：长期不互动导致关系淡化

与 AnimalReproductionSystem 的关系：
    - SocialSystem 负责配对和群体组织
    - ReproductionSystem 在配对成功后执行繁殖
"""

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_social_component import AnimalSocialComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

import logging

logger = logging.getLogger(__name__)


class AnimalSocialSystem(System):
    tick_interval = 20

    _next_group_id = 1

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新动物社交状态"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 第一阶段：群体形成与维护
        self._update_groups(world, space_system)

        # 第二阶段：配偶配对
        self._update_mating(world, space_system)

        # 第三阶段：关系衰减
        self._decay_relationships(world, dt)

    def _update_groups(self, world: World, space_system: SpaceSystem) -> None:
        """更新群体成员关系"""
        # 收集所有带社交组件的动物
        animals = []
        for entity, (animal, social, space) in world.get_components(
            AnimalComponent, AnimalSocialComponent, SpaceComponent
        ):
            animals.append((entity, animal, social, space))

        # 为独行个体寻找附近群体
        for entity, animal, social, space in animals:
            if social.group_id != -1:
                continue  # 已有群体

            nearest_group = self._find_nearest_group(
                world, space_system, space, social.pack_size_preference
            )
            if nearest_group:
                social.group_id = nearest_group
                social.group_role = "member"
                logger.debug(f"[Social] E{entity.id} 加入群体 {nearest_group}")

    def _find_nearest_group(
        self, world: World, space_system: SpaceSystem,
        space: SpaceComponent, max_size: int
    ) -> int | None:
        """寻找最近的未满群体"""
        nearby = space_system.query_radius(x=space.x, y=space.y, r=10.0)

        group_counts = {}
        for candidate_id in nearby:
            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue
            social = world.get_component(candidate, AnimalSocialComponent)
            if social is None or social.group_id == -1:
                continue
            gid = social.group_id
            group_counts[gid] = group_counts.get(gid, 0) + 1

        # 返回人数最少且未满的群体
        for gid, count in sorted(group_counts.items(), key=lambda x: x[1]):
            if count < max_size:
                return gid
        return None

    def _update_mating(self, world: World, space_system: SpaceSystem) -> None:
        """更新配偶配对"""
        eligible = []
        for entity, (animal, social, needs) in world.get_components(
            AnimalComponent, AnimalSocialComponent, AnimalNeedsComponent
        ):
            if not animal.is_adult:
                continue
            if social.mate_id != -1:
                continue  # 已有配偶
            if needs.reproductive_urge < 0.5:
                continue
            space = world.get_component(entity, SpaceComponent)
            if space:
                eligible.append((entity, animal, social, space))

        # 为每个 eligible 个体寻找最近异性
        for entity, animal, social, space in eligible:
            mate = self._find_mate(world, space_system, entity, animal, space)
            if mate:
                social.mate_id = mate
                # 双向绑定
                mate_social = world.get_component(mate, AnimalSocialComponent)
                if mate_social:
                    mate_social.mate_id = entity.id
                logger.debug(f"[Social] E{entity.id} 与 E{mate.id} 配对")

    def _find_mate(
        self, world: World, space_system: SpaceSystem,
        entity, animal: AnimalComponent, space: SpaceComponent
    ):
        """寻找最近的可配对异性"""
        nearby = space_system.query_radius(x=space.x, y=space.y, r=15.0)

        best_mate = None
        best_dist = float('inf')

        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue
            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            cand_animal = world.get_component(candidate, AnimalComponent)
            if cand_animal is None:
                continue
            if cand_animal.gender == animal.gender:
                continue  # 同性不配对
            if not cand_animal.is_adult:
                continue

            cand_social = world.get_component(candidate, AnimalSocialComponent)
            if cand_social and cand_social.mate_id != -1:
                continue  # 已有配偶

            cand_space = world.get_component(candidate, SpaceComponent)
            if cand_space is None:
                continue

            dist = (space.x - cand_space.x) ** 2 + (space.y - cand_space.y) ** 2
            if dist < best_dist:
                best_dist = dist
                best_mate = candidate

        return best_mate

    def _share_memory(self, world: World, from_entity, to_entity) -> None:
        """分享记忆：通过叙述传播重新生成记忆"""
        import random
        memory_layer = world.get_memory_layer()
        if memory_layer is None:
            return
        
        from memory_layer import SubjectType
        
        # 获取 from_entity 的记忆
        from_memories = memory_layer.get_subject_memories(from_entity.id)
        if not from_memories:
            return
        
        # 选择一个有趣的记忆分享
        interesting_memories = [
            m for m in from_memories
            if m.emotional_tag.intensity > 0.5 or m.recall_count > 2
        ]
        if not interesting_memories:
            return
        
        selected = random.choice(interesting_memories)
        
        # 叙述传播（重新生成，不是复制）
        new_memory = memory_layer.narrate_memory(
            from_subject=from_entity.id,
            to_subject=to_entity.id,
            to_subject_type=SubjectType.ANIMAL,
            concept_id=selected.concept_id,
        )
        
        if new_memory:
            logger.debug(
                f"[Social] E{from_entity.id} 向 E{to_entity.id} "
                f"叙述了 {selected.concept_id} "
                f"(确信度: {new_memory.confidence:.2f})"
            )

    def _decay_relationships(self, world: World, dt: float) -> None:
        """衰减所有社交关系"""
        decay_rate = 0.001 * dt
        # 使用 list() 复制避免迭代修改风险
        for entity, social in list(world.get_components(AnimalSocialComponent)):
            # 衰减关系分数
            to_remove = []
            for other_id, score in social.relationship_scores.items():
                new_score = max(-1.0, score - decay_rate)
                if abs(new_score) < 0.01:
                    to_remove.append(other_id)
                else:
                    social.relationship_scores[other_id] = new_score
            for rid in list(to_remove):
                social.relationship_scores.pop(rid, None)
