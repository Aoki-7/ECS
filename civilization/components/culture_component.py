#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
文化组件 v4.16.0
定义文明的文化属性、价值观、传统与演化路径
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from core.component import Component
from typing import Dict, List, Set


class CulturalValue(Enum):
    """文化价值观维度"""
    INDIVIDUALISM = auto()       # 个人主义 ↔ 集体主义
    HIERARCHY = auto()           # 等级制 ↔ 平等主义
    TRADITION = auto()           # 传统保守 ↔ 开放创新
    ASSERTIVENESS = auto()       # 竞争进取 ↔ 合作温和
    UNCERTAINTY_AVOIDANCE = auto() # 风险厌恶 ↔ 风险偏好
    LONG_TERM_ORIENTATION = auto() # 长期导向 ↔ 短期享乐
    INDULGENCE = auto()          # 宽容放纵 ↔ 克制自律


@dataclass(slots=True)
class CulturalNorm:
    """文化规范"""
    name: str
    description: str
    effect: str                   # 效果描述
    strength: float = 0.5         # 规范强度 0-1
    acceptance: float = 0.7       # 民众接受度 0-1


@dataclass(slots=True)
class CulturalTradition:
    """文化传统/节日/仪式"""
    name: str
    type: str                     # 节日/仪式/习俗
    frequency: float              # 举办频率（小时）
    effect: Dict[str, float]      # 举办时的效果
    last_held: float = 0.0        # 上次举办时间


@dataclass(slots=True)
class CultureComponent(Component):
    """
    文化组件
    每个文明实体挂载此组件，存储其完整的文化属性
    """
    
    # === 基础文化属性 ===
    culture_name: str = "无名文化"
    culture_level: int = 1        # 文化等级 1-10
    cultural_capital: float = 0.0 # 文化资本，用于文化传播、演化
    
    # === 价值观维度（每个维度值 0-1，0表示偏向左侧，1表示偏向右侧）===
    values: Dict[CulturalValue, float] = field(default_factory=lambda: {
        CulturalValue.INDIVIDUALISM: 0.5,
        CulturalValue.HIERARCHY: 0.5,
        CulturalValue.TRADITION: 0.5,
        CulturalValue.ASSERTIVENESS: 0.5,
        CulturalValue.UNCERTAINTY_AVOIDANCE: 0.5,
        CulturalValue.LONG_TERM_ORIENTATION: 0.5,
        CulturalValue.INDULGENCE: 0.5,
    })
    
    # === 文化规范 ===
    norms: List[CulturalNorm] = field(default_factory=list)
    
    # === 文化传统 ===
    traditions: List[CulturalTradition] = field(default_factory=list)
    
    # === 文化禁忌 ===
    taboos: Set[str] = field(default_factory=set)
    
    # === 文化演化 ===
    evolution_rate: float = 0.01  # 文化演化速率
    cultural_diversity: float = 0.5 # 文化多样性 0-1
    assimilation_strength: float = 0.3 # 文化同化强度 0-1
    
    # === 对外文化属性 ===
    cultural_influence: float = 0.0 # 对外文化影响力
    foreign_culture_acceptance: float = 0.3 # 对外来文化接受度
    
    def get_value_bonus(self, value: CulturalValue, high_bonus: float, low_bonus: float) -> float:
        """
        根据价值观维度获取对应加成
        :param value: 价值观类型
        :param high_bonus: 维度值高时的加成（偏向右侧）
        :param low_bonus: 维度值低时的加成（偏向左侧）
        """
        val = self.values.get(value, 0.5)
        return low_bonus * (1 - val) + high_bonus * val
    
    def add_norm(self, norm: CulturalNorm) -> None:
        """添加文化规范"""
        self.norms.append(norm)
    
    def remove_norm(self, norm_name: str) -> None:
        """移除文化规范"""
        self.norms = [n for n in self.norms if n.name != norm_name]
    
    def add_tradition(self, tradition: CulturalTradition) -> None:
        """添加文化传统"""
        self.traditions.append(tradition)
    
    def remove_tradition(self, tradition_name: str) -> None:
        """移除文化传统"""
        self.traditions = [t for t in self.traditions if t.name != tradition_name]
    
    def add_taboos(self, taboo: str) -> None:
        """添加文化禁忌"""
        self.taboos.add(taboo)
    
    def remove_taboo(self, taboo: str) -> None:
        """移除文化禁忌"""
        if taboo in self.taboos:
            self.taboos.remove(taboo)
    
    def update_cultural_capital(self, delta: float) -> None:
        """更新文化资本"""
        self.cultural_capital = max(0.0, self.cultural_capital + delta)
        # 文化等级提升
        while self.cultural_capital >= self.culture_level * 100:
            self.cultural_capital -= self.culture_level * 100
            self.culture_level += 1
            self._level_up_effect()
    
    def _level_up_effect(self) -> None:
        """文化等级提升效果"""
        self.cultural_influence += 0.1
        self.assimilation_strength += 0.05
        self.evolution_rate += 0.005
    
    def get_culture_description(self) -> str:
        """生成文化描述文本"""
        desc = [f"【{self.culture_name}】 等级 {self.culture_level}\n"]
        desc.append("价值观倾向：")
        
        value_desc = {
            CulturalValue.INDIVIDUALISM: ("集体主义", "个人主义"),
            CulturalValue.HIERARCHY: ("平等主义", "等级制"),
            CulturalValue.TRADITION: ("开放创新", "传统保守"),
            CulturalValue.ASSERTIVENESS: ("合作温和", "竞争进取"),
            CulturalValue.UNCERTAINTY_AVOIDANCE: ("风险偏好", "风险厌恶"),
            CulturalValue.LONG_TERM_ORIENTATION: ("短期享乐", "长期导向"),
            CulturalValue.INDULGENCE: ("克制自律", "宽容放纵"),
        }
        
        for v, val in self.values.items():
            left, right = value_desc[v]
            if val < 0.3:
                desc.append(f"- 倾向{left}")
            elif val > 0.7:
                desc.append(f"- 倾向{right}")
            else:
                desc.append(f"- 中立平衡")
        
        if self.norms:
            desc.append(f"\n核心规范（{len(self.norms)}条）：")
            for norm in self.norms[:3]:
                desc.append(f"- {norm.name}：{norm.description}")
        
        if self.traditions:
            desc.append(f"\n传统习俗（{len(self.traditions)}个）：")
            for tradition in self.traditions[:3]:
                desc.append(f"- {tradition.name}：{tradition.type}")
        
        return "\n".join(desc)
