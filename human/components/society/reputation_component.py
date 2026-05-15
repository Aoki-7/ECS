#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:reputation_component.py
@说明:声誉组件 - 在社区中的评价
@时间:2026/04/27
@作者:Coder Agent
@版本:1.0
'''

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.component import Component


@dataclass
class ReputationComponent(Component):
    """
    声誉组件 - 在社区中的评价系统
    
    用途：
    - 影响NPC对玩家的态度
    - 解锁不同的对话选项和机会
    - 作为角色扮演的一个重要维度
    
    特性：
    - 整体声誉值
    - 特定领域专长认知
    - 社会地位
    - 传闻和谣言传播
    """
    
    def __init__(self, 
                 reputation: float = 50.0,
                 social_status: str = "unknown"):
        super().__init__()
        
        self._reputation = reputation
        self._specialties: Dict[str, int] = field(default_factory=dict)
        self._social_status = social_status
        self._known_for: List[str] = []
        self._rumors: List[Dict] = []

    @property
    def reputation(self) -> float:
        """当前声誉值 (0-100，越高越正面)"""
        return max(0, min(100, self._reputation))
    
    @reputation.setter
    def reputation(self, value: float):
        self._reputation = max(-50, min(150, value))  # 扩展范围，但保持映射
    
    def adjust_reputation(self, delta: float, aspect: str = "general") -> None:
        """调整声誉"""
        if aspect == "general":
            self._reputation += delta
        elif aspect in self._specialties:
            # 专项声誉与整体声誉的转换系数
            self._specialties[aspect] = max(0, min(100, self._specialties[aspect] + delta))
        
        # 如果某个专项达到阈值，提升整体声誉
        for specialty, level in self._specialties.items():
            if level >= 80 and self._reputation < 70:
                self._reputation = min(100, self._reputation + (level - 70) * 0.3)

    def get_status(self) -> str:
        """根据声誉值映射到社会地位"""
        if self._reputation >= 80:
            return "respected"
        elif self._reputation >= 50:
            return "known"
        elif self._reputation >= 20:
            return "observed"
        elif self._reputation < -30:
            return "feared"
        elif self._reputation < 0:
            return "disliked"
        else:
            return "commoner"

    def add_knowledge(self, area: str, level: int) -> None:
        """添加专长知识"""
        if area not in self._specialties:
            self._specialties[area] = 0
        self._specialties[area] = min(100, self._specialties[area] + level)
        
        # 如果专长很高，添加到"known for"列表
        if level >= 80 and area not in self._known_for:
            self._known_for.append(area)

    def get_reputation_summary(self) -> Dict:
        """获取声誉摘要"""
        return {
            "overall": round(self.reputation, 1),
            "status": self.get_status(),
            "specialties": dict(self._specialties),
            "known_for": list(self._known_for),
            "social_status": self._social_status
        }

    def spread_rumor(self, content: str, source: str = "unknown") -> str:
        """传播谣言"""
        rumor_id = len(self._rumors) + 1
        rumor = {
            "id": rumor_id,
            "content": content,
            "source": source,
            "spread_level": 0,
            "believers": []
        }
        self._rumors.append(rumor)
        return f"Rumor ID {rumor_id} created"

    def get_trusted_entities(self) -> List[str]:
        """获取值得信任的实体列表"""
        if self.reputation >= 50:
            return ["friendly_npc1", "friendly_npc2"]
        elif self.reputation >= 20:
            return ["stranger"]
        else:
            return ["none_trusted"]

    def is_honorable(self) -> bool:
        """判断是否是荣耀之身"""
        return (self._reputation >= 75 and 
                any(v >= 80 for v in self._specialties.values()))

    def get_title(self) -> str:
        """根据声誉生成称号"""
        if self.is_honorable():
            return "Honored Citizen"
        elif self.reputation >= 50:
            areas = list(self._specialties.items())
            if any(v >= 70 for _, v in areas):
                specialty = [k for k, v in areas if v >= 70][0]
                return f"Known {specialty}"
        elif self.reputation < 0:
            return "Notorious Figure"
        else:
            return "Local Person"


@dataclass
class FameComponent(Component):
    """
    声望组件 - 额外的知名度追踪
    
    特点：
    - 区域限制（在某地区出名）
    - 传播范围
    - 正面/负面报道比例
    """
    
    def __init__(self, 
                 regional_popularity: Dict[str, float] = None):
        super().__init__()
        self._popularity = regional_popularity or {}
        self._regional_reach: Dict[str, int] = {"village": 0, "town": 0, "kingdom": 0}
        self._positive_reports: int = 0
        self._negative_reports: int = 0

    def update_popularity(self, region: str, delta: float) -> None:
        """更新区域知名度"""
        if region not in self._popularity:
            self._popularity[region] = 0
        self._popularity[region] = max(0, min(100, self._popularity[region] + delta))

    def get_popularity_map(self) -> Dict[str, float]:
        """获取区域知名度分布"""
        return dict(self._popularity)


@dataclass
class SocialStandingComponent(Component):
    """
    社会地位组件 - 等级制度中的位置
    
    特点：
    - 职业阶层
    - 财富层次
    - 政治影响力
    """
    
    def __init__(self, 
                 class_rank: int = 0,
                 wealth_tier: str = "unknown",
                 political_influence: float = 0.0,
                 family_status: str = "origin"):
        super().__init__()
        
        self._class_rank = class_rank
        self._wealth_tier = wealth_tier
        self._political_influence = political_influence
        self._family_status = family_status

    def calculate_class(self) -> str:
        """根据属性计算职业等级"""
        if self._class_rank >= 80:
            return "nobility"
        elif self._class_rank >= 60:
            return "middle_class"
        elif self._class_rank >= 40:
            return "working_class"
        else:
            return "lower_class"

    def get_standing_summary(self) -> Dict:
        """获取社会地位摘要"""
        return {
            "class": self.calculate_class(),
            "wealth": self._wealth_tier,
            "politics": round(self._political_influence, 1),
            "origin": self._family_status
        }