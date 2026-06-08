#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:disease_spread_system.py
@说明:疾病传播系统
@时间:2026/05/29
@版本:1.0
'''

import random

from core.system import System
from core.world import World

from biology.components.disease_component import DiseaseComponent, DiseaseRecord
from biology.components.health_status_component import HealthStatusComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem


class DiseaseSpreadSystem(System):
    tick_interval = 10  # 每10帧执行一次
    """
    疾病传播系统
    处理疾病在邻近实体间的传播和疾病进展
    """

    SPREAD_RADIUS = 3          # 传播半径（格）
    BASE_SPREAD_CHANCE = 0.01  # 基础传播概率 /小时
    IMMUNITY_THRESHOLD = 0.8   # 免疫阈值，超过此值不感染

    def update(self, world: World, dt: float):
        space_system = world.get_system(SpaceSystem)
        if space_system is None:
            return

        # 第一遍：疾病进展 + 传播
        for entity, (disease_comp, health, space) in list(world.get_components(
            DiseaseComponent, HealthStatusComponent, SpaceComponent
        )):
            disease_comp: DiseaseComponent
            health: HealthStatusComponent
            space: SpaceComponent

            for disease in list(disease_comp.diseases):
                # 疾病进展
                disease.elapsed += dt

                # hp 伤害
                if disease.damage_rate > 0:
                    health.hp -= disease.damage_rate * dt
                    health.hp = max(0.0, health.hp)

                # 治愈判定：自然消退或免疫足够
                immunity = disease_comp.immunity.get(disease.name, 0.0)
                if disease.duration > 0 and disease.elapsed >= disease.duration:
                    disease_comp.remove_disease(disease.name)
                    continue
                if immunity >= self.IMMUNITY_THRESHOLD:
                    disease_comp.remove_disease(disease.name)
                    continue

                # 免疫自然增长（带病期间缓慢获得免疫）
                disease_comp.immunity[disease.name] = min(
                    1.0, immunity + 0.001 * dt
                )

                # 传播给邻近实体
                self._try_spread(
                    world, space_system, entity, space, disease, dt
                )

    def _try_spread(self, world, space_system, source_entity, space, disease, dt: float):
        """尝试将疾病传播给邻近实体"""
        if disease.contagion <= 0:
            return

        nearby_ids = space_system.neighbors(
            space.x, space.y, self.SPREAD_RADIUS, space.layer
        )

        for target_id in nearby_ids:
            if target_id == source_entity.id:
                continue

            target = world.query_entity(target_id)
            if target is None or not target.is_alive():
                continue

            target_disease = world.get_component(target, DiseaseComponent)
            if target_disease is None:
                continue

            # 已感染则跳过
            if target_disease.has_disease(disease.name):
                continue

            # 免疫检查
            immunity = target_disease.immunity.get(disease.name, 0.0)
            if immunity >= self.IMMUNITY_THRESHOLD:
                continue

            # 传播判定
            spread_chance = self.BASE_SPREAD_CHANCE * disease.contagion * dt
            if random.random() < spread_chance:
                target_disease.add_disease(DiseaseRecord(
                    name=disease.name,
                    type=disease.type,
                    severity=disease.severity * 0.5,
                    contagion=disease.contagion,
                    duration=disease.duration,
                    elapsed=0.0,
                    damage_rate=disease.damage_rate * 0.5,
                ))