#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
人类观察系统

定期（默认每20帧）收集所有 human 的关键状态，
存储到 HumanObservationComponent 中，支持观察模式与历史回溯。
"""

import logging

from core.system import System
from core.world import World

from human.components.basic.human_component import HumanComponent
from human.components.basic.identity_component import IdentityComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.gender_component import GenderComponent, Gender
from biology.components.physiology_needs_component import PhysiologyNeedsComponent
from biology.components.health_status_component import HealthStatusComponent
from biology.components.disease_component import DiseaseComponent
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.cognitive.intent_component import IntentComponent
from human.components.action.action_component import ActionComponent
from human.components.social.tribe_membership_component import TribeMembershipComponent
from space.space_component import SpaceComponent

from presentation.human_observation_component import HumanObservationComponent

logger = logging.getLogger(__name__)


class HumanObservationSystem(System):
    """
    人类观察系统

    定期快照所有 human 的关键状态，支持：
    - 实时观察面板的数据来源
    - 历史回溯（查看某个 human 的状态变化轨迹）
    - 人口趋势统计
    """

    tick_interval = 20  # 每20帧记录一次

    def __init__(self):
        super().__init__()

    def on_add(self, world: World):
        """自动挂载 HumanObservationComponent 到 world_entity"""
        if world.get_world_component(HumanObservationComponent) is None:
            world.get_world_entity().add_component(HumanObservationComponent())

    def on_remove(self, world: World):
        """系统移除时清理 HumanObservationComponent"""
        we = world.get_world_entity()
        if we:
            comp = world.get_component(we, HumanObservationComponent)
            if comp:
                we.remove_component(HumanObservationComponent)

    def update(self, world: World, dt: float = 1.0) -> None:
        snapshot = self._collect_snapshot(world)
        comp = world.get_world_component(HumanObservationComponent)
        if comp is None:
            comp = HumanObservationComponent()
            world.get_world_entity().add_component(comp)
        comp.add_snapshot(snapshot)
        logger.debug(
            "[HumanObservation] 记录快照 step=%d humans=%d",
            snapshot["step"], len(snapshot["humans"]),
        )

    def _collect_snapshot(self, world: World) -> dict:
        """收集当前所有 human 的状态快照"""
        time_comp = world.get_time()
        step = getattr(world, "_step_count", 0)

        humans = []
        for entity, _ in world.get_components(HumanComponent):
            identity = world.get_component(entity, IdentityComponent)
            age = world.get_component(entity, LifeCycleComponent)
            gender = world.get_component(entity, GenderComponent)
            needs = world.get_component(entity, PhysiologyNeedsComponent)
            health = world.get_component(entity, HealthStatusComponent)
            disease = world.get_component(entity, DiseaseComponent)
            emotion = world.get_component(entity, EmotionComponent)
            intent = world.get_component(entity, IntentComponent)
            action = world.get_component(entity, ActionComponent)
            space = world.get_component(entity, SpaceComponent)
            membership = world.get_component(entity, TribeMembershipComponent)

            # 疾病信息（只记录严重度>0的）
            diseases = []
            if disease and disease.diseases:
                for d in disease.diseases:
                    if d.severity > 0:
                        diseases.append({
                            "name": d.name,
                            "severity": round(d.severity, 1),
                        })

            # 部落信息
            tribe_info = "-"
            if membership and membership.is_member():
                role = (
                    "首领" if membership.is_leader()
                    else "长老" if membership.role == "elder"
                    else "成员"
                )
                tribe_info = f"{role}(忠{membership.loyalty:.0f})"

            gender_str = (
                "M" if (gender and gender.gender == Gender.MALE)
                else "F" if (gender and gender.gender == Gender.FEMALE)
                else "?"
            )

            humans.append({
                "entity_id": entity.id,
                "name": identity.name if identity else f"E{entity.id}",
                "age": round(age.age, 1) if age else 0.0,
                "gender": gender_str,
                "position": (round(space.x, 1), round(space.y, 1)) if space else (None, None),
                "hp": round(health.hp, 1) if health else 0.0,
                "max_hp": round(health.max_hp, 1) if health else 100.0,
                "hunger": round(needs.hunger, 1) if needs else 0.0,
                "thirst": round(needs.thirst, 1) if needs else 0.0,
                "energy": round(needs.energy, 1) if needs else 0.0,
                "fatigue": round(needs.fatigue, 1) if needs else 0.0,
                "body_temperature": round(needs.body_temperature, 1) if needs else 37.0,
                "heat_stress": round(needs.heat_stress, 1) if needs else 0.0,
                "cold_stress": round(needs.cold_stress, 1) if needs else 0.0,
                "emotion": emotion.get_mood_label() if emotion else "-",
                "mood_score": round(emotion.get_mood_score(), 2) if emotion else 0.0,
                "intent": intent.intent.name if intent and intent.intent else "-",
                "action": action.current_action.name if action and action.current_action else "-",
                "diseases": diseases,
                "tribe": tribe_info,
            })

        return {
            "timestamp": time_comp.total_hours if time_comp else 0.0,
            "step": step,
            "humans": humans,
        }
