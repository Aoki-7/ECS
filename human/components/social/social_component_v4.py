#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:social_component.py
@说明:社会组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum, auto

from core.component import Component


class RelationshipType(Enum):
    """关系类型"""
    FAMILY = auto()         # 亲情
    FRIEND = auto()         # 友情
    ROMANTIC = auto()       # 爱情
    HOSTILE = auto()        # 敌对
    NEUTRAL = auto()        # 中立
    COLLEAGUE = auto()      # 同事
    MENTOR = auto()         # 导师
    STUDENT = auto()        # 学生
    LEADER = auto()         # 领导
    FOLLOWER = auto()       # 追随者


class RelationshipStrength(Enum):
    """关系强度"""
    INTIMATE = auto()       # 亲密
    CLOSE = auto()          # 亲密
    FAMILIAR = auto()       # 熟悉
    ACQUAINTED = auto()     # 认识
    STRANGER = auto()       # 陌生


class SocialRole(Enum):
    """社会角色"""
    PARENT = auto()         # 父母
    CHILD = auto()          # 子女
    SPOUSE = auto()         # 配偶
    SIBLING = auto()        # 兄弟姐妹
    LEADER = auto()         # 领导者
    WORKER = auto()         # 工人
    EXPERT = auto()         # 专家
    NOVICE = auto()         # 新手
    TEACHER = auto()        # 教师
    STUDENT = auto()        # 学生
    HEALER = auto()         # 医者
    WARRIOR = auto()        # 战士


class SocialStatus(Enum):
    """社会地位"""
    WEALTHY = auto()        # 富有
    POOR = auto()           # 贫穷
    NOBLE = auto()          # 贵族
    COMMONER = auto()       # 平民
    LEADER = auto()         # 领导者
    FOLLOWER = auto()       # 追随者
    EXPERT = auto()         # 专家
    NOVICE = auto()         # 新手


class InteractionType(Enum):
    """互动类型"""
    CONVERSATION = auto()   # 交谈
    TRADE = auto()          # 交易
    COOPERATION = auto()    # 合作
    COMPETITION = auto()    # 竞争
    CONFLICT = auto()       # 冲突
    HELP = auto()           # 帮助
    TEACH = auto()          # 教学
    LEARN = auto()          # 学习
    CELEBRATION = auto()    # 庆祝
    MOURNING = auto()       # 哀悼


@dataclass(slots=True)
class Relationship:
    """关系"""
    relationship_id: int
    target_id: int                    # 目标实体ID
    relationship_type: RelationshipType
    strength: float = 0.5             # 关系强度 (0-1)
    trust: float = 0.5                # 信任度 (0-1)
    familiarity: float = 0.0          # 熟悉度 (0-1)
    history: List[Dict] = field(default_factory=list)  # 互动历史
    created_time: float = 0.0         # 创建时间
    last_interaction: float = 0.0     # 最后互动时间
    
    def get_strength_level(self) -> RelationshipStrength:
        """获取关系强度等级"""
        if self.strength < 0.2:
            return RelationshipStrength.STRANGER
        elif self.strength < 0.4:
            return RelationshipStrength.ACQUAINTED
        elif self.strength < 0.6:
            return RelationshipStrength.FAMILIAR
        elif self.strength < 0.8:
            return RelationshipStrength.CLOSE
        else:
            return RelationshipStrength.INTIMATE
    
    def update_strength(self, interaction_type: InteractionType, outcome: float):
        """更新关系强度"""
        # 根据互动类型和结果更新关系强度
        if interaction_type in [InteractionType.HELP, InteractionType.COOPERATION, InteractionType.TEACH]:
            # 正面互动
            self.strength = min(1.0, self.strength + outcome * 0.1)
            self.trust = min(1.0, self.trust + outcome * 0.05)
        elif interaction_type in [InteractionType.CONFLICT, InteractionType.COMPETITION]:
            # 负面互动
            self.strength = max(0.0, self.strength - outcome * 0.1)
            self.trust = max(0.0, self.trust - outcome * 0.05)
        else:
            # 中性互动
            self.familiarity = min(1.0, self.familiarity + outcome * 0.05)
        
        # 记录互动历史
        self.history.append({
            'type': interaction_type.name,
            'outcome': outcome,
            'timestamp': 0.0  # 实际应用中应该使用真实时间戳
        })
        
        # 限制历史记录长度
        if len(self.history) > 50:
            self.history = self.history[-50:]


@dataclass(slots=True)
class SocialRoleInfo:
    """社会角色信息"""
    role: SocialRole
    start_time: float = 0.0           # 开始时间
    end_time: Optional[float] = None  # 结束时间
    performance: float = 0.5          # 表现 (0-1)
    satisfaction: float = 0.5         # 满意度 (0-1)
    responsibilities: List[str] = field(default_factory=list)  # 职责
    
    def is_active(self) -> bool:
        """是否活跃"""
        return self.end_time is None


@dataclass(slots=True)
class SocialStatusInfo:
    """社会地位信息"""
    status: SocialStatus
    level: float = 0.5                # 地位水平 (0-1)
    reputation: float = 0.5           # 声望 (0-1)
    influence: float = 0.5            # 影响力 (0-1)
    wealth: float = 0.5               # 财富 (0-1)
    power: float = 0.5                # 权力 (0-1)
    
    def get_overall_status(self) -> float:
        """获取整体地位"""
        return (self.level + self.reputation + self.influence + 
                self.wealth + self.power) / 5.0


@dataclass(slots=True)
class SocialInteraction:
    """社会互动"""
    interaction_id: int
    interaction_type: InteractionType
    participants: List[int]           # 参与者ID列表
    start_time: float = 0.0           # 开始时间
    duration: float = 0.0             # 持续时间
    outcome: float = 0.5              # 结果 (0-1)
    location: Optional[tuple] = None  # 位置
    
    def is_successful(self) -> bool:
        """是否成功"""
        return self.outcome > 0.5


@dataclass(slots=True)
class SocialManagerComponent(Component):
    """
    社会管理组件 v4.0 - 细化版
    包括关系、角色、地位、互动等细化功能。
    """
    
    # === 关系系统 ===
    relationships: Dict[int, Relationship] = field(default_factory=dict)  # 关系ID -> 关系
    next_relationship_id: int = 0
    relationship_by_entity: Dict[int, List[int]] = field(default_factory=dict)  # 实体ID -> 关系ID列表
    
    # === 社会角色 ===
    current_roles: List[SocialRoleInfo] = field(default_factory=list)  # 当前角色
    role_history: List[SocialRoleInfo] = field(default_factory=list)   # 角色历史
    
    # === 社会地位 ===
    social_status: Dict[SocialStatus, SocialStatusInfo] = field(default_factory=dict)  # 地位类型 -> 地位信息
    overall_status: float = 0.5  # 整体地位 (0-1)
    
    # === 社会互动 ===
    active_interactions: Dict[int, SocialInteraction] = field(default_factory=dict)  # 互动ID -> 互动
    next_interaction_id: int = 0
    interaction_history: List[SocialInteraction] = field(default_factory=list)  # 互动历史
    
    # === 社会网络 ===
    social_network: Dict[int, Set[int]] = field(default_factory=dict)  # 实体ID -> 连接的实体ID集合
    network_centrality: float = 0.5  # 网络中心性 (0-1)
    
    # === 社会规范 ===
    followed_norms: Set[str] = field(default_factory=set)  # 遵循的规范
    violated_norms: Set[str] = field(default_factory=set)  # 违反的规范
    
    def add_relationship(self, target_id: int, relationship_type: RelationshipType, 
                        strength: float = 0.5) -> int:
        """添加关系"""
        relationship_id = self.next_relationship_id
        self.next_relationship_id += 1
        
        relationship = Relationship(
            relationship_id=relationship_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength
        )
        
        self.relationships[relationship_id] = relationship
        
        # 更新实体关系映射
        if target_id not in self.relationship_by_entity:
            self.relationship_by_entity[target_id] = []
        self.relationship_by_entity[target_id].append(relationship_id)
        
        return relationship_id
    
    def get_relationship(self, target_id: int) -> Optional[Relationship]:
        """获取与指定实体的关系"""
        if target_id in self.relationship_by_entity:
            relationship_ids = self.relationship_by_entity[target_id]
            if relationship_ids:
                # 返回最强的关系
                relationships = [self.relationships[rid] for rid in relationship_ids]
                return max(relationships, key=lambda r: r.strength)
        return None
    
    def update_relationship(self, target_id: int, interaction_type: InteractionType, outcome: float):
        """更新关系"""
        relationship = self.get_relationship(target_id)
        if relationship:
            relationship.update_strength(interaction_type, outcome)
    
    def add_role(self, role: SocialRole, responsibilities: List[str] = None) -> SocialRoleInfo:
        """添加角色"""
        role_info = SocialRoleInfo(
            role=role,
            responsibilities=responsibilities or []
        )
        
        self.current_roles.append(role_info)
        return role_info
    
    def remove_role(self, role: SocialRole):
        """移除角色"""
        for role_info in self.current_roles:
            if role_info.role == role:
                role_info.end_time = 0.0  # 实际应用中应该使用真实时间戳
                self.role_history.append(role_info)
                self.current_roles.remove(role_info)
                break
    
    def has_role(self, role: SocialRole) -> bool:
        """是否有指定角色"""
        return any(role_info.role == role for role_info in self.current_roles)
    
    def add_status(self, status: SocialStatus, level: float = 0.5) -> SocialStatusInfo:
        """添加社会地位"""
        status_info = SocialStatusInfo(
            status=status,
            level=level
        )
        
        self.social_status[status] = status_info
        self._update_overall_status()
        return status_info
    
    def _update_overall_status(self):
        """更新整体地位"""
        if self.social_status:
            total_status = sum(info.get_overall_status() for info in self.social_status.values())
            self.overall_status = total_status / len(self.social_status)
    
    def add_interaction(self, interaction_type: InteractionType, participants: List[int]) -> int:
        """添加社会互动"""
        interaction_id = self.next_interaction_id
        self.next_interaction_id += 1
        
        interaction = SocialInteraction(
            interaction_id=interaction_id,
            interaction_type=interaction_type,
            participants=participants
        )
        
        self.active_interactions[interaction_id] = interaction
        
        # 更新社会网络
        for participant in participants:
            if participant not in self.social_network:
                self.social_network[participant] = set()
            
            for other_participant in participants:
                if other_participant != participant:
                    self.social_network[participant].add(other_participant)
        
        return interaction_id
    
    def complete_interaction(self, interaction_id: int, outcome: float):
        """完成社会互动"""
        if interaction_id in self.active_interactions:
            interaction = self.active_interactions[interaction_id]
            interaction.outcome = outcome
            
            # 移动到历史记录
            self.interaction_history.append(interaction)
            del self.active_interactions[interaction_id]
            
            # 更新参与者的关系
            for participant in interaction.participants:
                for other_participant in interaction.participants:
                    if other_participant != participant:
                        self.update_relationship(other_participant, interaction.interaction_type, outcome)
    
    def get_social_connections(self, entity_id: int) -> Set[int]:
        """获取社会连接"""
        return self.social_network.get(entity_id, set())
    
    def get_social_influence(self) -> float:
        """获取社会影响力"""
        # 基于网络中心性和社会地位
        return (self.network_centrality + self.overall_status) / 2.0
    
    def get_social_summary(self) -> Dict:
        """获取社会摘要"""
        return {
            'relationships_count': len(self.relationships),
            'current_roles': [role_info.role.name for role_info in self.current_roles],
            'overall_status': self.overall_status,
            'social_influence': self.get_social_influence(),
            'active_interactions': len(self.active_interactions),
            'network_size': len(self.social_network)
        }
    
    # === 兼容属性 (Compatibility Layer for v2 API) ===
    @property
    def relations(self) -> Dict[int, str]:
        """兼容v2: 返回 {target_id: relationship_type_name}"""
        return {rel.target_id: rel.relationship_type.name for rel in self.relationships.values()}
    
    @relations.setter
    def relations(self, value: Dict[int, str]):
        """兼容v2: 从 {target_id: relationship_type_name} 同步到新版关系"""
        # 清除旧关系，重新建立
        self.relationships.clear()
        self.relationship_by_entity.clear()
        self.next_relationship_id = 0
        for target_id, rel_type_name in value.items():
            try:
                rel_type = RelationshipType[rel_type_name.upper()]
            except KeyError:
                rel_type = RelationshipType.NEUTRAL
            self.add_relationship(target_id, rel_type, strength=0.5)
    
    @property
    def relation_strength(self) -> Dict[int, float]:
        """兼容v2: 返回 {target_id: strength}"""
        result = {}
        for rel in self.relationships.values():
            if rel.target_id in result:
                result[rel.target_id] = max(result[rel.target_id], rel.strength)
            else:
                result[rel.target_id] = rel.strength
        return result
    
    @relation_strength.setter
    def relation_strength(self, value: Dict[int, float]):
        """兼容v2: 从 {target_id: strength} 同步到新版关系"""
        for target_id, strength in value.items():
            relationship = self.get_relationship(target_id)
            if relationship:
                relationship.strength = strength
            else:
                self.add_relationship(target_id, RelationshipType.NEUTRAL, strength=strength)
    
    @property
    def conflicts(self) -> List[Dict]:
        """兼容v2: 返回冲突记录（从敌对关系历史和互动中提取）"""
        conflict_records = []
        for rel in self.relationships.values():
            if rel.relationship_type == RelationshipType.HOSTILE:
                conflict_records.append({
                    'target_id': rel.target_id,
                    'reason': 'hostile_relationship',
                    'strength': rel.strength
                })
        return conflict_records
    
    @conflicts.setter
    def conflicts(self, value: List[Dict]):
        """兼容v2: 添加冲突记录，创建敌对关系"""
        for record in value:
            target_id = record.get('target_id')
            if target_id is not None:
                relationship = self.get_relationship(target_id)
                if relationship:
                    relationship.relationship_type = RelationshipType.HOSTILE
                else:
                    self.add_relationship(target_id, RelationshipType.HOSTILE, strength=0.3)
    
    @property
    def is_socializing(self) -> bool:
        """兼容v2: 是否有活跃的互动"""
        return len(self.active_interactions) > 0
    
    @is_socializing.setter
    def is_socializing(self, value: bool):
        """兼容v2: 设置社交状态（仅记录，不改变活跃互动）"""
        pass
    
    @property
    def current_interaction_partner(self) -> Optional[int]:
        """兼容v2: 获取当前互动伙伴（取第一个活跃互动的其他参与者）"""
        if self.active_interactions:
            interaction = next(iter(self.active_interactions.values()))
            # 假设当前实体是0号参与者，返回其他参与者
            for participant in interaction.participants:
                if participant != 0:  # 0 是占位符，实际需要当前实体ID
                    return participant
            return interaction.participants[0] if interaction.participants else None
        return None
    
    @current_interaction_partner.setter
    def current_interaction_partner(self, value: Optional[int]):
        """兼容v2: 设置当前互动伙伴（仅记录）"""
        pass
    
    @property
    def total_interactions(self) -> int:
        """兼容v2: 总互动次数"""
        return len(self.interaction_history)
    
    @total_interactions.setter
    def total_interactions(self, value: int):
        """兼容v2: 只读统计，设置无效"""
        pass
    
    @property
    def successful_interactions(self) -> int:
        """兼容v2: 成功互动次数（outcome > 0.5）"""
        return sum(1 for interaction in self.interaction_history if interaction.outcome > 0.5)
    
    @successful_interactions.setter
    def successful_interactions(self, value: int):
        """兼容v2: 只读统计，设置无效"""
        pass
    
    @property
    def failed_interactions(self) -> int:
        """兼容v2: 失败互动次数（outcome <= 0.5）"""
        return sum(1 for interaction in self.interaction_history if interaction.outcome <= 0.5)
    
    @failed_interactions.setter
    def failed_interactions(self, value: int):
        """兼容v2: 只读统计，设置无效"""
        pass
