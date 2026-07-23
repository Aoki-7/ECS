#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
物种形成迁移器

职责：
    - 将离群实体迁移到新物种
    - 更新实体的 SpeciationTrackerComponent
"""

import logging
from typing import List, Tuple

from core.world import World
from biology.ecology.components.speciation_tracker_component import SpeciationTrackerComponent

logger = logging.getLogger(__name__)


class SpeciationMigrator:
    """物种形成迁移器"""

    def migrate_entities_to_species(
        self,
        world: World,
        outliers: List[Tuple[int, List[float]]],
        new_species_id: str,
    ) -> None:
        """
        将离群实体迁移到新物种

        Args:
            world: ECS 世界
            outliers: [(entity_id, vector), ...] 离群实体列表
            new_species_id: 新物种 ID
        """
        for eid, _ in outliers:
            entity = world.query_entity(eid)
            if entity is None:
                continue
            tracker = world.get_component(entity, SpeciationTrackerComponent)
            if tracker is None:
                continue
            old_id = tracker.species_id
            tracker.species_id = new_species_id
            logger.debug(
                f"[Speciation] 实体 {eid} 从 '{old_id}' 迁移到 '{new_species_id}'"
            )