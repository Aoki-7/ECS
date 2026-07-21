#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:perception_component.py
@说明:感知组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto

from core.component import Component


class VisionType(Enum):
    """视觉类型"""
    NORMAL = auto()         # 正常视觉
    NIGHT = auto()          # 夜视
    INFRARED = auto()       # 红外视觉
    ULTRAVIOLET = auto()    # 紫外视觉


class HearingType(Enum):
    """听觉类型"""
    NORMAL = auto()         # 正常听觉
    ENHANCED = auto()       # 增强听觉
    ECHOLOCATION = auto()   # 回声定位


class SpatialAwareness(Enum):
    """空间意识"""
    BASIC = auto()          # 基本空间意识
    ADVANCED = auto()       # 高级空间意识
    EXPERT = auto()         # 专家空间意识


@dataclass(slots=True)
class VisualInfo:
    """视觉信息"""
    entity_id: int
    position: Tuple[float, float]
    distance: float
    size: float
    color: str
    shape: str
    movement: Tuple[float, float]  # 移动方向和速度
    
    def is_threat(self) -> bool:
        """是否是威胁"""
        # 简化实现：根据大小和移动速度判断
        return self.size > 1.0 and (abs(self.movement[0]) > 0.5 or abs(self.movement[1]) > 0.5)


@dataclass(slots=True)
class AuditoryInfo:
    """听觉信息"""
    sound_type: str
    intensity: float        # 强度 (0-1)
    direction: float        # 方向（角度）
    distance: float         # 距离
    frequency: float        # 频率
    
    def is_danger(self) -> bool:
        """是否是危险信号"""
        # 简化实现：根据强度和频率判断
        return self.intensity > 0.7 and self.frequency > 1000


@dataclass(slots=True)
class SpatialMap:
    """空间地图"""
    center: Tuple[float, float]
    radius: float
    obstacles: List[Tuple[float, float]] = field(default_factory=list)  # 障碍物
    resources: List[Tuple[float, float]] = field(default_factory=list)  # 资源
    entities: List[Tuple[float, float]] = field(default_factory=list)   # 实体
    
    def is_safe(self, position: Tuple[float, float]) -> bool:
        """检查位置是否安全"""
        # 简化实现：检查是否在障碍物附近
        for obstacle in self.obstacles:
            distance = ((position[0] - obstacle[0])**2 + (position[1] - obstacle[1])**2)**0.5
            if distance < 2.0:
                return False
        return True


@dataclass(slots=True)
class PerceptionComponent(Component):
    """
    感知组件 v4.0 - 细化版
    包括视觉、听觉、空间认知等细化功能。
    """
    
    # === 视觉系统 ===
    vision_type: VisionType = VisionType.NORMAL  # 视觉类型
    vision_range: float = 20.0  # 视觉范围
    vision_acuity: float = 0.8  # 视觉敏锐度 (0-1)
    visible_entities: Dict[int, VisualInfo] = field(default_factory=dict)  # 可见实体
    
    # === 听觉系统 ===
    hearing_type: HearingType = HearingType.NORMAL  # 听觉类型
    hearing_range: float = 15.0  # 听觉范围
    hearing_acuity: float = 0.7  # 听觉敏锐度 (0-1)
    audible_sounds: List[AuditoryInfo] = field(default_factory=list)  # 可听声音
    
    # === 空间认知 ===
    spatial_awareness: SpatialAwareness = SpatialAwareness.BASIC  # 空间意识
    spatial_memory: Dict[str, SpatialMap] = field(default_factory=dict)  # 空间记忆
    current_map: Optional[SpatialMap] = None  # 当前地图
    
    # === 感知整合 ===
    attention_focus: Optional[int] = None  # 注意力焦点（实体ID）
    threat_level: float = 0.0  # 威胁水平 (0-1)
    opportunity_level: float = 0.0  # 机会水平 (0-1)
    
    # === 感知历史 ===
    perception_history: List[Dict] = field(default_factory=list)  # 感知历史
    max_history_length: int = 100
    
    def update_vision(self, entities: List[Tuple[int, Tuple[float, float], float, str, str, Tuple[float, float]]]):
        """更新视觉"""
        self.visible_entities.clear()
        
        for entity_id, position, size, color, shape, movement in entities:
            # 计算距离
            distance = ((position[0] - self.current_map.center[0])**2 + 
                       (position[1] - self.current_map.center[1])**2)**0.5 if self.current_map else 0.0
            
            # 检查是否在视觉范围内
            if distance <= self.vision_range:
                visual_info = VisualInfo(
                    entity_id=entity_id,
                    position=position,
                    distance=distance,
                    size=size,
                    color=color,
                    shape=shape,
                    movement=movement
                )
                
                self.visible_entities[entity_id] = visual_info
    
    def update_hearing(self, sounds: List[Tuple[str, float, float, float, float]]):
        """更新听觉"""
        self.audible_sounds.clear()
        
        for sound_type, intensity, direction, distance, frequency in sounds:
            # 检查是否在听觉范围内
            if distance <= self.hearing_range:
                auditory_info = AuditoryInfo(
                    sound_type=sound_type,
                    intensity=intensity,
                    direction=direction,
                    distance=distance,
                    frequency=frequency
                )
                
                self.audible_sounds.append(auditory_info)
    
    def update_spatial_map(self, center: Tuple[float, float], radius: float):
        """更新空间地图"""
        if not self.current_map or self.current_map.center != center:
            self.current_map = SpatialMap(center=center, radius=radius)
    
    def add_obstacle(self, position: Tuple[float, float]):
        """添加障碍物"""
        if self.current_map:
            self.current_map.obstacles.append(position)
    
    def add_resource(self, position: Tuple[float, float]):
        """添加资源"""
        if self.current_map:
            self.current_map.resources.append(position)
    
    def add_entity(self, position: Tuple[float, float]):
        """添加实体"""
        if self.current_map:
            self.current_map.entities.append(position)
    
    def assess_threats(self) -> float:
        """评估威胁"""
        threat_count = 0
        
        # 视觉威胁
        for visual_info in self.visible_entities.values():
            if visual_info.is_threat():
                threat_count += 1
        
        # 听觉威胁
        for auditory_info in self.audible_sounds:
            if auditory_info.is_danger():
                threat_count += 1
        
        # 计算威胁水平
        total_entities = len(self.visible_entities) + len(self.audible_sounds)
        if total_entities > 0:
            self.threat_level = min(1.0, threat_count / total_entities)
        else:
            self.threat_level = 0.0
        
        return self.threat_level
    
    def assess_opportunities(self) -> float:
        """评估机会"""
        opportunity_count = 0
        
        # 资源机会
        if self.current_map:
            opportunity_count += len(self.current_map.resources)
        
        # 实体机会（非威胁实体）
        for visual_info in self.visible_entities.values():
            if not visual_info.is_threat():
                opportunity_count += 1
        
        # 计算机会水平
        total_opportunities = opportunity_count
        if total_opportunities > 0:
            self.opportunity_level = min(1.0, total_opportunities / 10.0)  # 假设最多10个机会
        else:
            self.opportunity_level = 0.0
        
        return self.opportunity_level
    
    def get_nearest_threat(self) -> Optional[VisualInfo]:
        """获取最近的威胁"""
        threats = [info for info in self.visible_entities.values() if info.is_threat()]
        if threats:
            return min(threats, key=lambda x: x.distance)
        return None
    
    def get_nearest_resource(self) -> Optional[Tuple[float, float]]:
        """获取最近的资源"""
        if self.current_map and self.current_map.resources:
            center = self.current_map.center
            return min(self.current_map.resources, 
                      key=lambda x: ((x[0] - center[0])**2 + (x[1] - center[1])**2)**0.5)
        return None
    
    def get_safe_position(self, current_position: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """获取安全位置"""
        if not self.current_map:
            return None
        
        # 简化实现：返回远离威胁的位置
        threats = [info for info in self.visible_entities.values() if info.is_threat()]
        if not threats:
            return current_position
        
        # 计算远离所有威胁的方向
        avoid_x, avoid_y = 0.0, 0.0
        for threat in threats:
            dx = current_position[0] - threat.position[0]
            dy = current_position[1] - threat.position[1]
            distance = (dx**2 + dy**2)**0.5
            if distance > 0:
                avoid_x += dx / distance
                avoid_y += dy / distance
        
        # 归一化
        length = (avoid_x**2 + avoid_y**2)**0.5
        if length > 0:
            avoid_x /= length
            avoid_y /= length
        
        # 返回安全位置
        safe_distance = 5.0
        return (current_position[0] + avoid_x * safe_distance,
                current_position[1] + avoid_y * safe_distance)
    
    def update_perception(self, dt: float):
        """更新感知"""
        # 评估威胁和机会
        self.assess_threats()
        self.assess_opportunities()
        
        # 记录感知历史
        perception_record = {
            'timestamp': 0.0,  # 实际应用中应该使用真实时间戳
            'visible_entities': len(self.visible_entities),
            'audible_sounds': len(self.audible_sounds),
            'threat_level': self.threat_level,
            'opportunity_level': self.opportunity_level
        }
        
        self.perception_history.append(perception_record)
        
        # 限制历史记录长度
        if len(self.perception_history) > self.max_history_length:
            self.perception_history = self.perception_history[-self.max_history_length:]
    
    def get_perception_summary(self) -> Dict:
        """获取感知摘要"""
        return {
            'vision_type': self.vision_type.name,
            'vision_range': self.vision_range,
            'visible_entities': len(self.visible_entities),
            'hearing_type': self.hearing_type.name,
            'hearing_range': self.hearing_range,
            'audible_sounds': len(self.audible_sounds),
            'spatial_awareness': self.spatial_awareness.name,
            'threat_level': self.threat_level,
            'opportunity_level': self.opportunity_level,
            'attention_focus': self.attention_focus
        }
