#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:memory_system.py
@说明:记忆系统 v4.0 - 细化版
@时间:2026/07/19
@版本:4.0
'''

import logging
import random
from typing import Dict, List, Optional, Any
from core.system import System
from core.world import World
from human.components.cognitive.memory_component_v4 import MemoryManagerComponent, MemoryType, RetrievalType
from human.components.basic.human_component import HumanComponent
from human.components.cognitive.intent_component import IntentComponent, IntentType

logger = logging.getLogger(__name__)


class MemorySystem(System):
    """记忆系统 v4.0 - 细化版"""
    tick_interval = 20  # 每20帧更新一次

    def __init__(self):
        self.memory_formation_probability = 0.3  # 记忆形成概率
        self.consolidation_interval = 100  # 记忆巩固间隔（帧）
        self.consolidation_counter = 0

    def update(self, world: World, dt: float):
        """更新记忆系统"""
        # 更新记忆
        for e, (memory, human, intent) in world.get_components(
            MemoryManagerComponent, HumanComponent, IntentComponent
        ):
            entity_id = e.id
            
            # 更新记忆
            memory.update_memories(dt)
            
            # 形成新记忆
            self._form_memories(memory, intent, entity_id)
        
        # 定期巩固记忆
        self.consolidation_counter += 1
        if self.consolidation_counter >= self.consolidation_interval:
            self.consolidation_counter = 0
            self._consolidate_all_memories(world)

    def _form_memories(self, memory: MemoryManagerComponent, intent: IntentComponent, entity_id: int):
        """形成新记忆"""
        # 根据意图形成记忆
        if random.random() < self.memory_formation_probability:
            if intent.intent == IntentType.EAT:
                # 形成关于食物的记忆
                content = {
                    'type': 'food',
                    'action': 'eat',
                    'location': intent.target_pos,
                    'satisfaction': random.uniform(0.5, 1.0)
                }
                memory.add_memory(MemoryType.EPISODIC, content, importance=0.6)
            
            elif intent.intent == IntentType.SOCIALIZE:
                # 形成关于社交的记忆
                content = {
                    'type': 'social',
                    'action': 'socialize',
                    'partner': intent.target_entity,
                    'pleasure': random.uniform(0.3, 0.9)
                }
                memory.add_memory(MemoryType.EPISODIC, content, importance=0.7)
            
            elif intent.intent == IntentType.WORK:
                # 形成关于工作的记忆
                content = {
                    'type': 'work',
                    'action': 'work',
                    'task': intent.goal_type,
                    'success': random.random() < 0.7  # 70%成功率
                }
                memory.add_memory(MemoryType.EPISODIC, content, importance=0.5)
            
            elif intent.intent == IntentType.FIGHT:
                # 形成关于战斗的记忆
                content = {
                    'type': 'combat',
                    'action': 'fight',
                    'enemy': intent.target_entity,
                    'fear': random.uniform(0.5, 1.0)
                }
                memory.add_memory(MemoryType.EMOTIONAL, content, importance=0.8, emotional_valence=-0.5)
            
            elif intent.intent == IntentType.EXPLORE:
                # 形成关于探索的记忆
                content = {
                    'type': 'exploration',
                    'action': 'explore',
                    'location': intent.target_pos,
                    'discovery': random.random() < 0.3  # 30%发现新事物
                }
                memory.add_memory(MemoryType.EPISODIC, content, importance=0.4)

    def _consolidate_all_memories(self, world: World):
        """巩固所有记忆"""
        for e, (memory, human) in world.get_components(MemoryManagerComponent, HumanComponent):
            memory.consolidate_memories()
            logger.debug(f"[Memory] 实体{e.id} 记忆巩固完成")

    def add_knowledge_memory(self, memory: MemoryManagerComponent, knowledge_type: str, 
                           content: Any, importance: float = 0.7):
        """添加知识记忆"""
        knowledge_content = {
            'type': 'knowledge',
            'knowledge_type': knowledge_type,
            'content': content,
            'learned_time': 0.0  # 实际应用中应该使用真实时间戳
        }
        return memory.add_memory(MemoryType.SEMANTIC, knowledge_content, importance=importance)

    def add_skill_memory(self, memory: MemoryManagerComponent, skill_type: str, 
                        proficiency: float, importance: float = 0.8):
        """添加技能记忆"""
        skill_content = {
            'type': 'skill',
            'skill_type': skill_type,
            'proficiency': proficiency,
            'practice_count': 0
        }
        return memory.add_memory(MemoryType.PROCEDURAL, skill_content, importance=importance)

    def search_food_memories(self, memory: MemoryManagerComponent) -> List:
        """搜索食物记忆"""
        return memory.search_memories({'type': 'food'}, MemoryType.EPISODIC)

    def search_social_memories(self, memory: MemoryManagerComponent) -> List:
        """搜索社交记忆"""
        return memory.search_memories({'type': 'social'}, MemoryType.EPISODIC)

    def search_danger_memories(self, memory: MemoryManagerComponent) -> List:
        """搜索危险记忆"""
        return memory.search_memories({'type': 'combat'}, MemoryType.EMOTIONAL)

    def get_memory_statistics(self, world: World) -> Dict:
        """获取记忆统计"""
        total_entities = 0
        total_memories = 0
        memory_types_count = {mt.name: 0 for mt in MemoryType}
        
        for e, (memory, human) in world.get_components(MemoryManagerComponent, HumanComponent):
            total_entities += 1
            stats = memory.get_memory_statistics()
            total_memories += stats['total_memories']
            
            for mt_name, count in stats['memories_by_type'].items():
                memory_types_count[mt_name] += count
        
        return {
            'total_entities': total_entities,
            'total_memories': total_memories,
            'average_memories_per_entity': total_memories / total_entities if total_entities > 0 else 0.0,
            'memory_types_distribution': memory_types_count
        }

    def get_memory_summary(self, memory: MemoryManagerComponent) -> Dict:
        """获取记忆摘要"""
        return memory.get_memory_summary()

    def enhance_memory_by_emotion(self, memory: MemoryManagerComponent, memory_id: int, 
                                 emotion_intensity: float):
        """根据情绪增强记忆"""
        # 情绪越强烈，记忆越深刻
        enhancement = emotion_intensity * 0.3
        return memory.enhance_memory(memory_id, enhancement)

    def forget_traumatic_memory(self, memory: MemoryManagerComponent, memory_id: int):
        """遗忘创伤记忆"""
        # 创伤记忆可能对健康有害，主动遗忘
        return memory.forget_memory(memory_id)

    def get_learning_progress(self, memory: MemoryManagerComponent, skill_type: str) -> float:
        """获取学习进度"""
        skill_memories = memory.search_memories({'type': 'skill', 'skill_type': skill_type}, 
                                              MemoryType.PROCEDURAL)
        
        if not skill_memories:
            return 0.0
        
        # 返回最新的技能熟练度
        latest_skill = max(skill_memories, key=lambda m: m.created_time)
        return latest_skill.content.get('proficiency', 0.0)

    def update_skill_proficiency(self, memory: MemoryManagerComponent, skill_type: str, 
                               practice_amount: float = 0.1):
        """更新技能熟练度"""
        skill_memories = memory.search_memories({'type': 'skill', 'skill_type': skill_type}, 
                                              MemoryType.PROCEDURAL)
        
        if skill_memories:
            # 更新现有技能记忆
            latest_skill = max(skill_memories, key=lambda m: m.created_time)
            current_proficiency = latest_skill.content.get('proficiency', 0.0)
            new_proficiency = min(1.0, current_proficiency + practice_amount)
            
            # 更新熟练度
            latest_skill.content['proficiency'] = new_proficiency
            latest_skill.content['practice_count'] = latest_skill.content.get('practice_count', 0) + 1
            
            # 增强记忆
            memory.enhance_memory(latest_skill.memory_id, practice_amount)
        else:
            # 创建新的技能记忆
            self.add_skill_memory(memory, skill_type, practice_amount)