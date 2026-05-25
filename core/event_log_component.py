#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:event_log_component.py
@说明:世界事件日志组件
@时间:2026/05/23
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

from core.component import Component


@dataclass
class EventLogComponent(Component):
    """
    世界事件日志组件
    
    挂载到 WorldEntity 上，记录整个模拟过程中的结构化事件。
    支持按类型、时间、实体查询和导出。
    """
    
    # 事件列表，按时间顺序
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # 索引：按类型快速查询
    _index_by_type: Dict[str, List[int]] = field(default_factory=lambda: defaultdict(list), repr=False)
    
    # 索引：按实体快速查询
    _index_by_entity: Dict[int, List[int]] = field(default_factory=lambda: defaultdict(list), repr=False)
    
    # 统计计数器
    counters: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def add_event(self, event_type: str, description: str,
                  time: float = 0.0, step: int = 0,
                  entity_id: Optional[int] = None,
                  target_id: Optional[int] = None,
                  location: Optional[Tuple[float, float]] = None,
                  data: Optional[Dict[str, Any]] = None,
                  severity: str = "info") -> Dict[str, Any]:
        """
        添加一条事件记录
        
        Args:
            event_type: 事件类型标识符
            description: 人类可读描述
            time: 世界时间（总小时）
            step: 模拟步数
            entity_id: 主要相关实体ID
            target_id: 次要/目标实体ID
            location: 发生位置 (x, y)
            data: 额外结构化数据
            severity: 严重程度 (info, warning, critical, milestone)
        
        Returns:
            创建的事件字典
        """
        event = {
            "time": time,
            "step": step,
            "type": event_type,
            "entity_id": entity_id,
            "target_id": target_id,
            "location": location,
            "description": description,
            "data": data or {},
            "severity": severity,
        }
        
        idx = len(self.events)
        self.events.append(event)
        
        # 更新索引
        self._index_by_type[event_type].append(idx)
        if entity_id is not None:
            self._index_by_entity[entity_id].append(idx)
        if target_id is not None:
            self._index_by_entity[target_id].append(idx)
        
        # 更新计数器
        self.counters[event_type] += 1
        if severity in ("critical", "milestone"):
            self.counters[f"severity_{severity}"] += 1
        
        # 限制总事件数，防止内存无限增长
        if len(self.events) > 10000:
            self._prune_old_events()
        
        return event
    
    def get_events(self, event_type: Optional[str] = None,
                   entity_id: Optional[int] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Dict[str, Any]]:
        """
        查询事件
        
        Args:
            event_type: 按类型过滤
            entity_id: 按实体过滤
            limit: 返回最大数量
            offset: 跳过最近 N 条
        
        Returns:
            事件列表（按时间倒序）
        """
        if event_type is not None and entity_id is not None:
            # 交集查询
            type_indices = set(self._index_by_type.get(event_type, []))
            entity_indices = set(self._index_by_entity.get(entity_id, []))
            indices = sorted(type_indices & entity_indices, reverse=True)
        elif event_type is not None:
            indices = sorted(self._index_by_type.get(event_type, []), reverse=True)
        elif entity_id is not None:
            indices = sorted(self._index_by_entity.get(entity_id, []), reverse=True)
        else:
            # 返回最近的事件
            indices = list(range(len(self.events) - 1, -1, -1))
        
        # 应用 offset 和 limit
        indices = indices[offset:offset + limit]
        return [self.events[i] for i in indices]
    
    def get_recent_events(self, n: int = 20) -> List[Dict[str, Any]]:
        """获取最近 N 条事件"""
        return self.events[-n:] if n < len(self.events) else self.events.copy()
    
    def get_event_summary(self) -> Dict[str, int]:
        """获取事件类型统计摘要"""
        return dict(self.counters)
    
    def get_events_by_time_range(self, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """获取时间范围内的事件"""
        return [
            e for e in self.events
            if start_time <= e["time"] <= end_time
        ]
    
    def export_to_list(self) -> List[Dict[str, Any]]:
        """导出所有事件为列表"""
        return self.events.copy()
    
    def _prune_old_events(self):
        """修剪旧事件，保留最近 5000 条，重建索引"""
        keep_count = 5000
        self.events = self.events[-keep_count:]
        
        # 重建索引
        self._index_by_type = defaultdict(list)
        self._index_by_entity = defaultdict(list)
        for idx, event in enumerate(self.events):
            self._index_by_type[event["type"]].append(idx)
            if event["entity_id"] is not None:
                self._index_by_entity[event["entity_id"]].append(idx)
            if event["target_id"] is not None:
                self._index_by_entity[event["target_id"]].append(idx)


class EventLog:
    """
    事件日志静态工具类
    
    提供便捷的全局事件记录接口，所有系统都可以通过此类记录事件。
    """
    
    @staticmethod
    def log(world, event_type: str, description: str,
            entity_id: Optional[int] = None,
            target_id: Optional[int] = None,
            location: Optional[Tuple[float, float]] = None,
            data: Optional[Dict[str, Any]] = None,
            severity: str = "info"):
        """
        记录一条世界事件
        
        Args:
            world: World 实例
            event_type: 事件类型
            description: 描述文本
            entity_id: 主要实体ID
            target_id: 目标实体ID
            location: 位置
            data: 额外数据
            severity: 严重程度
        """
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            # 自动创建并挂载
            log_comp = EventLogComponent()
            world.get_world_entity().add_component(log_comp)
        
        current_time = 0.0
        try:
            time_comp = world.get_time()
            if time_comp:
                current_time = time_comp.total_hours
        except Exception:
            pass
        
        log_comp.add_event(
            event_type=event_type,
            description=description,
            time=current_time,
            step=getattr(world, '_step_count', 0),
            entity_id=entity_id,
            target_id=target_id,
            location=location,
            data=data,
            severity=severity,
        )
    
    @staticmethod
    def get_recent(world, n: int = 20) -> List[Dict[str, Any]]:
        """获取最近事件"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []
        return log_comp.get_recent_events(n)
    
    @staticmethod
    def get_by_type(world, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按类型获取事件"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return []
        return log_comp.get_events(event_type=event_type, limit=limit)
    
    @staticmethod
    def get_summary(world) -> Dict[str, int]:
        """获取事件统计摘要"""
        log_comp = world.get_world_component(EventLogComponent)
        if log_comp is None:
            return {}
        return log_comp.get_event_summary()
