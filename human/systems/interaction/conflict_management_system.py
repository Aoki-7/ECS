#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
冲突管理系统 - 处理人际间的矛盾、竞争与协作
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto


class ConflictType(Enum):
    RESOURCE = auto()         # 资源争夺
    VALUES = auto()           # 价值观冲突
    RELATIONAL = auto()       # 关系问题
    TASK = auto()             # 任务/目标冲突
    MISCOMMUNICATION = auto()   # 沟通误解


class ResolutionStrategy(Enum):
    AVOIDANCE = auto()        # 回避
    COMPROMISE = auto()       # 妥协
    COMPETITION = auto()      # 竞争
    COLLABORATION = auto()    # 协作
    ACCOMMODATION = auto()    # 迁就


@dataclass
class ConflictInstance:
    """冲突实例记录"""
    id: str = field(default_factory=lambda: f"conflict_{len(ConflictInstance._instances) + 1}")
    conflict_type: Optional[ConflictType] = None
    parties: List[int] = field(default_factory=list)
    description: str = ""
    intensity: float = 0.0     # 冲突强度 0-100
    current_phase: str = "active"  # active, resolution, resolved
    resolution_method: Optional[str] = None
    outcome: str = ""
    
    _instances = []

    def add_party(self, entity_id: int):
        if entity_id not in self.parties:
            self.parties.append(entity_id)
    
    def get_participant_count(self) -> int:
        return len(self.parties)


class RelationshipQuality(Enum):
    STRAINED = "strained"     # 紧张
    DAMAGED = "damaged"       # 受损
    STABLE = "stable"         # 稳定
    IMPROVED = "improved"     # 改善


class ConflictManagementSystem:
    """
    冲突管理系统 - 管理和调解实体间的人际冲突
    
    功能：
    - 检测潜在的冲突情境
    - 分析冲突类型和原因
    - 提供解决策略建议
    - 跟踪冲突解决结果
    - 评估关系影响
    """
    
    def __init__(self):
        self.active_conflicts: List[ConflictInstance] = []
        self.resolved_conflicts: List[ConflictInstance] = []
        self.resolution_history: List[Dict] = []
        
        # 实体间关系状态
        self.relationship_quality: Dict[int, RelationshipQuality] = {}
    
    def detect_contradiction(self, entity1: int, entity2: int) -> Optional[Dict]:
        """
        检测两个实体间的潜在矛盾
        
        Args:
            entity1: 实体ID 1
            entity2: 实体ID 2
            
        Returns:
            矛盾分析报告或 None
        """
        # 简单的检测逻辑示例
        contradictions = []
        
        # TODO: 检查各种矛盾类型：
        # - 目标冲突（目标重叠但互斥）
        # - 资源竞争（需要同一资源）
        # - 关系紧张（关系强度低或负面）
        # - 价值观差异
        
        if contradictions:
            return {
                "contradiction_type": ",".join(contradictions),
                "severity": len(contradictions) * 20,
                "entities": [entity1, entity2]
            }
        return None
    
    def add_conflict(self, conflict_type: ConflictType, 
                    description: str, 
                    entities: List[int]) -> ConflictInstance:
        """添加/记录一个冲突事件"""
        conflict = ConflictInstance(
            conflict_type=conflict_type,
            description=description,
            parties=[e for e in entities if e] or [],
            intensity=self._calculate_intensity(entities, description)
        )
        self.active_conflicts.append(conflict)
        return conflict
    
    def _calculate_intensity(self, entities: List[int], desc: str) -> float:
        """计算冲突强度"""
        # 考虑参与人数和描述关键词
        intensity = len(entities) * 25
        
        keywords = ["严重", "激烈", "致命", "暴力", "永久"]
        if any(kw in desc for kw in keywords):
            intensity += 30
        
        return min(100, intensity)
    
    def propose_resolution(self, conflict: ConflictInstance) -> List[Tuple[ResolutionStrategy, str]]:
        """
        为冲突推荐解决策略
        
        Returns:
            [(策略, 说明), ...] 列表
        """
        suggestions = []
        
        if conflict.conflict_type == ConflictType.RESOURCE:
            suggestions.append((ResolutionStrategy.COMPROMISE, 
                             "双方各退一步，共享资源"))
            suggestions.append((ResolutionStrategy.COLLABORATION,
                             "合作开发新方案，扩大资源"))
        
        elif conflict.conflict_type == ConflictType.VALUES:
            suggestions.append((ResolutionStrategy.ACCOMMODATION,
                             "尊重差异，各自坚持自己的价值观"))
            suggestions.append((ResolutionStrategy.DIALOGUE,
                             "深入沟通，寻找共同基础"))
        
        elif conflict.conflict_type == ConflictType.RELATIONAL:
            suggestions.append((ResolutionStrategy.COLLABORATION,
                             "重建信任，修复关系"))
            suggestions.append((ResolutionStrategy.ACCOMMODATION,
                             "一方做出让步，缓和关系"))
        
        else:
            suggestions.append((ResolutionStrategy.DIALOGUE,
                             "坦诚沟通，解决问题"))
        
        return suggestions
    
    def resolve_conflict(self, conflict: ConflictInstance, 
                        resolution_method: ResolutionStrategy) -> Dict:
        """
        解决冲突
        
        Returns:
            解决结果报告
        """
        # 更新冲突状态
        conflict.current_phase = "resolution"
        conflict.resolution_method = resolution_method.value
        
        # 模拟解决过程
        result = {
            "conflict_id": conflict.id,
            "method_used": resolution_method,
            "outcome": self._simulate_outcome(resolution_method),
            "parties_involved": conflict.parties.copy(),
            "relationships_affected": conflict.parties.copy()
        }
        
        # 更新关系状态
        for party in conflict.parties:
            if party in self.relationship_quality:
                self.relationship_quality[party] = self._adjust_relationship(
                    self.relationship_quality[party], 
                    conflict,
                    resolution_method
                )
            
            if party not in self.relationship_quality:
                self.relationship_quality[party] = RelationshipQuality.STABLE
        
        # 记录解决结果
        conflict.current_phase = "resolved"
        conflict.outcome = result["outcome"]
        self.resolved_conflicts.append(conflict)
        self.resolution_history.append(result)
        
        return result
    
    def _simulate_outcome(self, method: ResolutionStrategy) -> str:
        """模拟冲突解决结果"""
        outcomes = {
            ResolutionStrategy.AVOIDANCE: "暂时搁置问题，避免正面冲突。关系维持现状。",
            ResolutionStrategy.COMPROMISE: "双方各让一步，达成妥协方案。关系略有改善。",
            ResolutionStrategy.COMPETITION: "一方取得优势，但可能造成关系紧张。",
            ResolutionStrategy.COLLABORATION: "共同努力寻找双赢方案。关系显著改善。",
            ResolutionStrategy.ACCOMMODATION: "一方让步，另一方满意。依赖程度增加。"
        }
        return outcomes.get(method, "问题解决。")
    
    def _adjust_relationship(self, quality: RelationshipQuality, 
                           conflict: ConflictInstance,
                           resolution: ResolutionStrategy) -> RelationshipQuality:
        """调整关系质量"""
        # 简化实现：始终返回 STABLE 或 IMPROVED
        if resolution == ResolutionStrategy.COLLABORATION:
            return RelationshipQuality.IMPROVED
        elif resolution in [ResolutionStrategy.COMPROMISE, ResolutionStrategy.ACCOMMODATION]:
            return RelationshipQuality.STABLE
        else:
            return quality
    
    def get_relationship_status(self, entity_id: int) -> Dict[int, str]:
        """获取实体与其他实体的关系状态"""
        result = {}
        for other_id, quality in self.relationship_quality.items():
            if other_id != self.entity_id:
                result[other_id] = quality.value
        return result
    
    def get_conflict_risk(self, entity1: int, entity2: int) -> float:
        """计算两个实体间发生冲突的概率"""
        # 简单模型：关系质量越低，风险越高
        risk_sum = 0
        if entity1 != entity2:
            for e in [entity1, entity2]:
                quality = self.relationship_quality.get(e, RelationshipQuality.STABLE)
                if quality == RelationshipQuality.DAMAGED:
                    risk_sum += 30
                elif quality == RelationshipQuality.STRAINED:
                    risk_sum += 15
        
        return min(100, risk_sum + random.uniform(0, 20))

    def update(self, world, dt: float = 0.0):
        """系统更新（冲突管理系统暂不执行每帧逻辑）"""
        pass


if __name__ == "__main__":
    import logging
    logging.getLogger(__name__).debug("冲突管理系统已加载")