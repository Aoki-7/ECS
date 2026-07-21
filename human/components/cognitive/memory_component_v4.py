#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:memory_component.py
@说明:记忆组件 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

from core.component import Component
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import math


class MemoryType(Enum):
    """记忆类型"""
    WORKING = auto()        # 工作记忆（短期）
    SEMANTIC = auto()       # 语义记忆（知识）
    EPISODIC = auto()       # 情景记忆（经历）
    PROCEDURAL = auto()     # 程序记忆（技能）
    EMOTIONAL = auto()      # 情绪记忆（感受）


class MemoryStrength(Enum):
    """记忆强度"""
    WEAK = auto()       # 弱
    MODERATE = auto()   # 中等
    STRONG = auto()     # 强
    PERMANENT = auto()  # 永久


class RetrievalType(Enum):
    """检索类型"""
    RECALL = auto()         # 回忆
    RECOGNITION = auto()    # 再认
    RECONSTRUCTION = auto() # 重构


@dataclass(slots=True)
class Memory:
    """记忆"""
    memory_id: int
    memory_type: MemoryType
    content: Any                    # 记忆内容
    strength: float = 0.5           # 记忆强度 (0-1)
    created_time: float = 0.0       # 创建时间
    last_accessed: float = 0.0      # 最后访问时间
    access_count: int = 0           # 访问次数
    emotional_valence: float = 0.0  # 情绪效价 (-1到1)
    importance: float = 0.5         # 重要性 (0-1)
    
    def get_strength_level(self) -> MemoryStrength:
        """获取记忆强度等级"""
        if self.strength < 0.3:
            return MemoryStrength.WEAK
        elif self.strength < 0.6:
            return MemoryStrength.MODERATE
        elif self.strength < 0.9:
            return MemoryStrength.STRONG
        else:
            return MemoryStrength.PERMANENT
    
    def update_strength(self, dt: float, accessed: bool = False):
        """更新记忆强度（根据遗忘曲线）"""
        # 艾宾浩斯遗忘曲线
        time_since_creation = dt - self.created_time
        time_since_access = dt - self.last_accessed
        
        # 基础遗忘率
        forgetting_rate = 0.1
        
        # 根据记忆类型调整遗忘率
        if self.memory_type == MemoryType.WORKING:
            forgetting_rate = 0.5  # 工作记忆遗忘快
        elif self.memory_type == MemoryType.PROCEDURAL:
            forgetting_rate = 0.05  # 程序记忆遗忘慢
        elif self.memory_type == MemoryType.EMOTIONAL:
            forgetting_rate = 0.02  # 情绪记忆遗忘很慢
        
        # 根据重要性调整遗忘率
        importance_factor = 1.0 - self.importance * 0.5
        
        # 根据情绪效价调整遗忘率
        emotion_factor = 1.0 - abs(self.emotional_valence) * 0.3
        
        # 计算遗忘
        if accessed:
            # 如果刚访问过，强化记忆
            self.strength = min(1.0, self.strength + 0.1)
            self.access_count += 1
            self.last_accessed = dt
        else:
            # 自然遗忘
            time_factor = math.exp(-forgetting_rate * time_since_access * importance_factor * emotion_factor)
            self.strength = max(0.0, self.strength * time_factor)
    
    def get_retrieval_probability(self, retrieval_type: RetrievalType = RetrievalType.RECALL) -> float:
        """获取检索概率"""
        base_probability = self.strength
        
        # 根据检索类型调整
        if retrieval_type == RetrievalType.RECOGNITION:
            # 再认比回忆容易
            base_probability = min(1.0, base_probability * 1.5)
        elif retrieval_type == RetrievalType.RECONSTRUCTION:
            # 重构可能不准确
            base_probability = base_probability * 0.8
        
        # 根据访问次数调整
        access_factor = min(1.0, self.access_count / 10.0)
        
        return base_probability * (0.5 + access_factor * 0.5)


@dataclass(slots=True)
class MemoryManagerComponent(Component):
    """
    记忆管理组件 v4.0 - 细化版
    包括工作记忆、长期记忆、遗忘曲线、记忆检索等细化功能。
    """
    
    # === 记忆存储 ===
    working_memory: List[Memory] = field(default_factory=list)      # 工作记忆（容量有限）
    long_term_memory: Dict[int, Memory] = field(default_factory=dict)  # 长期记忆
    next_memory_id: int = 0
    
    # === 记忆容量 ===
    working_memory_capacity: int = 7  # 工作记忆容量（7±2）
    long_term_memory_capacity: int = 10000  # 长期记忆容量（理论无限，实际有限）
    
    # === 记忆参数 ===
    attention_level: float = 0.5      # 注意力水平 (0-1)
    encoding_strength: float = 0.5    # 编码强度 (0-1)
    retrieval_strength: float = 0.5   # 检索强度 (0-1)
    
    # === 记忆统计 ===
    total_memories: int = 0           # 总记忆数
    memories_by_type: Dict[str, int] = field(default_factory=dict)  # 按类型统计（key为MemoryType.name）
    
    # === 记忆历史 ===
    memory_history: List[Dict] = field(default_factory=list)  # 记忆历史
    max_history_length: int = 100
    
    # === v2 API 兼容字段 ===
    # 旧版 MemoryComponent 使用 events(list)/places(dict)/people(dict)/recent_successes(dict)
    # 这些字段保持可写，以便旧系统直接修改，同时不破坏 v4 的 working/long_term 记忆结构。
    _events: List[Any] = field(default_factory=list)
    _places: Dict[Any, Dict] = field(default_factory=dict)
    _people: Dict[int, Dict] = field(default_factory=dict)
    _recent_successes: Dict[str, int] = field(default_factory=lambda: {
        "find_water": 0,
        "find_food": 0,
        "socialize": 0,
        "explore": 0,
        "rest": 0,
    })
    
    def __post_init__(self):
        """初始化记忆统计"""
        if not self.memories_by_type:
            for memory_type in MemoryType:
                self.memories_by_type[memory_type.name] = 0
    
    def add_memory(self, memory_type: MemoryType, content: Any, 
                   importance: float = 0.5, emotional_valence: float = 0.0) -> int:
        """添加记忆"""
        memory_id = self.next_memory_id
        self.next_memory_id += 1
        
        memory = Memory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            emotional_valence=emotional_valence,
            created_time=0.0,  # 实际应用中应该使用真实时间戳
            last_accessed=0.0
        )
        
        # 根据记忆类型存储
        if memory_type == MemoryType.WORKING:
            # 工作记忆容量有限
            if len(self.working_memory) >= self.working_memory_capacity:
                # 移除最弱的记忆
                weakest_memory = min(self.working_memory, key=lambda m: m.strength)
                self.working_memory.remove(weakest_memory)
                # 将最弱的记忆转移到长期记忆（如果强度足够）
                if weakest_memory.strength > 0.3:
                    self.long_term_memory[weakest_memory.memory_id] = weakest_memory
            
            self.working_memory.append(memory)
        else:
            # 长期记忆
            self.long_term_memory[memory_id] = memory
        
        # 更新统计
        self.total_memories += 1
        self.memories_by_type[memory_type.name] += 1
        
        # 记录记忆历史
        self._record_memory_event("add", f"添加{memory_type.name}记忆", memory_id)
        
        return memory_id
    
    def retrieve_memory(self, memory_id: int, retrieval_type: RetrievalType = RetrievalType.RECALL) -> Optional[Memory]:
        """检索记忆"""
        # 先在工作记忆中查找
        for memory in self.working_memory:
            if memory.memory_id == memory_id:
                memory.update_strength(0.0, accessed=True)
                return memory
        
        # 再在长期记忆中查找
        if memory_id in self.long_term_memory:
            memory = self.long_term_memory[memory_id]
            
            # 检查检索概率
            retrieval_probability = memory.get_retrieval_probability(retrieval_type)
            
            # 根据检索强度调整
            retrieval_probability *= self.retrieval_strength
            
            # 如果记忆强度足够高，直接检索成功
            if memory.strength > 0.7:
                memory.update_strength(0.0, accessed=True)
                return memory
            
            # 如果检索成功
            if retrieval_probability > 0.5:
                memory.update_strength(0.0, accessed=True)
                
                # 如果是工作记忆，将其加入工作记忆
                if memory.memory_type == MemoryType.WORKING:
                    if memory not in self.working_memory:
                        if len(self.working_memory) >= self.working_memory_capacity:
                            # 移除最弱的记忆
                            weakest_memory = min(self.working_memory, key=lambda m: m.strength)
                            self.working_memory.remove(weakest_memory)
                        self.working_memory.append(memory)
                
                return memory
        
        return None
    
    def search_memories(self, query: Any, memory_type: Optional[MemoryType] = None, 
                       max_results: int = 10) -> List[Memory]:
        """搜索记忆"""
        results = []
        
        # 搜索工作记忆
        for memory in self.working_memory:
            if memory_type and memory.memory_type != memory_type:
                continue
            
            # 简单的内容匹配（实际应用中应该使用更复杂的匹配算法）
            if self._match_content(memory.content, query):
                results.append(memory)
        
        # 搜索长期记忆
        for memory in self.long_term_memory.values():
            if memory_type and memory.memory_type != memory_type:
                continue
            
            if self._match_content(memory.content, query):
                results.append(memory)
        
        # 按强度排序
        results.sort(key=lambda m: m.strength, reverse=True)
        
        return results[:max_results]
    
    def _match_content(self, content: Any, query: Any) -> bool:
        """匹配内容"""
        # 简单的匹配逻辑
        if isinstance(content, str) and isinstance(query, str):
            return query.lower() in content.lower()
        elif isinstance(content, dict) and isinstance(query, dict):
            # 检查是否有共同的键值对
            for key, value in query.items():
                if key in content and content[key] == value:
                    return True
        elif content == query:
            return True
        
        return False
    
    def update_memories(self, dt: float):
        """更新记忆"""
        # 更新工作记忆
        for memory in self.working_memory:
            memory.update_strength(dt, accessed=False)
        
        # 更新长期记忆
        for memory in self.long_term_memory.values():
            memory.update_strength(dt, accessed=False)
        
        # 清理强度过低的记忆
        self._cleanup_weak_memories()
        
        # 更新注意力水平（自然波动）
        self.attention_level = max(0.0, min(1.0, 
            self.attention_level + (0.5 - self.attention_level) * 0.01 * dt))
    
    def _cleanup_weak_memories(self):
        """清理强度过低的记忆"""
        # 清理工作记忆
        self.working_memory = [m for m in self.working_memory if m.strength > 0.1]
        
        # 清理长期记忆（保留强度较高的记忆）
        memories_to_remove = []
        for memory_id, memory in self.long_term_memory.items():
            if memory.strength < 0.05:
                memories_to_remove.append(memory_id)
        
        for memory_id in memories_to_remove:
            del self.long_term_memory[memory_id]
            self.total_memories -= 1
    
    def consolidate_memories(self):
        """巩固记忆（将工作记忆转移到长期记忆）"""
        for memory in self.working_memory:
            if memory.strength > 0.3:  # 强度足够的工作记忆
                # 转移到长期记忆
                self.long_term_memory[memory.memory_id] = memory
                # 更新记忆类型
                if memory.memory_type == MemoryType.WORKING:
                    memory.memory_type = MemoryType.EPISODIC  # 工作记忆巩固为情景记忆
        
        # 清空工作记忆
        self.working_memory.clear()
        
        # 记录巩固事件
        self._record_memory_event("consolidate", "巩固记忆到长期存储")
    
    def get_memory_statistics(self) -> Dict:
        """获取记忆统计"""
        return {
            'total_memories': self.total_memories,
            'working_memory_count': len(self.working_memory),
            'long_term_memory_count': len(self.long_term_memory),
            'memories_by_type': self.memories_by_type.copy(),
            'attention_level': self.attention_level,
            'encoding_strength': self.encoding_strength,
            'retrieval_strength': self.retrieval_strength
        }
    
    def get_memory_summary(self) -> Dict:
        """获取记忆摘要"""
        # 计算平均记忆强度
        all_memories = list(self.working_memory) + list(self.long_term_memory.values())
        if all_memories:
            avg_strength = sum(m.strength for m in all_memories) / len(all_memories)
        else:
            avg_strength = 0.0
        
        # 计算各类型记忆的强度
        strength_by_type = {}
        for memory_type in MemoryType:
            type_memories = [m for m in all_memories if m.memory_type == memory_type]
            if type_memories:
                strength_by_type[memory_type.name] = sum(m.strength for m in type_memories) / len(type_memories)
            else:
                strength_by_type[memory_type.name] = 0.0
        
        return {
            'average_strength': avg_strength,
            'strength_by_type': strength_by_type,
            'memory_count': len(all_memories),
            'working_memory_usage': len(self.working_memory) / self.working_memory_capacity
        }
    
    def _record_memory_event(self, event_type: str, description: str, memory_id: Optional[int] = None):
        """记录记忆事件"""
        event = {
            'type': event_type,
            'description': description,
            'memory_id': memory_id,
            'timestamp': 0.0  # 实际应用中应该使用真实时间戳
        }
        
        self.memory_history.append(event)
        
        # 限制历史记录长度
        if len(self.memory_history) > self.max_history_length:
            self.memory_history = self.memory_history[-self.max_history_length:]
    
    def forget_memory(self, memory_id: int):
        """主动遗忘记忆"""
        if memory_id in self.long_term_memory:
            memory = self.long_term_memory[memory_id]
            memory.strength = 0.0
            del self.long_term_memory[memory_id]
            self.total_memories -= 1
            
            # 记录遗忘事件
            self._record_memory_event("forget", f"遗忘记忆", memory_id)
    
    def enhance_memory(self, memory_id: int, enhancement: float = 0.2):
        """增强记忆"""
        # 在工作记忆中查找
        for memory in self.working_memory:
            if memory.memory_id == memory_id:
                memory.strength = min(1.0, memory.strength + enhancement)
                memory.importance = min(1.0, memory.importance + enhancement * 0.5)
                return True
        
        # 在长期记忆中查找
        if memory_id in self.long_term_memory:
            memory = self.long_term_memory[memory_id]
            memory.strength = min(1.0, memory.strength + enhancement)
            memory.importance = min(1.0, memory.importance + enhancement * 0.5)
            return True
        
        return False
    
    # === 兼容属性 (Compatibility Layer for v2 API) ===
    def _get_memories_by_content_type(self, content_type: str) -> List[Any]:
        """根据内容类型从长期记忆中提取内容列表"""
        result = []
        for memory in self.long_term_memory.values():
            if memory.memory_type == MemoryType.EPISODIC:
                content = memory.content
                if isinstance(content, dict) and content.get('type') == content_type:
                    result.append(content)
                elif content_type == 'success' and isinstance(content, dict) and 'success' in content:
                    result.append(content)
        return result
    
    @property
    def events(self) -> List[Any]:
        """兼容v2: 返回事件记忆列表"""
        return self._events
    
    @events.setter
    def events(self, value: List[Any]):
        """兼容v2: 替换事件记忆列表"""
        self._events = list(value) if value else []
    
    @property
    def places(self) -> Dict[Any, Dict]:
        """兼容v2: 返回地点记忆字典"""
        return self._places
    
    @places.setter
    def places(self, value: Dict[Any, Dict]):
        """兼容v2: 替换地点记忆字典"""
        self._places = dict(value) if value else {}
    
    @property
    def people(self) -> Dict[int, Dict]:
        """兼容v2: 返回人物记忆字典"""
        return self._people
    
    @people.setter
    def people(self, value: Dict[int, Dict]):
        """兼容v2: 替换人物记忆字典"""
        self._people = dict(value) if value else {}
    
    @property
    def recent_successes(self) -> Dict[str, int]:
        """兼容v2: 返回最近成功行动计数字典"""
        return self._recent_successes
    
    @recent_successes.setter
    def recent_successes(self, value):
        """兼容v2: 替换最近成功行动计数"""
        if isinstance(value, dict):
            self._recent_successes = dict(value)
        elif isinstance(value, list):
            self._recent_successes = {
                "find_water": 0,
                "find_food": 0,
                "socialize": 0,
                "explore": 0,
                "rest": 0,
            }
            for item in value:
                action = item.get('action_type') if isinstance(item, dict) else str(item)
                if action:
                    self._recent_successes[action] = self._recent_successes.get(action, 0) + 1
        else:
            self._recent_successes = {
                "find_water": 0,
                "find_food": 0,
                "socialize": 0,
                "explore": 0,
                "rest": 0,
            }
    
    @property
    def MAX_EVENTS(self) -> int:
        """兼容v2: 工作记忆容量"""
        return self.working_memory_capacity
    
    @MAX_EVENTS.setter
    def MAX_EVENTS(self, value: int):
        """兼容v2: 设置工作记忆容量"""
        self.working_memory_capacity = value
    
    @property
    def MAX_PEOPLE(self) -> int:
        """兼容v2: 长期记忆容量"""
        return self.long_term_memory_capacity
    
    @MAX_PEOPLE.setter
    def MAX_PEOPLE(self, value: int):
        """兼容v2: 设置长期记忆容量"""
        self.long_term_memory_capacity = value

