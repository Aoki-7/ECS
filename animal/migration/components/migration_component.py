#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:migration_component.py
@说明:迁徙组件 v2.0 - 纯数据版
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component

@dataclass(slots=True)
class MigrationComponent(Component):
    """
    迁徙组件 - 纯数据版
    存储迁徙信息。
    """
    # 迁徙状态
    is_migrating: bool = False
    migration_direction: str = "north"
    
    # 目标位置
    destination_x: Optional[float] = None
    destination_y: Optional[float] = None
    
    # 迁徙进度
    distance_traveled: float = 0.0
    total_distance: float = 0.0
    
    # 触发条件
    spring_trigger: Dict = field(default_factory=dict)
    autumn_trigger: Dict = field(default_factory=dict)
    
    # 历史记录
    migration_history: List[Dict] = field(default_factory=list)
    
    # 兼容性字段（兼容旧测试）
    is_migratory: bool = False
    migration_status: str = "resident"
    energy_reserve: float = 1.0
    temperature_threshold_depart: float = 10.0
    day_length_trigger: float = 12.0
    temperature_threshold_arrive: float = 15.0
    breeding_ground: tuple = None
    wintering_ground: tuple = None
    migration_speed: float = 1.0
    migration_route: List = field(default_factory=list)
    migration_season: str = "spring"
    migration_reason: str = "temperature"
    migration_start_time: float = 0.0
    migration_end_time: float = 0.0
    migration_duration: float = 0.0
    migration_distance: float = 0.0
    migration_success: bool = False
    migration_failure_reason: str = ""
    current_target: tuple = None
    migration_progress: float = 0.0
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            'is_migratory': self.is_migratory,
            'migration_status': self.migration_status,
            'energy_reserve': self.energy_reserve,
            'breeding_ground': self.breeding_ground,
            'wintering_ground': self.wintering_ground,
            'temperature_threshold_depart': self.temperature_threshold_depart,
            'day_length_trigger': self.day_length_trigger,
            'temperature_threshold_arrive': self.temperature_threshold_arrive,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MigrationComponent':
        """反序列化"""
        comp = cls()
        for key, value in data.items():
            if hasattr(comp, key):
                setattr(comp, key, value)
        return comp
