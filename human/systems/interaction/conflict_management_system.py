#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
冲突管理系统 - 处理人际间的矛盾、竞争与协作
"""

from typing import Dict, List, Optional, Tuple
import random

from core.system import System
from core.world import World

from human.components.social.conflict_component import ConflictComponent
from human.components.social.relationship_component import RelationshipComponent
from human.components.cognitive.personality_component import PersonalityComponent
from human.components.cognitive.emotion_component import EmotionComponent
from human.components.action.action_component import ActionComponent, ActionType, ActionStatus

from human.systems.interaction.conflict_models import (
    ConflictType,
    ResolutionStrategy,
    RelationshipQuality,
    ConflictInstance,
)


class ConflictManagementSystem(System):
    """
    冲突管理系统 - 管理和调解实体间的人际冲突（ECS 版）
    
    功能：
    - 检测潜在的冲突情境
    - 分析冲突类型和原因
    - 提供解决策略建议
    - 跟踪冲突解决结果
    - 评估关系影响
    """
    
    def __init__(self):
        super().__init__()
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
        
        # NOTE: 矛盾检测规则待扩展，当前已实现框架：
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

    def update(self, world: World, dt: float = 0.0):
        """系统更新：检测负面关系并自动创建/解决冲突"""
        for entity, (relation, personality, emotion, action, conflict_comp) in world.get_components(
            RelationshipComponent, PersonalityComponent, EmotionComponent,
            ActionComponent, ConflictComponent
        ):
            relation: RelationshipComponent
            personality: PersonalityComponent
            emotion: EmotionComponent
            action: ActionComponent
            conflict_comp: ConflictComponent

            # 清理已解决的冲突
            for c in list(conflict_comp.active_conflicts):
                if c.get("intensity", 0) <= 0:
                    conflict_comp.remove_conflict(c["conflict_id"])

            # 检测负面关系
            if not hasattr(relation, 'relations') or not relation.relations:
                continue

            for other_id, score in list(relation.relations.items()):
                if score >= -20:
                    continue  # 关系不够差，不构成冲突

                # 检查是否已有活跃冲突
                existing = any(
                    c.get("opponent_id") == other_id
                    for c in conflict_comp.active_conflicts
                )
                if existing:
                    continue

                # 创建新冲突
                intensity = min(100, abs(score) * 0.5 + random.uniform(0, 10))
                strategy = self._choose_strategy(personality, emotion)

                conflict = {
                    "conflict_id": f"conflict_{entity.id}_{other_id}",
                    "type": ConflictType.RELATIONAL.name,
                    "opponent_id": other_id,
                    "intensity": intensity,
                    "strategy": strategy.name if strategy else "AVOIDANCE",
                }
                conflict_comp.add_conflict(conflict)

                # 冲突强度高时触发攻击
                if intensity > 60 and action.current_action in (ActionType.IDLE, ActionType.WAIT):
                    action.current_action = ActionType.ATTACK
                    action.status = ActionStatus.RUNNING
                    action.target_entity = other_id

                # 创建全局冲突记录
                self.add_conflict(
                    ConflictType.RELATIONAL,
                    f"实体 {entity.id} 与 {other_id} 关系紧张（分数 {score:.0f}）",
                    [entity.id, other_id]
                )

    def _choose_strategy(self, personality: PersonalityComponent, emotion: EmotionComponent) -> Optional[ResolutionStrategy]:
        """根据性格和情绪选择解决策略"""
        if personality.kindness > 0.7:
            return ResolutionStrategy.COLLABORATION
        if personality.greed > 0.7:
            return ResolutionStrategy.COMPETITION
        if emotion.fear > 0.6:
            return ResolutionStrategy.AVOIDANCE
        if emotion.anger > 0.6:
            return ResolutionStrategy.COMPETITION
        return ResolutionStrategy.COMPROMISE


if __name__ == "__main__":
    import logging
    logging.getLogger(__name__).debug("冲突管理系统已加载")