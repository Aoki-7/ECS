#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物领地系统

处理动物的领地行为：
    1. 领地建立：成年动物自动建立领地
    2. 边界巡逻：定期巡逻领地边界
    3. 入侵检测：检测并记录入侵者
    4. 领地防御：驱逐入侵者
    5. 气味标记：刷新领地气味标记

与 AnimalSocialSystem 的关系：
    - 群体成员共享领地
    - 领地边界决定社交范围
"""

from core.system import System
from core.world import World

from animal.components.animal_component import AnimalComponent
from animal.components.animal_territory_component import AnimalTerritoryComponent
from animal.components.animal_social_component import AnimalSocialComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

import logging

logger = logging.getLogger(__name__)


class AnimalTerritorySystem(System):
    tick_interval = 25

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新动物领地状态"""
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        for entity, (animal, territory, space) in world.get_components(
            AnimalComponent, AnimalTerritoryComponent, SpaceComponent
        ):
            if not animal.is_adult:
                continue

            # 更新领地中心（跟随动物移动）
            self._update_territory_center(territory, space)

            # 检测入侵者
            self._detect_intruders(world, space_system, entity, territory, space)

            # 巡逻与气味标记
            self._patrol_and_mark(world, entity, territory, space, dt)

            # 衰减气味
            territory.decay_scent(0.02 * dt)

    def _update_territory_center(
        self, territory: AnimalTerritoryComponent, space: SpaceComponent
    ) -> None:
        """领地中心缓慢跟随动物当前位置"""
        # 使用平滑跟随，领地中心不会瞬间跳到动物位置
        territory.center_x += (space.x - territory.center_x) * 0.1
        territory.center_y += (space.y - territory.center_y) * 0.1

    def _detect_intruders(
        self, world: World, space_system: SpaceSystem,
        entity, territory: AnimalTerritoryComponent, space: SpaceComponent
    ) -> None:
        """检测领地内的入侵者"""
        nearby = space_system.query_radius(
            x=space.x, y=space.y, r=territory.radius
        )

        current_intruders = []
        for candidate_id in nearby:
            if candidate_id == entity.id:
                continue
            candidate = world.query_entity(candidate_id)
            if candidate is None:
                continue

            # 检查是否是同群体成员
            cand_social = world.get_component(candidate, AnimalSocialComponent)
            entity_social = world.get_component(entity, AnimalSocialComponent)
            if cand_social and entity_social:
                if cand_social.group_id == entity_social.group_id and cand_social.group_id != -1:
                    continue  # 同群体不视为入侵

            cand_space = world.get_component(candidate, SpaceComponent)
            if cand_space and territory.is_inside(cand_space.x, cand_space.y):
                current_intruders.append(candidate_id)
                territory.add_intruder(candidate_id)

        # 移除已离开的入侵者
        territory.intruders = [
            iid for iid in territory.intruders if iid in current_intruders
        ]

        # 高防御等级时驱逐入侵者
        if territory.defense_level > 0.6 and territory.intruders:
            self._defend_territory(world, entity, territory)

    def _defend_territory(
        self, world: World, entity, territory: AnimalTerritoryComponent
    ) -> None:
        """驱逐入侵者"""
        needs = world.get_component(entity, AnimalNeedsComponent)
        if needs:
            needs.fear = max(needs.fear, 0.3)  # 防御时产生一定恐惧

        for intruder_id in territory.intruders[:3]:  # 最多处理 3 个
            intruder = world.query_entity(intruder_id)
            if intruder is None:
                continue
            intruder_needs = world.get_component(intruder, AnimalNeedsComponent)
            if intruder_needs:
                intruder_needs.fear = min(1.0, intruder_needs.fear + 0.5)
                logger.debug(f"[Territory] E{entity.id} 驱逐入侵者 E{intruder_id}")

    def _patrol_and_mark(
        self, world: World, entity,
        territory: AnimalTerritoryComponent, space: SpaceComponent, dt: float
    ) -> None:
        """巡逻边界并刷新气味标记"""
        world_time = getattr(world, 'time', 0)
        time_since_patrol = world_time - territory.last_patrol_time

        # 每 50 tick 巡逻一次
        if time_since_patrol < 50:
            return

        territory.last_patrol_time = world_time

        # 在边界生成标记点
        import math
        territory.boundary_markers = []
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            bx = territory.center_x + territory.radius * math.cos(rad)
            by = territory.center_y + territory.radius * math.sin(rad)
            territory.boundary_markers.append((bx, by))

        # 刷新气味
        territory.refresh_scent()
        logger.debug(f"[Territory] E{entity.id} 巡逻领地并刷新气味")
