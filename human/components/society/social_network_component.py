#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from collections import defaultdict

@dataclass
class SocialConnection:
    """社交连接记录"""
    other_entity_id: int
    relationship_type: str = "acquaintance"  # stranger, acquaintance, friend, family, colleague
    strength: float = 10.0  # 关系强度 0-100
    interaction_count: int = 0
    shared_interests: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "entity_id": self.other_entity_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "interaction_count": self.interaction_count,
            "shared_interests": list(self.shared_interests)
        }


@dataclass
class Community:
    """社区信息"""
    name: str
    members: Set[int] = field(default_factory=set)
    activities: List[str] = field(default_factory=list)
    affiliation_level: float = 0.0  # 对该社区的归属感 0-100
    
    def add_member(self, entity_id: int):
        self.members.add(entity_id)
    
    def remove_member(self, entity_id: int):
        self.members.discard(entity_id)
    
    def get_connectivity(self) -> float:
        """计算社区连接度（成员间平均关系强度）"""
        if len(self.members) < 2:
            return 0.0
        connections = []
        members_list = list(self.members)
        for i in range(len(members_list)):
            for j in range(i+1, len(members_list)):
                strength = self._get_connection_strength(members_list[i], members_list[j])
                if strength > 0:
                    connections.append(strength)
        return sum(connections) / len(connections) if connections else 0.0
    
    def _get_connection_strength(self, e1: int, e2: int) -> float:
        """获取两个实体间的连接强度（从社交网络中查询）"""
        # 优先从 relationships 字典中查询双向关系
        if e1 in self.relationships and e2 in self.relationships[e1]:
            return self.relationships[e1][e2].strength
        if e2 in self.relationships and e1 in self.relationships[e2]:
            return self.relationships[e2][e1].strength
        return 0.0


@dataclass
class InterestGroup:
    """兴趣群体"""
    topic: str  # e.g., "gaming", "cooking", "technology"
    members: Set[int] = field(default_factory=set)
    discussion_threads: List[str] = field(default_factory=list)
    
    def get_popularity(self) -> float:
        return len(self.members) / max(1, len(set().union(*[g.members for g in []]))) * 100


class SocialNetworkComponent:
    """
    社交网络组件 - 管理实体间的社会关系
    
    功能：
    - 追踪实体间的人际关系（朋友、家人、同事等）
    - 计算关系强度和亲密度
    - 管理社区归属和参与
    - 维护兴趣群体
    """
    
    def __init__(self):
        # entity_id -> {entity_id: SocialConnection}
        self.relationships: Dict[int, Dict[int, SocialConnection]] = defaultdict(dict)
        self.communities: Dict[str, Community] = {}
        self.interest_groups: Dict[str, InterestGroup] = defaultdict(lambda: InterestGroup(members=set()))
    
    def update_relationship(self, entity_id: int, other_entity_id: int, 
                          relationship_type: str, additional_strength: float = 0):
        """更新两个实体间的关系"""
        # 确保双向关系都有记录
        if entity_id not in self.relationships:
            self.relationships[entity_id] = {}
        if other_entity_id not in self.relationships:
            self.relationships[other_entity_id] = {}
        
        # 更新主关系
        conn = self.relationships[entity_id].get(other_entity_id) or SocialConnection(
            other_entity_id=other_entity_id
        )
        
        # 根据关系类型设置基础强度
        base_strength = {"stranger": 0, "acquaintance": 10, "friend": 30, "family": 60, "colleague": 25}.get(relationship_type, 10)
        conn.strength = min(100, max(0, base_strength + additional_strength))
        conn.relationship_type = relationship_type
        
        # 更新反向关系（通常弱一些）
        reverse_conn = self.relationships[other_entity_id].get(entity_id) or SocialConnection(
            other_entity_id=entity_id
        )
        reverse_strength = min(100, max(0, conn.strength * 0.5 + additional_strength // 2))
        reverse_conn.strength = reverse_strength
        self.relationships[other_entity_id][entity_id] = reverse_conn
        
        return conn.strength
    
    def get_connection_strength(self, entity_id: int, other_entity_id: int) -> float:
        """获取两个实体间的关系强度"""
        if entity_id in self.relationships and other_entity_id in self.relationships[entity_id]:
            return self.relationships[entity_id][other_entity_id].strength
        if other_entity_id in self.relationships and entity_id in self.relationships[other_entity_id]:
            return self.relationships[other_entity_id][entity_id].strength
        return 0.0
    
    def get_connections(self, entity_id: int) -> List[SocialConnection]:
        """获取实体的所有社交连接"""
        return list(self.relationships.get(entity_id, {}).values())
    
    def add_interest(self, entity_id: int, topic: str, interest_name: str):
        """添加或更新实体兴趣"""
        if topic not in self.interest_groups:
            self.interest_groups[topic] = InterestGroup(topic=topic)
        group = self.interest_groups[topic]
        
        if entity_id not in group.members:
            group.members.add(entity_id)
            # 找到共享兴趣的人，增加关系强度
            others_with_same_interest = [m for m in group.members if m != entity_id]
            for other in others_with_same_interest:
                current_strength = self.get_connection_strength(entity_id, other)
                self.update_relationship(
                    entity_id, other,
                    "acquaintance",
                    additional_strength=current_strength + 5
                )
    
    def get_shared_interests(self, entity1_id: int, entity2_id: int) -> List[str]:
        """获取两个实体的共享兴趣"""
        interests_1 = set()
        interests_2 = set()
        
        for topic in self.interest_groups:
            if entity1_id in self.interest_groups[topic].members:
                interests_1.add(topic)
            if entity2_id in self.interest_groups[topic].members:
                interests_2.add(topic)
        
        return list(interests_1 & interests_2)
    
    def get_community_affiliation(self, entity_id: int) -> Dict[str, float]:
        """获取实体对各社区的归属感"""
        result = {}
        for comm_name, comm in self.communities.items():
            if entity_id in comm.members:
                # 归属度基于参与度和关系强度
                affinity = sum(
                    self.get_connection_strength(entity_id, m) 
                    for m in comm.members if m != entity_id
                ) / max(1, len(comm.members) - 1) * 50 + comm.affiliation_level / 2
                result[comm_name] = min(100, affinity)
        return result
    
    def add_community(self, name: str):
        """添加新社区"""
        self.communities[name] = Community(name=name)
    
    def join_community(self, entity_id: int, community_name: str):
        """实体加入社区"""
        if community_name in self.communities:
            self.communities[community_name].add_member(entity_id)
            self.communities[community_name].affiliation_level = min(100, 
                self.communities[community_name].affiliation_level + 10)

    def find_common_friends(self, entity_id: int, target_entity_id: int, k: int = 5) -> List[tuple]:
        """找到共同朋友"""
        friends_1 = set()
        friends_2 = set()
        
        for conn in self.get_connections(entity_id):
            if conn.strength >= 25:  # 只考虑真正的朋友
                friends_1.add(conn.other_entity_id)
        
        for conn in self.get_connections(target_entity_id):
            if conn.strength >= 25:
                friends_2.add(conn.other_entity_id)
        
        common = list(friends_1 & friends_2)
        # 按共同朋友的数量排序（他们有多少个共同朋友）
        for friend in common[:k]:
            count = len(set(self.get_connections(friend)))
            yield (count, friend)

if __name__ == "__main__":
    print("Social Network Component loaded")