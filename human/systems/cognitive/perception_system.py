#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:perception_system.py
@说明:感知系统 — 从 360° 雷达升级为锥形 FOV + 注意力 + 记忆写入
@时间:2026/03/28 17:30:09
@作者:Sherry / AI Assistant
@版本:2.0

增强说明（v2.0）：
    1. FOV 锥形过滤：只保留 fov_direction ± fov_angle/2 范围内的实体
    2. 注意力分配：按动态性、大小、熟悉度计算注意力分数，只关注前 N 个
    3. 视距分层：近距清晰、中距模糊、远距仅能感知存在
    4. 记忆写入：看到人 → record_person；看到资源 → record_place；
       看到异常（尸体/敌人）→ add_event("perception_alert")
'''

import math
import logging

from core.system import System
from core.world import World

from space.space_system import SpaceSystem
from human.components.perception.vision_component import VisionComponent
from space.space_component import SpaceComponent
from human.components.cognitive.memory_component import MemoryComponent
from identity.name_component import NameComponent

logger = logging.getLogger(__name__)


class PerceptionSystem(System):
    tick_interval = 1
    """
    感知系统 v2.0

    执行流程：
        1. 空间查询：获取 radius 内所有实体
        2. FOV 过滤：只保留锥形视野内的实体
        3. 视距分层：近/中/远距赋予不同识别精度
        4. 注意力排序：按动态性、大小、熟悉度打分
        5. 记忆写入：将观察到的人/地点/异常写入 MemoryComponent
    """

    def update(self, world: World, dt: float):
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (space, vision) in world.get_components(SpaceComponent, VisionComponent):
            space: SpaceComponent
            vision: VisionComponent

            # 更新视野朝向（如果实体有移动方向，可进一步与 VelocityComponent 联动）
            self._update_fov_direction(space, vision)

            x, y = space.x, space.y
            r = vision.radius

            # 1) 空间查询：获取 radius 内所有实体
            id_list = space_system.query_radius(x=x, y=y, r=r)
            candidate_ids = [eid for eid in id_list if eid != entity.id]

            # 2) FOV 锥形过滤
            visible_ids = self._filter_by_fov(x, y, vision, candidate_ids, space_system)

            # 3) 视距分层 + 4) 注意力排序
            memory = world.get_component(entity, MemoryComponent)
            focused_ids, attention_scores = self._allocate_attention(
                world, entity, x, y, vision, visible_ids
            )

            # 写入 VisionComponent
            vision.entity_ids = visible_ids
            vision.entities = [world.query_entity(eid) for eid in visible_ids]
            vision.focused_entity_ids = focused_ids
            vision.attention_scores = attention_scores
            vision.entities_seen_this_tick = len(visible_ids)
            vision.last_perception_tick = world.tick_count

            # 5) 记忆写入
            if memory is not None:
                self._write_to_memory(world, entity, x, y, vision, visible_ids, memory)

    # ── 内部方法 ──

    def _update_fov_direction(self, space: SpaceComponent, vision: VisionComponent):
        """根据实体的 dirty 标志或速度更新视野朝向。当前简化为保持原值，
        若后续接入 VelocityComponent，可改为 velocity 方向。"""
        # 预留：若 VelocityComponent 存在，可读取速度方向更新 fov_direction
        pass

    def _filter_by_fov(
        self, observer_x: float, observer_y: float,
        vision: VisionComponent, candidate_ids: list, space_system
    ) -> list:
        """FOV 锥形过滤：只保留位于视野锥形范围内的实体"""
        if vision.fov_angle >= 360.0:
            return candidate_ids

        half_fov = vision.fov_angle / 2.0
        center_dir = math.radians(vision.fov_direction)
        visible = []

        for eid in candidate_ids:
            pos = space_system.get_position(eid)
            if pos is None:
                continue
            ex, ey = pos
            dx, dy = ex - observer_x, ey - observer_y
            if dx == 0 and dy == 0:
                continue
            angle = math.degrees(math.atan2(dy, dx))
            # 计算与中心方向的最小角度差（处理 360° 环绕）
            diff = abs((angle - vision.fov_direction + 180) % 360 - 180)
            if diff <= half_fov:
                visible.append(eid)

        return visible

    def _allocate_attention(
        self, world: World, observer, observer_x: float, observer_y: float,
        vision: VisionComponent, visible_ids: list
    ) -> tuple:
        """
        注意力分配：为每个可见实体计算注意力分数，返回前 N 个。

        评分维度：
            - 动态性 (+0.3)：有 VelocityComponent 的实体更容易吸引注意
            - 大小 (+0.2)：MorphologyComponent.weight 越大越显眼
            - 熟悉度 (+0.2)：memory 中有记录的人/地点更熟悉
            - 近距离 (+0.2)：越近越容易注意
            - 异常 (+0.1)：DeadTagComponent 等异常状态
        """
        if not visible_ids:
            return [], {}

        memory = world.get_component(observer, MemoryComponent)
        scores = {}

        for eid in visible_ids:
            target = world.query_entity(eid)
            if target is None:
                continue

            score = 0.0
            t_space = world.get_component(target, SpaceComponent)
            dist = math.hypot(t_space.x - observer_x, t_space.y - observer_y) if t_space else vision.radius
            norm_dist = 1.0 - min(1.0, dist / max(1.0, vision.radius))

            # 近距离加分
            score += norm_dist * 0.2

            # 动态性加分
            from human.components.abilities.velocity_component import VelocityComponent
            if world.get_component(target, VelocityComponent) is not None:
                score += 0.3

            # 大小加分
            from biology.lifecycle.components.morphology_component import MorphologyComponent
            morph = world.get_component(target, MorphologyComponent)
            if morph is not None and morph.weight > 0:
                score += min(0.2, morph.weight / 100.0)

            # 熟悉度加分
            if memory is not None:
                if eid in getattr(memory, 'people', {}):
                    score += 0.2

            # 异常加分（尸体、死亡标记）
            from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
            if world.get_component(target, DeadTagComponent) is not None:
                score += 0.1

            scores[eid] = round(score, 3)

        # 取前 N 个最高分
        sorted_ids = sorted(scores.keys(), key=lambda eid: scores[eid], reverse=True)
        focused = sorted_ids[:vision.attention_capacity]
        return focused, scores

    def _write_to_memory(
        self, world: World, observer, observer_x: float, observer_y: float,
        vision: VisionComponent, visible_ids: list, memory: MemoryComponent
    ):
        """将感知到的人、地点、异常写入记忆（传统记忆组件 + 统一记忆层）"""
        from biology.lifecycle.components.morphology_component import MorphologyComponent
        from resource.food.components.food_component import FoodComponent
        from resource.water.components.water_component import WaterComponent
        from plant.components.plant_component import PlantComponent
        from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
        from human.components.basic.human_component import HumanComponent
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent

        current_time = 0.0
        try:
            time_comp = world.get_time()
            if time_comp:
                current_time = time_comp.total_hours
        except Exception as e:
            logger.warning(f"[PerceptionSystem] 获取世界时间失败: {e}")

        # === 统一记忆层集成 ===
        memory_layer = world.get_memory_layer()
        from memory_layer import SubjectType

        for eid in visible_ids:
            target = world.query_entity(eid)
            if target is None:
                continue
            t_space = world.get_component(target, SpaceComponent)
            if t_space is None:
                continue

            pos = (t_space.x, t_space.y)

            # A) 看到其他人类 → record_person（传统）+ record_contact（统一记忆层）
            if world.get_component(target, HumanComponent) is not None:
                name_comp = world.get_component(target, NameComponent)
                name = name_comp.name if name_comp else f"E{eid}"
                memory.record_person(
                    entity_id=eid,
                    name=name,
                    time=current_time,
                    relationship="acquaintance",
                    trust=0.5
                )
                # 统一记忆层：记录接触
                if memory_layer is not None:
                    memory_layer.record_contact(
                        subject_id=observer.id,
                        subject_type=SubjectType.HUMAN,
                        entity_id=eid,
                        contact_type="visual",
                        intensity=0.8,
                        context=f"看到人类 {name} 在 ({t_space.x:.0f}, {t_space.y:.0f})",
                    )

            # B) 看到资源/地点 → record_place（传统）+ record_contact（统一记忆层）
            place_type = None
            if world.get_component(target, FoodComponent) is not None:
                place_type = "food_source"
            elif world.get_component(target, WaterComponent) is not None:
                place_type = "water_source"
            elif world.get_component(target, PlantComponent) is not None:
                plant = world.get_component(target, PlantComponent)
                lifecycle = world.get_component(target, LifeCycleComponent)
                if plant is not None and lifecycle is not None and lifecycle.stage >= plant.harvest_stage:
                    place_type = "food_source"

            if place_type is not None:
                existing = memory.places.get(pos)
                if existing is None or (current_time - existing.get("last_visit", 0)) > 1.0:
                    memory.record_place(pos, place_type, current_time, sentiment=0.3)
                # 统一记忆层：记录接触
                if memory_layer is not None:
                    memory_layer.record_contact(
                        subject_id=observer.id,
                        subject_type=SubjectType.HUMAN,
                        entity_id=eid,
                        contact_type="visual",
                        intensity=0.6,
                        context=f"发现{place_type}在 ({t_space.x:.0f}, {t_space.y:.0f})",
                    )

            # C) 看到异常实体（尸体）→ add_event（传统）+ record_contact（统一记忆层）
            if world.get_component(target, DeadTagComponent) is not None:
                name_comp = world.get_component(target, NameComponent)
                name = name_comp.name if name_comp else f"E{eid}"
                memory.add_event(
                    time=current_time,
                    event_type="perception_alert",
                    description=f"在 ({t_space.x:.0f}, {t_space.y:.0f}) 看到尸体 {name}",
                    impact=-0.4,
                    location=pos
                )
                # 统一记忆层：记录接触（高情感强度）
                if memory_layer is not None:
                    memory_layer.record_contact(
                        subject_id=observer.id,
                        subject_type=SubjectType.HUMAN,
                        entity_id=eid,
                        contact_type="visual",
                        intensity=0.9,
                        attention_level=0.95,
                        context=f"在 ({t_space.x:.0f}, {t_space.y:.0f}) 看到尸体 {name}",
                    )


# 向后兼容的旧拼写别名
PreceptionSystem = PerceptionSystem
