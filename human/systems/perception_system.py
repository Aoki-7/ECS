#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:perception_system.py
@说明:感知系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional, Tuple
from core.system import System
from core.world import World
from human.components.perception.perception_component_v4 import PerceptionComponent, VisionType, HearingType
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class PerceptionSystem(System):
    """感知系统 v4.0 - 细化版"""
    tick_interval = 5  # 每5帧更新一次

    def __init__(self):
        self.perception_update_probability = 0.3  # 感知更新概率

    def update(self, world: World, dt: float):
        """更新感知系统"""
        # 获取所有人类实体
        humans = []
        for e, (perception, human, pos) in world.get_components(
            PerceptionComponent, HumanComponent, SpaceComponent
        ):
            humans.append((e.id, perception, pos))
        
        # 更新感知
        for entity_id, perception, pos in humans:
            # 更新空间地图
            perception.update_spatial_map((pos.x, pos.y), perception.vision_range)
            
            # 更新视觉
            self._update_vision(world, perception, pos)
            
            # 更新听觉
            self._update_hearing(world, perception, pos)
            
            # 更新感知
            perception.update_perception(dt)
            
            # 处理威胁和机会
            self._handle_threats_and_opportunities(perception, entity_id)

    def _update_vision(self, world: World, perception: PerceptionComponent, pos: SpaceComponent):
        """更新视觉"""
        # 获取可见实体
        visible_entities = []
        
        for e, (human, other_pos) in world.get_components(HumanComponent, SpaceComponent):
            if e.id == perception.attention_focus:  # 跳过自己
                continue
            
            # 计算距离
            distance = ((pos.x - other_pos.x)**2 + (pos.y - other_pos.y)**2)**0.5
            
            # 检查是否在视觉范围内
            if distance <= perception.vision_range:
                # 生成实体信息
                entity_info = (
                    e.id,  # 实体ID
                    (other_pos.x, other_pos.y),  # 位置
                    1.0,  # 大小
                    "brown",  # 颜色
                    "human",  # 形状
                    (0.0, 0.0)  # 移动
                )
                
                visible_entities.append(entity_info)
        
        # 更新视觉
        perception.update_vision(visible_entities)

    def _update_hearing(self, world: World, perception: PerceptionComponent, pos: SpaceComponent):
        """更新听觉"""
        # 生成环境声音
        sounds = []
        
        # 风声
        wind_intensity = random.uniform(0.1, 0.3)
        sounds.append(("wind", wind_intensity, random.uniform(0, 360), random.uniform(5, 15), 500))
        
        # 动物声音
        if random.random() < 0.3:  # 30%概率听到动物声音
            animal_intensity = random.uniform(0.2, 0.5)
            sounds.append(("animal", animal_intensity, random.uniform(0, 360), random.uniform(3, 10), 800))
        
        # 人类声音
        if random.random() < 0.2:  # 20%概率听到人类声音
            human_intensity = random.uniform(0.3, 0.7)
            sounds.append(("human", human_intensity, random.uniform(0, 360), random.uniform(2, 8), 300))
        
        # 更新听觉
        perception.update_hearing(sounds)

    def _handle_threats_and_opportunities(self, perception: PerceptionComponent, entity_id: int):
        """处理威胁和机会"""
        # 评估威胁
        threat_level = perception.assess_threats()
        
        # 评估机会
        opportunity_level = perception.assess_opportunities()
        
        # 如果威胁水平高，记录日志
        if threat_level > 0.7:
            nearest_threat = perception.get_nearest_threat()
            if nearest_threat:
                logger.debug(f"[Perception] 实体{entity_id} 检测到威胁: 实体{nearest_threat.entity_id}, 距离: {nearest_threat.distance:.2f}")
        
        # 如果机会水平高，记录日志
        if opportunity_level > 0.6:
            nearest_resource = perception.get_nearest_resource()
            if nearest_resource:
                logger.debug(f"[Perception] 实体{entity_id} 发现资源: 位置{nearest_resource}")

    def get_perception_statistics(self, world: World) -> Dict:
        """获取感知统计"""
        total_entities = 0
        total_visible_entities = 0
        total_audible_sounds = 0
        average_threat_level = 0.0
        average_opportunity_level = 0.0
        
        for e, (perception, human) in world.get_components(PerceptionComponent, HumanComponent):
            total_entities += 1
            total_visible_entities += len(perception.visible_entities)
            total_audible_sounds += len(perception.audible_sounds)
            average_threat_level += perception.threat_level
            average_opportunity_level += perception.opportunity_level
        
        if total_entities > 0:
            average_threat_level /= total_entities
            average_opportunity_level /= total_entities
        
        return {
            'total_entities': total_entities,
            'total_visible_entities': total_visible_entities,
            'total_audible_sounds': total_audible_sounds,
            'average_threat_level': average_threat_level,
            'average_opportunity_level': average_opportunity_level
        }
