#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_system.py
@说明:社会系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional
from core.system import System
from core.world import World
from human.components.social.social_component_v4 import SocialManagerComponent, RelationshipType, InteractionType, SocialRole
from human.components.basic.human_component import HumanComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class SocialSystem(System):
    """社会系统 v4.0 - 细化版"""
    tick_interval = 10  # 每10帧更新一次

    def __init__(self):
        self.interaction_probability = 0.1  # 互动概率
        self.relationship_formation_probability = 0.05  # 关系形成概率

    def update(self, world: World, dt: float):
        """更新社会系统"""
        # 获取所有人类实体
        humans = []
        for e, (social, human, pos) in world.get_components(
            SocialManagerComponent, HumanComponent, SpaceComponent
        ):
            humans.append((e.id, social, pos))
        
        # 处理社会互动
        self._handle_social_interactions(world, humans)
        
        # 处理关系形成
        self._handle_relationship_formation(world, humans)
        
        # 更新社会网络
        self._update_social_networks(world, humans)

    def _handle_social_interactions(self, world: World, humans: List):
        """处理社会互动"""
        for entity_id, social, pos in humans:
            # 随机进行社会互动
            if random.random() < self.interaction_probability:
                # 查找附近的其他实体
                nearby_entities = self._find_nearby_entities(world, pos, radius=15.0)
                
                if nearby_entities:
                    # 选择一个附近的实体进行互动
                    target_id = random.choice(nearby_entities)
                    
                    # 选择互动类型
                    interaction_type = self._choose_interaction_type(social, target_id)
                    
                    # 进行互动
                    self._perform_interaction(social, target_id, interaction_type)

    def _handle_relationship_formation(self, world: World, humans: List):
        """处理关系形成"""
        for entity_id, social, pos in humans:
            # 随机形成新关系
            if random.random() < self.relationship_formation_probability:
                # 查找附近的其他实体
                nearby_entities = self._find_nearby_entities(world, pos, radius=20.0)
                
                if nearby_entities:
                    # 选择一个附近的实体形成关系
                    target_id = random.choice(nearby_entities)
                    
                    # 检查是否已经有关系
                    existing_relationship = social.get_relationship(target_id)
                    if not existing_relationship:
                        # 选择关系类型
                        relationship_type = self._choose_relationship_type(social, target_id)
                        
                        # 形成关系
                        social.add_relationship(target_id, relationship_type, strength=0.3)
                        logger.info(f"[Social] 实体{entity_id} 与实体{target_id} 形成关系: {relationship_type.name}")

    def _update_social_networks(self, world: World, humans: List):
        """更新社会网络"""
        for entity_id, social, pos in humans:
            # 更新网络中心性
            connections = social.get_social_connections(entity_id)
            if connections:
                # 简化计算：连接数越多，中心性越高
                social.network_centrality = min(1.0, len(connections) / 10.0)
            else:
                social.network_centrality = 0.0

    def _find_nearby_entities(self, world: World, pos: SpaceComponent, radius: float) -> List[int]:
        """查找附近的实体"""
        nearby_entities = []
        
        for e, (human, other_pos) in world.get_components(HumanComponent, SpaceComponent):
            distance = ((pos.x - other_pos.x)**2 + (pos.y - other_pos.y)**2)**0.5
            if distance <= radius:
                nearby_entities.append(e.id)
        
        return nearby_entities

    def _choose_interaction_type(self, social: SocialManagerComponent, target_id: int) -> InteractionType:
        """选择互动类型"""
        # 获取与目标的关系
        relationship = social.get_relationship(target_id)
        
        if relationship:
            # 根据关系类型选择互动类型
            if relationship.relationship_type == RelationshipType.FRIEND:
                return random.choice([InteractionType.CONVERSATION, InteractionType.COOPERATION, InteractionType.HELP])
            elif relationship.relationship_type == RelationshipType.HOSTILE:
                return random.choice([InteractionType.CONFLICT, InteractionType.COMPETITION])
            elif relationship.relationship_type == RelationshipType.ROMANTIC:
                return random.choice([InteractionType.CONVERSATION, InteractionType.CELEBRATION])
            else:
                return random.choice([InteractionType.CONVERSATION, InteractionType.TRADE])
        else:
            # 没有关系，随机选择互动类型
            return random.choice([InteractionType.CONVERSATION, InteractionType.TRADE, InteractionType.COOPERATION])

    def _choose_relationship_type(self, social: SocialManagerComponent, target_id: int) -> RelationshipType:
        """选择关系类型"""
        # 简化实现：随机选择关系类型
        relationship_types = [
            RelationshipType.FRIEND,
            RelationshipType.NEUTRAL,
            RelationshipType.COLLEAGUE
        ]
        
        return random.choice(relationship_types)

    def _perform_interaction(self, social: SocialManagerComponent, target_id: int, interaction_type: InteractionType):
        """进行互动"""
        # 创建互动
        interaction_id = social.add_interaction(interaction_type, [target_id])
        
        # 模拟互动结果
        outcome = random.uniform(0.3, 0.9)  # 随机结果
        
        # 完成互动
        social.complete_interaction(interaction_id, outcome)
        
        logger.debug(f"[Social] 互动: {interaction_type.name}, 结果: {outcome:.2f}")

    def get_social_statistics(self, world: World) -> Dict:
        """获取社会统计"""
        total_entities = 0
        total_relationships = 0
        relationship_types_count = {}
        
        for e, (social, human) in world.get_components(SocialManagerComponent, HumanComponent):
            total_entities += 1
            total_relationships += len(social.relationships)
            
            for relationship in social.relationships.values():
                rel_type = relationship.relationship_type.name
                relationship_types_count[rel_type] = relationship_types_count.get(rel_type, 0) + 1
        
        return {
            'total_entities': total_entities,
            'total_relationships': total_relationships,
            'average_relationships_per_entity': total_relationships / total_entities if total_entities > 0 else 0.0,
            'relationship_types_distribution': relationship_types_count
        }
