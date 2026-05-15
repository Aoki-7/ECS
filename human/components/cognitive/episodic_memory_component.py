#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:episodic_memory_component.py
@说明:事件记忆组件 - 记录个人经历和事件
@时间:2026/04/27
@作者:Coder Agent
@版本:1.0
'''

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

from core.component import Component


@dataclass
class EpisodicMemoryComponent(Component):
    """
    事件记忆组件 - 存储个人经历和事件
    
    特点:
    - 时间戳记录（何时发生）
    - 地点关联（在哪里发生）
    - 参与者（涉及的人物）
    - 情感标签（当时的情绪感受）
    - 细节描述（事件的详细内容）
    """
    # 当前记忆槽位数量限制（可选）
    max_memories: int = 100
    
    def __init__(self):
        super().__init__()
        self.memories: List[Dict] = field(default_factory=list)
        self.index: Dict[str, int] = {}  # 快速索引

    def add_memory(self, 
                   title: str,
                   description: str,
                   location: str = "",
                   participants: List[int] = None,
                   emotion: str = "neutral",
                   timestamp: Optional[datetime] = None) -> int:
        """
        添加入事记忆
        
        Args:
            title: 事件标题/关键词
            description: 详细描述
            location: 发生地点
            participants: 参与者的 entity id 列表
            emotion: 情感标签（happy/sad/angry/scared/excited等）
            timestamp: 时间戳，默认使用当前时间
        
        Returns:
            新记忆的索引 ID
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # 移除最旧的记忆如果达到上限
        if len(self.memories) >= self.max_memories:
            self.memories.pop(0)
        
        memory_id = f"epi_{len(self.memories)}"
        memory = {
            "id": memory_id,
            "title": title,
            "description": description,
            "location": location or "",
            "participants": participants or [],
            "emotion": emotion,
            "timestamp": timestamp,
            "retrieval_strength": 1.0  # 记忆强度衰减用
        }
        
        self.memories.append(memory)
        self.index[title.lower()] = len(self.memories) - 1
        
        return memory_id

    def recall(self, query: str) -> Optional[Dict]:
        """
        根据关键词回忆事件
        
        Args:
            query: 搜索关键词
        
        Returns:
            匹配的记忆，如果没找到返回 None
        """
        # 使用简单字符串匹配
        lower_query = query.lower()
        
        for memory in reversed(self.memories):
            if (lower_query in memory["title"].lower() or 
                lower_query in memory["description"].lower() or
                lower_query in str(memory.get("location", "")).lower()):
                return memory
        
        return None

    def get_by_timeframe(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        获取指定时间段内的记忆列表
        """
        return [m for m in self.memories 
                if start_date <= m["timestamp"] <= end_date]

    def get_related(self, entity_id: int) -> List[Dict]:
        """
        获取涉及特定人物的事件的记忆
        
        Args:
            entity_id: 人物 entity id
        """
        return [m for m in self.memories 
                if entity_id in m.get("participants", [])]

    def get_index(self, keyword: str) -> int:
        """
        使用预建索引快速查找记忆
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            记忆索引 ID，如果没找到返回 -1
        """
        lower_keyword = keyword.lower()
        return self.index.get(lower_keyword, -1)


@dataclass
class SemanticMemoryComponent(Component):
    """
    语义记忆组件 - 存储事实知识和世界信息
    
    特点：
    - 通用知识（如"苹果是水果"）
    - 概念关联（事物之间的关系）
    - 属性信息（事物的特征）
    """
    facts: Dict[str, List[Dict]] = field(default_factory=dict)
    concepts: Dict[str, str] = field(default_factory=dict)

    def add_fact(self, subject: str, predicate: str, obj: str, 
                 importance: float = 1.0) -> None:
        """
        添加事实知识
        
        Args:
            subject: 主题实体/概念
            predicate: 谓词（关系类型）
            obj: 宾语/对象
            importance: 重要性评分
        """
        fact = {
            "subject": subject,
            "predicate": predicate,
            "obj": obj,
            "importance": importance
        }
        
        if subject not in self.facts:
            self.facts[subject] = []
        self.facts[subject].append(fact)

    def query(self, subject: str, predicate: str) -> List[str]:
        """
        查询事实知识
        
        Args:
            subject: 主题
            predicate: 谓词
        
        Returns:
            匹配的宾语列表
        """
        if subject not in self.facts:
            return []
        return [f["obj"] for f in self.facts[subject] 
                if f["predicate"] == predicate]

    def add_concept(self, concept: str, definition: str) -> None:
        """添加概念定义"""
        self.concepts[concept] = definition


@dataclass
class ProceduralMemoryComponent(Component):
    """
    程序性记忆组件 - 存储技能和程序化知识
    
    特点：
    - 技能操作步骤
    - "如何做"的知识
    - 通过训练获得
    """
    skills: Dict[str, Dict] = field(default_factory=dict)

    def add_skill(self, skill_name: str, steps: List[str], 
                  difficulty: float = 1.0, mastery_level: float = 0.0) -> None:
        """
        添加技能
        
        Args:
            skill_name: 技能名称
            steps: 操作步骤列表
            difficulty: 难度系数
            mastery_level: 当前掌握程度 (0-100)
        """
        self.skills[skill_name] = {
            "name": skill_name,
            "steps": steps,
            "difficulty": difficulty,
            "mastery_level": mastery_level,
            "learned_at": None  # 学习时间戳（如果有）
        }

    def get_skill_steps(self, skill_name: str) -> List[str]:
        """获取技能步骤"""
        return self.skills.get(skill_name, {}).get("steps", [])

    def is_trained(self, skill_name: str) -> bool:
        """检查是否已掌握该技能"""
        return skill_name in self.skills


@dataclass
class WorkingMemoryComponent(Component):
    """
    工作记忆组件 - 短期记忆缓冲区
    
    特点：
    - 临时存储当前进行中的信息
    - 容量有限（通常7±2个组块）
    - 快速读写但容易丢失
    """
    buffer: List[Dict] = field(default_factory=list)
    max_capacity: int = 7  # 米勒定律：7±2

    def push(self, item: Dict) -> None:
        """添加一项到工作记忆"""
        if len(self.buffer) >= self.max_capacity:
            # 容量已满，丢弃最旧项
            self.buffer.pop(0)
        self.buffer.append(item)

    def pop(self) -> Optional[Dict]:
        """弹出最新项"""
        return self.buffer.pop(-1) if self.buffer else None

    def peek(self) -> Optional[Dict]:
        """查看最新项而不弹出"""
        return self.buffer[-1] if self.buffer else None

    def find(self, key: str, value: str) -> bool:
        """查找是否包含特定内容"""
        for item in self.buffer:
            if (key in item and item[key] == value):
                return True
        return False


# 更新__init__.py的扩展说明
if __name__ == "__main__":
    print("Memory components are available for import.")