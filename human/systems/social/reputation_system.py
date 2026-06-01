#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
ReputationSystem - 声誉管理系统

职责：
- 管理 ReputationComponent / FameComponent / SocialStandingComponent 的业务逻辑
- 声誉动态调整、称号生成、谣言传播

原 reputation_component.py 中的业务逻辑已迁移至此。
"""

from typing import Dict, List, Optional
from core.system import System
from core.world import World
from core.entity import Entity

from human.components.society.reputation_component import (
    ReputationComponent, FameComponent, SocialStandingComponent
)


class ReputationSystem(System):
    tick_interval = 5  # 每5帧执行一次
    """
    声誉管理系统

    处理实体在社区中的评价动态变化。
    """

    priority = 35  # 在人类核心系统之后

    # ── ReputationComponent 业务逻辑 ──

    @staticmethod
    def adjust_reputation(world: World, entity: Entity, delta: float, aspect: str = "general") -> None:
        """调整声誉"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return

        if aspect == "general":
            rep.reputation = max(-50, min(150, rep.reputation + delta))
        elif aspect in rep.specialties:
            rep.specialties[aspect] = max(0, min(100, rep.specialties[aspect] + delta))

        # 专项声誉反哺整体声誉
        for specialty, level in rep.specialties.items():
            if level >= 80 and rep.reputation < 70:
                rep.reputation = min(100, rep.reputation + (level - 70) * 0.3)

    @staticmethod
    def get_status(world: World, entity: Entity) -> str:
        """根据声誉值映射到社会地位"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return "unknown"

        r = rep.reputation
        if r >= 80:
            return "respected"
        elif r >= 50:
            return "known"
        elif r >= 20:
            return "observed"
        elif r < -30:
            return "feared"
        elif r < 0:
            return "disliked"
        else:
            return "commoner"

    @staticmethod
    def add_knowledge(world: World, entity: Entity, area: str, level: int) -> None:
        """添加专长知识"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return

        if area not in rep.specialties:
            rep.specialties[area] = 0
        rep.specialties[area] = min(100, rep.specialties[area] + level)

        if level >= 80 and area not in rep.known_for:
            rep.known_for.append(area)

    @staticmethod
    def get_reputation_summary(world: World, entity: Entity) -> Dict:
        """获取声誉摘要"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return {}

        return {
            "overall": round(max(0, min(100, rep.reputation)), 1),
            "status": ReputationSystem.get_status(world, entity),
            "specialties": dict(rep.specialties),
            "known_for": list(rep.known_for),
            "social_status": rep.social_status,
        }

    @staticmethod
    def spread_rumor(world: World, entity: Entity, content: str, source: str = "unknown") -> str:
        """传播谣言"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return "No reputation component"

        rumor_id = len(rep.rumors) + 1
        rumor = {
            "id": rumor_id,
            "content": content,
            "source": source,
            "spread_level": 0,
            "believers": []
        }
        rep.rumors.append(rumor)
        return f"Rumor ID {rumor_id} created"

    @staticmethod
    def get_trusted_entities(world: World, entity: Entity) -> List[str]:
        """获取值得信任的实体列表"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return ["none_trusted"]

        r = max(0, min(100, rep.reputation))
        if r >= 50:
            return ["friendly_npc1", "friendly_npc2"]
        elif r >= 20:
            return ["stranger"]
        else:
            return ["none_trusted"]

    @staticmethod
    def is_honorable(world: World, entity: Entity) -> bool:
        """判断是否是荣耀之身"""
        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return False

        return (rep.reputation >= 75 and
                any(v >= 80 for v in rep.specialties.values()))

    @staticmethod
    def get_title(world: World, entity: Entity) -> str:
        """根据声誉生成称号"""
        if ReputationSystem.is_honorable(world, entity):
            return "Honored Citizen"

        rep = world.get_component(entity, ReputationComponent)
        if rep is None:
            return "Local Person"

        r = max(0, min(100, rep.reputation))
        if r >= 50:
            areas = list(rep.specialties.items())
            if any(v >= 70 for _, v in areas):
                specialty = [k for k, v in areas if v >= 70][0]
                return f"Known {specialty}"
        elif r < 0:
            return "Notorious Figure"

        return "Local Person"

    # ── FameComponent 业务逻辑 ──

    @staticmethod
    def update_popularity(world: World, entity: Entity, region: str, delta: float) -> None:
        """更新区域知名度"""
        fame = world.get_component(entity, FameComponent)
        if fame is None:
            return

        if region not in fame.regional_popularity:
            fame.regional_popularity[region] = 0
        fame.regional_popularity[region] = max(0, min(100, fame.regional_popularity[region] + delta))

    @staticmethod
    def get_popularity_map(world: World, entity: Entity) -> Dict[str, float]:
        """获取区域知名度分布"""
        fame = world.get_component(entity, FameComponent)
        if fame is None:
            return {}
        return dict(fame.regional_popularity)

    # ── SocialStandingComponent 业务逻辑 ──

    @staticmethod
    def calculate_class(world: World, entity: Entity) -> str:
        """根据属性计算职业等级"""
        standing = world.get_component(entity, SocialStandingComponent)
        if standing is None:
            return "unknown"

        if standing.class_rank >= 80:
            return "nobility"
        elif standing.class_rank >= 60:
            return "middle_class"
        elif standing.class_rank >= 40:
            return "working_class"
        else:
            return "lower_class"

    @staticmethod
    def get_standing_summary(world: World, entity: Entity) -> Dict:
        """获取社会地位摘要"""
        standing = world.get_component(entity, SocialStandingComponent)
        if standing is None:
            return {}

        return {
            "class": ReputationSystem.calculate_class(entity),
            "wealth": standing.wealth_tier,
            "politics": round(standing.political_influence, 1),
            "origin": standing.family_status,
        }

    # ── System update（预留：声誉自然衰减等） ──

    def update(self, world: World, dt: float = 1.0):
        super().update(world, dt)
        # 当前无每 tick 必须执行的逻辑
        # 未来可添加：谣言自然传播、声誉衰减等
        pass
