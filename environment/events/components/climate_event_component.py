#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
气候事件组件 v4.16.0
定义各种极端气候事件的属性与参数
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from core.component import Component
from typing import Tuple


class ClimateEventType(Enum):
    """气候事件类型"""
    DROUGHT = auto()        # 干旱
    FLOOD = auto()          # 洪水
    COLD_WAVE = auto()      # 寒潮
    HEAT_WAVE = auto()      # 热浪
    WILDFIRE = auto()       # 野火
    HAILSTORM = auto()      # 冰雹
    TORNADO = auto()        # 龙卷风
    HURRICANE = auto()      # 飓风/台风


class EventSeverity(Enum):
    """事件强度等级"""
    LIGHT = auto()      # 轻度
    MODERATE = auto()   # 中度
    SEVERE = auto()     # 重度
    EXTREME = auto()    # 极端


@dataclass(slots=True)
class ClimateEventComponent(Component):
    """
    气候事件组件
    每个气候事件实体挂载此组件，存储事件的完整信息
    """
    
    # 基础属性
    event_type: ClimateEventType
    severity: EventSeverity = EventSeverity.MODERATE
    start_time: float = 0.0  # 事件开始时间（世界小时）
    duration: float = 72.0   # 事件持续时间（小时），默认3天
    remaining_time: float = field(init=False)  # 剩余持续时间
    
    # 影响范围
    center: Tuple[float, float] = (0.0, 0.0)  # 事件中心坐标
    radius: float = 50.0  # 影响半径（米）
    intensity_falloff: float = 0.5  # 强度随距离衰减系数，0=无衰减，1=线性衰减到0
    
    # 强度参数
    intensity: float = 0.5  # 事件强度 0-1，由 severity 自动计算
    is_active: bool = True  # 事件是否正在生效
    
    def __post_init__(self):
        """初始化事件参数"""
        # 根据严重度设置基础强度
        severity_intensity_map = {
            EventSeverity.LIGHT: 0.3,
            EventSeverity.MODERATE: 0.6,
            EventSeverity.SEVERE: 0.85,
            EventSeverity.EXTREME: 1.0,
        }
        self.intensity = severity_intensity_map[self.severity]
        self.remaining_time = self.duration
    
    def get_intensity_at_position(self, x: float, y: float) -> float:
        """计算指定位置的事件强度"""
        if not self.is_active:
            return 0.0
        
        # 计算距离
        dx = x - self.center[0]
        dy = y - self.center[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance >= self.radius:
            return 0.0
        
        # 强度随距离衰减
        distance_factor = 1.0 - (distance / self.radius) * self.intensity_falloff
        return max(0.0, self.intensity * distance_factor)
    
    def update(self, dt: float) -> bool:
        """更新事件剩余时间，返回是否还在生效"""
        if not self.is_active:
            return False
        
        self.remaining_time -= dt
        if self.remaining_time <= 0:
            self.is_active = False
            return False
        
        # 强度随时间衰减，最后1/3时间强度开始下降
        if self.remaining_time < self.duration / 3:
            time_factor = self.remaining_time / (self.duration / 3)
            self.intensity *= time_factor
        
        return True
    
    def get_effect_description(self) -> str:
        """获取事件效果描述"""
        severity_desc = {
            EventSeverity.LIGHT: "轻度",
            EventSeverity.MODERATE: "中度",
            EventSeverity.SEVERE: "重度",
            EventSeverity.EXTREME: "极端",
        }
        
        type_desc = {
            ClimateEventType.DROUGHT: "干旱",
            ClimateEventType.FLOOD: "洪水",
            ClimateEventType.COLD_WAVE: "寒潮",
            ClimateEventType.HEAT_WAVE: "热浪",
            ClimateEventType.WILDFIRE: "野火",
            ClimateEventType.HAILSTORM: "冰雹",
            ClimateEventType.TORNADO: "龙卷风",
            ClimateEventType.HURRICANE: "飓风",
        }
        
        return f"{severity_desc[self.severity]}{type_desc[self.event_type]}，强度{self.intensity:.1f}，剩余时间{self.remaining_time:.1f}小时，影响半径{self.radius:.0f}米"