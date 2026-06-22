#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeathArchiveSystem — 死亡档案系统

职责：
1. 扫描所有已死亡实体（DeadTagComponent），将信息归档到 DeathArchiveComponent
2. 持续同步 CorpseComponent 的腐烂进度
3. 提供查询 API：按实体、死因、时间范围、实体类型检索死亡记录

设计原则：
    - 纯管理与检索，无超自然逻辑（无转生、业力、灵魂状态等）
    - 不创建新实体，只读取现有死亡实体的组件数据
    - 所有状态变更源于对现有组件的只读观察
"""

import logging
from typing import List, Optional, Dict, Any

from core.system import System
from core.world import World
from identity.event_log_system import EventLog

from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
from biology.lifecycle.death.components.death_reason_component import DeathReasonComponent
from biology.lifecycle.death.components.death_time_component import DeathTimeComponent
from biology.lifecycle.corpse.components.corpse_component import CorpseComponent
from death_archive.components.death_archive_component import DeathArchiveComponent
from death_archive.components.record_entry import RecordEntry

logger = logging.getLogger(__name__)


class DeathArchiveSystem(System):
    """
    死亡档案系统

    priority = 55（在 DeathSystem/DeathEventSystem/CorpseSystem 之后，
                  在 TransformationSystem/CivilizationSystem 之前）
    tick_interval = 5（每 5 帧同步一次腐烂进度，归档无需高频执行）
    """

    priority = 55
    tick_interval = 5

    def on_add(self, world: World):
        """系统注册时自动挂载 DeathArchiveComponent 到 world_entity"""
        if world.get_world_component(DeathArchiveComponent) is None:
            world.get_world_entity().add_component(DeathArchiveComponent())

    def on_remove(self, world: World):
        """系统移除时清理 DeathArchiveComponent"""
        we = world.get_world_entity()
        if we:
            comp = world.get_component(we, DeathArchiveComponent)
            if comp:
                we.remove_component(DeathArchiveComponent)

    def update(self, world: World, dt: float = 1.0) -> None:
        """主更新入口：归档新死亡 + 同步腐烂进度"""
        super().update(world, dt)
        self._archive_new_deaths(world)
        self._update_decay_status(world)

    # ── 阶段 A：归档新死亡实体 ──

    def _archive_new_deaths(self, world: World):
        """扫描死亡实体，将未归档的实体加入死亡档案"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return

        from human.components.basic.human_component import HumanComponent
        from plant.components.plant_component import PlantComponent
        from animal.components.animal_component import AnimalComponent
        from identity.name_component import NameComponent

        for entity, (dead_tag,) in world.get_components(DeadTagComponent):
            # 跳过已归档的实体
            if entity.id in archive.index_by_entity:
                continue

            # 读取死亡原因和时间
            reason_comp = world.get_component(entity, DeathReasonComponent)
            time_comp = world.get_component(entity, DeathTimeComponent)

            death_reason = reason_comp.primary_reason if reason_comp else "unknown"
            death_time = time_comp.world_time_hours if time_comp else 0.0
            death_time_display = time_comp.world_time_display if time_comp else "unknown"

            # 读取实体名称
            name_comp = world.get_component(entity, NameComponent)
            entity_name = name_comp.name if name_comp else f"E{entity.id}"

            # 推断实体类型
            entity_type = "creature"
            if world.get_component(entity, HumanComponent) is not None:
                entity_type = "human"
            elif world.get_component(entity, PlantComponent) is not None:
                entity_type = "plant"
            elif world.get_component(entity, AnimalComponent) is not None:
                entity_type = "animal"

            # 读取尸体腐烂进度（若已挂载 CorpseComponent）
            corpse_comp = world.get_component(entity, CorpseComponent)
            decay_progress = corpse_comp.decay_progress if corpse_comp else 0.0
            is_decayed = decay_progress >= 1.0

            # 写入档案
            record = RecordEntry(
                entity_id=entity.id,
                entity_name=entity_name,
                entity_type=entity_type,
                death_reason=death_reason,
                death_time=death_time,
                death_time_display=death_time_display,
                decay_progress=decay_progress,
                is_decayed=is_decayed,
            )
            archive.records.append(record)
            archive.index_by_entity[entity.id] = len(archive.records) - 1
            archive.total_deaths += 1
            archive.counters[death_reason] = archive.counters.get(death_reason, 0) + 1

            logger.info(f"[DeathArchive] 归档: {entity_name} (原因: {death_reason}, 类型: {entity_type})")
            EventLog.log(
                world,
                event_type="death_archived",
                description=f"{entity_name} 的死亡记录已归档 (原因: {death_reason})",
                entity_id=entity.id,
                data={"death_reason": death_reason, "entity_type": entity_type}
            )

    # ── 阶段 B：同步腐烂进度 ──

    def _update_decay_status(self, world: World):
        """读取 CorpseComponent，同步所有档案的腐烂进度"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return

        for entity, (corpse,) in world.get_components(CorpseComponent):
            if entity.id not in archive.index_by_entity:
                continue

            idx = archive.index_by_entity[entity.id]
            if idx >= len(archive.records):
                continue

            record = archive.records[idx]
            new_decay = corpse.decay_progress
            new_is_decayed = new_decay >= 1.0

            # 只在数据变化时更新（避免无意义的 _replace）
            if record.decay_progress != new_decay or record.is_decayed != new_is_decayed:
                archive.records[idx] = record._replace(
                    decay_progress=new_decay,
                    is_decayed=new_is_decayed
                )
                if new_is_decayed and not record.is_decayed:
                    archive.decayed_count += 1
                    logger.debug(f"[DeathArchive] 尸体完全腐烂: {record.entity_name}")

    # ── 查询 API ──

    def get_record(self, world: World, entity_id: int) -> Optional[RecordEntry]:
        """按实体 ID 获取单条死亡档案"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None or entity_id not in archive.index_by_entity:
            return None
        idx = archive.index_by_entity[entity_id]
        if idx < len(archive.records):
            return archive.records[idx]
        return None

    def get_records_by_reason(self, world: World, reason: str) -> List[RecordEntry]:
        """按死亡原因获取所有档案"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return []
        return [r for r in archive.records if r.death_reason == reason]

    def get_records_by_time_range(
        self, world: World, start_time: float, end_time: float
    ) -> List[RecordEntry]:
        """按死亡时间范围获取档案（含边界）"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return []
        return [r for r in archive.records if start_time <= r.death_time <= end_time]

    def get_records_by_type(self, world: World, entity_type: str) -> List[RecordEntry]:
        """按实体类型获取所有档案"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return []
        return [r for r in archive.records if r.entity_type == entity_type]

    def get_recent_records(self, world: World, n: int = 20) -> List[RecordEntry]:
        """获取最近 N 条死亡档案（按死亡时间倒序）"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return []
        return list(reversed(archive.records[-n:]))

    def get_statistics(self, world: World) -> Dict[str, Any]:
        """获取死亡统计摘要"""
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return {}
        return {
            "total_deaths": archive.total_deaths,
            "decayed_count": archive.decayed_count,
            "pending_decay": archive.total_deaths - archive.decayed_count,
            "counters": dict(archive.counters),
        }

    def get_recent_deaths_from_event_log(self, world: World, n: int = 20) -> List[Dict[str, Any]]:
        """
        从 EventLogSystem 查询最近死亡事件（与本地档案交叉验证）。
        这是 EventLog 查询 API 的首个生产调用者，用于验证事件日志集成。
        """
        from identity.event_log_system import EventLogSystem
        event_system = world.get_system(EventLogSystem)
        if event_system is None:
            return []
        # 查询最近 N 条 death_archived 类型的事件
        return event_system.get_events(world, event_type="death_archived", limit=n)

    def cross_check_with_event_log(self, world: World) -> Dict[str, Any]:
        """
        交叉验证：比较本地档案与 EventLog 中的死亡事件数量。
        用于调试和确认两个系统的数据一致性。
        """
        archive = world.get_world_component(DeathArchiveComponent)
        if archive is None:
            return {"archive_count": 0, "event_log_count": 0, "matched": False}

        from identity.event_log_system import EventLogSystem
        event_system = world.get_system(EventLogSystem)
        if event_system is None:
            return {"archive_count": archive.total_deaths, "event_log_count": 0, "matched": False}

        events = event_system.get_events(world, event_type="death_archived", limit=10000)
        return {
            "archive_count": archive.total_deaths,
            "event_log_count": len(events),
            "matched": archive.total_deaths == len(events),
        }
