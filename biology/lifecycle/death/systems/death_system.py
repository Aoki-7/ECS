#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeathSystem — 统一死亡执行系统

职责：
    1. 扫描所有挂载了 PendingDeathComponent 的实体
    2. 执行统一的死亡流程（Alive → Dead）
    3. 记录死亡原因、死亡时间
    4. 触发死亡事件日志
    5. 将实体移出空间索引（但保留尸体实体，供 CorpseSystem 处理）
    6. 移除不需要保留的组件，保留尸体相关组件

设计原则：
    - DeathSystem 不判断死亡原因，只执行
    - 死亡原因由 PendingDeathComponent 携带
    - 多个 PendingDeath 同时存在时，按 priority 取最高优先级的原因
    - 尸体实体保留在世界中，由 CorpseSystem 后续处理
"""

import logging
from typing import Optional

from core.system import System
from core.world import World

from biology.lifecycle.death.components.pending_death_component import PendingDeathComponent
from biology.lifecycle.death.components.dead_tag_component import DeadTagComponent
from biology.lifecycle.death.components.death_reason_component import DeathReasonComponent
from biology.lifecycle.death.components.death_time_component import DeathTimeComponent
from biology.lifecycle.corpse.components.corpse_component import CorpseComponent

from space.space_system import SpaceSystem
from space.space_component import SpaceComponent
from identity.name_component import NameComponent

logger = logging.getLogger(__name__)


class DeathSystem(System):
    tick_interval = 1
    """
    统一死亡执行系统。

    处理流程：
        PendingDeath → 选择最高优先级原因 → 挂载 DeadTag/DeathReason/DeathTime
        → 记录日志 → 从空间索引移除 → 保留尸体实体
    """

    def update(self, world: World, dt: float = 1.0) -> None:
        pending_deaths = list(world.get_components(PendingDeathComponent))
        if not pending_deaths:
            return

        time_component = world.get_time()
        world_time = time_component.total_hours if time_component else 0.0
        world_time_display = self._format_time(time_component)

        space_system: Optional[SpaceSystem] = world.get_system(SpaceSystem)

        for entity, (pending,) in pending_deaths:
            if not world.has_entity(entity):
                continue

            # 如果已经死亡，跳过（防止重复处理）
            if world.get_component(entity, DeadTagComponent) is not None:
                world.remove_component(entity, PendingDeathComponent)
                continue

            # 收集该实体上的所有 PendingDeath（可能有多个系统同时标记）
            all_pendings = self._collect_all_pending_deaths(entity, world)
            if not all_pendings:
                continue

            # 按优先级排序，取最高优先级的作为主要原因
            all_pendings.sort(key=lambda p: p.priority, reverse=True)
            primary = all_pendings[0]

            # 1. 挂载死亡标记组件（processed=False，由 DeathEventSystem 广播后设为 True）
            world.add_component(entity, DeadTagComponent(processed=False))
            world.add_component(entity, DeathReasonComponent(
                primary_reason=primary.reason,
                all_reasons=[p.reason for p in all_pendings],
                primary_source=primary.source_system
            ))
            world.add_component(entity, DeathTimeComponent(
                world_time_hours=world_time,
                world_time_display=world_time_display
            ))

            # 2. 获取实体名称用于日志
            entity_name = self._get_entity_name(entity, world)

            # 3. 记录死亡日志
            reason_str = primary.reason
            source_str = primary.source_system
            details = primary.details
            logger.info(f"[Death] {entity_name} died of {reason_str} (source: {source_str}) {details}")

            # 4. 从空间索引移除（尸体不再参与空间查询）
            if space_system is not None:
                space_system.remove_entity(entity)

            # 5. 挂载尸体组件（保留实体供 CorpseSystem 处理）
            corpse = self._build_corpse_component(entity, world)
            world.add_component(entity, corpse)

            # 6. 清理不再需要的基础组件（保留尸体相关组件）
            self._strip_living_components(entity, world)

            # 7. 移除所有 PendingDeath 标记
            for p in all_pendings:
                world.remove_component(entity, type(p))

            # 8. 触发死亡事件（供 EventLogSystem 或后续系统订阅）
            self._emit_death_event(entity, reason_str, world_time, world)

    def _collect_all_pending_deaths(self, entity, world: World) -> list:
        """收集实体上所有 PendingDeathComponent 实例（支持多个）"""
        # 由于 world.get_components 每 tick 只返回一个，我们需要直接查 entity 的组件
        # 但当前 ECS 一个实体同类型组件只能有一个，所以这里直接返回单个
        pending = world.get_component(entity, PendingDeathComponent)
        return [pending] if pending is not None else []

    def _get_entity_name(self, entity, world: World) -> str:
        """获取实体名称，用于日志输出"""
        name_comp = world.get_component(entity, NameComponent)
        if name_comp is not None and name_comp.name:
            return f"{name_comp.name}(E{entity.id})"
        return f"E{entity.id}"

    def _format_time(self, time_component) -> str:
        """格式化世界时间"""
        if time_component is None:
            return "unknown"
        try:
            year = int(getattr(time_component, 'year', 0))
            day = int(getattr(time_component, 'day_of_year', 0))
            hour = int(getattr(time_component, 'hour', 0))
            return f"Year {year}, Day {day}, {hour:02d}:00"
        except (AttributeError, TypeError, ValueError):
            return "unknown"

    def _build_corpse_component(self, entity, world: World) -> CorpseComponent:
        """根据死亡实体构建尸体组件"""
        name_comp = world.get_component(entity, NameComponent)
        original_name = name_comp.name if name_comp else f"E{entity.id}"

        # 推断原始类型
        from human.components.basic.human_component import HumanComponent
        original_type = "human" if world.get_component(entity, HumanComponent) else "creature"

        return CorpseComponent(
            original_entity_id=entity.id,
            original_name=original_name,
            decay_progress=0.0,
            decay_rate=0.01,
            is_looted=False,
            original_type=original_type
        )

    def _strip_living_components(self, entity, world: World) -> None:
        """移除生命期组件，将实体转换为尸体"""
        # 这些组件列表可以根据需要扩展
        living_component_types = [
            # 生理与需求
            "biology.components.physiology_needs_component.PhysiologyNeedsComponent",
            "biology.components.energy_component.EnergyComponent",
            "biology.components.health_status_component.HealthStatusComponent",
            "biology.components.immune_component.ImmuneComponent",
            "biology.components.nutrient_component.NutrientComponent",
            # 认知与行为
            "human.components.cognitive.intent_component.IntentComponent",
            "human.components.cognitive.task_component.TaskComponent",
            "human.components.cognitive.memory_component.MemoryComponent",
            "core.components.action_component.ActionComponent",
            "core.components.search_component.SearchComponent",
            "core.components.vision_component.VisionComponent",
            "core.components.velocity_component.VelocityComponent",
            # 社交
            "human.components.social.relationship_component.RelationshipComponent",
            # 经济与装备
            "human.components.economic.inventory.inventory_component.InventoryComponent",
            "equipment.components.ownership_component.OwnershipComponent",
        ]

        for type_path in living_component_types:
            try:
                comp_class = self._import_component(type_path)
                if comp_class is not None and world.get_component(entity, comp_class) is not None:
                    world.remove_component(entity, comp_class)
            except (ImportError, AttributeError):
                pass  # 组件可能不存在，静默跳过

    def _import_component(self, dotted_path: str):
        """动态导入组件类"""
        try:
            module_path, class_name = dotted_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError, ValueError):
            return None

    def _emit_death_event(self, entity, reason: str, world_time: float, world: World) -> None:
        """发射死亡事件，供其他系统订阅"""
        try:
            from core.components.event_log_component import EventLog
            EventLog.log(
                world,
                event_type="death",
                message=f"E{entity.id} died of {reason}",
                entities=[entity.id],
                data={"death_reason": reason, "world_time": world_time}
            )
        except (ImportError, AttributeError):
            pass  # EventLog 可能不可用，静默跳过
