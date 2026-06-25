#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NeedsSystem — 统一需求管理系统

P1 任务：从 PhysiologyNeedsComponent 拆分出独立需求组件，
统一处理饥饿、口渴、睡眠、温度、社交等需求。

设计原则：
- 每个需求独立 Component（HungerComponent, ThirstComponent 等）
- NeedsSystem 统一读取各需求组件，计算优先级
- 向后兼容：PhysiologyNeedsComponent 保留但标记为 deprecated
"""

import logging
from typing import List, Optional, Tuple

from core.system import System
from core.world import World
from core.entity import Entity

logger = logging.getLogger(__name__)


class NeedsSystem(System):
    """
    统一需求管理系统
    
    职责：
        1. 读取各实体的需求组件（Hunger, Thirst, Sleep, Temperature, Social）
        2. 计算需求优先级队列
        3. 更新需求衰减/恢复
        4. 触发需求紧急事件
    
    需求优先级算法：
        - 每个需求 0-100，数值越高越紧急
        - 饥饿 > 口渴 > 睡眠 > 温度 > 社交（默认权重）
        - 可配置权重和阈值
    """

    tick_interval = 1  # 每帧执行（需求变化快）

    # 默认需求权重（越高越优先）
    DEFAULT_WEIGHTS = {
        'hunger': 1.5,
        'thirst': 1.8,      # 口渴比饥饿更紧急
        'sleep': 1.2,
        'temperature': 1.0,
        'social': 0.5,
    }

    # 紧急阈值
    CRITICAL_THRESHOLD = 80.0
    WARNING_THRESHOLD = 50.0

    def __init__(self, weights: dict = None):
        super().__init__()
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._critical_callbacks = []  # 紧急需求回调

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新所有实体的需求状态"""
        for entity in self._get_entities_with_needs(world):
            needs = self._collect_needs(world, entity)
            if not needs:
                continue

            # 计算优先级
            priorities = self._calculate_priorities(needs)
            
            # 更新需求衰减
            self._decay_needs(world, entity, needs, dt)
            
            # 检查紧急状态
            self._check_critical_needs(world, entity, needs, priorities)

    def _get_entities_with_needs(self, world: World) -> List[Entity]:
        """获取所有有需求组件的实体"""
        # 优先使用新组件，回退到旧 PhysiologyNeedsComponent
        entities = []
        
        # 尝试新组件
        try:
            from biology.components.hunger_component import HungerComponent
            for entity, _ in world.get_components(HungerComponent):
                if entity not in entities:
                    entities.append(entity)
        except ImportError:
            pass
            
        try:
            from biology.components.thirst_component import ThirstComponent
            for entity, _ in world.get_components(ThirstComponent):
                if entity not in entities:
                    entities.append(entity)
        except ImportError:
            pass
            
        try:
            from biology.components.sleep_component import SleepComponent
            for entity, _ in world.get_components(SleepComponent):
                if entity not in entities:
                    entities.append(entity)
        except ImportError:
            pass
            
        try:
            from biology.components.temperature_component import TemperatureComponent
            for entity, _ in world.get_components(TemperatureComponent):
                if entity not in entities:
                    entities.append(entity)
        except ImportError:
            pass
            
        try:
            from biology.components.social_needs_component import SocialNeedsComponent
            for entity, _ in world.get_components(SocialNeedsComponent):
                if entity not in entities:
                    entities.append(entity)
        except ImportError:
            pass
        
        # 回退到旧组件
        if not entities:
            try:
                from biology.components.physiology_needs_component import PhysiologyNeedsComponent
                for entity, _ in world.get_components(PhysiologyNeedsComponent):
                    entities.append(entity)
            except ImportError:
                pass
        
        return entities

    def _collect_needs(self, world: World, entity: Entity) -> dict:
        """收集实体的所有需求值"""
        needs = {}
        
        # 尝试新组件
        try:
            from biology.components.hunger_component import HungerComponent
            comp = world.get_component(entity, HungerComponent)
            if comp:
                needs['hunger'] = comp.value
        except ImportError:
            pass
            
        try:
            from biology.components.thirst_component import ThirstComponent
            comp = world.get_component(entity, ThirstComponent)
            if comp:
                needs['thirst'] = comp.value
        except ImportError:
            pass
            
        try:
            from biology.components.sleep_component import SleepComponent
            comp = world.get_component(entity, SleepComponent)
            if comp:
                needs['sleep'] = comp.value
        except ImportError:
            pass
            
        try:
            from biology.components.temperature_component import TemperatureComponent
            comp = world.get_component(entity, TemperatureComponent)
            if comp:
                needs['temperature'] = abs(comp.discomfort)  # 温度偏离舒适度
        except ImportError:
            pass
            
        try:
            from biology.components.social_needs_component import SocialNeedsComponent
            comp = world.get_component(entity, SocialNeedsComponent)
            if comp:
                needs['social'] = comp.loneliness
        except ImportError:
            pass
        
        # 回退到旧 PhysiologyNeedsComponent
        if not needs:
            try:
                from biology.components.physiology_needs_component import PhysiologyNeedsComponent
                comp = world.get_component(entity, PhysiologyNeedsComponent)
                if comp:
                    needs['hunger'] = getattr(comp, 'hunger', 0.0) * 100
                    needs['thirst'] = getattr(comp, 'thirst', 0.0) * 100
                    needs['sleep'] = getattr(comp, 'sleepiness', 0.0) * 100
                    needs['fatigue'] = getattr(comp, 'fatigue', 0.0) * 100
                    needs['social'] = (100 - getattr(comp, 'social', 50.0)) * 2
            except ImportError:
                pass
        
        return needs

    def _calculate_priorities(self, needs: dict) -> List[Tuple[str, float]]:
        """计算需求优先级队列"""
        scored = []
        for need_type, value in needs.items():
            weight = self.weights.get(need_type, 1.0)
            score = value * weight
            scored.append((need_type, score))
        
        # 按分数降序排列
        scored.sort(key=lambda x: -x[1])
        return scored

    def _decay_needs(self, world: World, entity: Entity, needs: dict, dt: float) -> None:
        """更新需求衰减（由各自 System 处理，这里仅做协调）"""
        # 需求衰减由专门的 HungerSystem, ThirstSystem 等处理
        # NeedsSystem 仅负责优先级计算和协调
        pass

    def _check_critical_needs(self, world: World, entity: Entity, needs: dict, priorities: List[Tuple[str, float]]) -> None:
        """检查紧急需求并触发事件"""
        if not priorities:
            return
            
        top_need, top_score = priorities[0]
        
        # 紧急状态
        if top_score >= self.CRITICAL_THRESHOLD:
            logger.warning(f"[NeedsSystem] 实体 {entity.id} {top_need} 紧急！({top_score:.1f})")
            self._trigger_critical_event(world, entity, top_need, top_score)
        # 警告状态
        elif top_score >= self.WARNING_THRESHOLD:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[NeedsSystem] 实体 {entity.id} {top_need} 警告({top_score:.1f})")

    def _trigger_critical_event(self, world: World, entity: Entity, need_type: str, score: float) -> None:
        """触发紧急需求事件"""
        try:
            from core.event_bus import EventBus
            EventBus.get_instance().publish(
                f"critical_{need_type}",
                {
                    "entity_id": entity.id,
                    "need_type": need_type,
                    "score": score,
                },
                source="NeedsSystem",
            )
        except Exception:
            pass

    def get_top_need(self, world: World, entity: Entity) -> Optional[Tuple[str, float]]:
        """获取实体最紧急的需求"""
        needs = self._collect_needs(world, entity)
        priorities = self._calculate_priorities(needs)
        if priorities:
            return priorities[0]
        return None

    def set_weight(self, need_type: str, weight: float) -> None:
        """设置需求权重"""
        self.weights[need_type] = weight

    def register_critical_callback(self, callback) -> None:
        """注册紧急需求回调"""
        self._critical_callbacks.append(callback)
