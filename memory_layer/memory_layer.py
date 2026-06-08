#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆层管理器（MemoryLayer）

全局单例，管理所有客观记忆（Concept）和主观记忆（MemoryInstance）。

核心职责：
1. 概念注册：实体创建时自动注册概念
2. 概念消亡：实体销毁时标记概念为非活跃
3. 接触记录：记录主体与实体的客观交互
4. 记忆形成：基于接触记录自动生成主观记忆
5. 记忆回忆：主体回忆某概念的记忆
6. 记忆传播：叙述传播时重新生成记忆（非复制）
7. 遗忘机制：自然衰减 + 容量上限
"""

import random
import uuid
from typing import Dict, List, Optional, Set

from .concept import Concept, ConceptType
from .memory_instance import MemoryInstance, SubjectType
from .contact_record import ContactRecord
from .sensory_description import SensoryDescription
from .emotional_tag import EmotionalTag


class MemoryLayer:
    """
    统一记忆层管理器

    全局单例，管理：
    - _concepts: Dict[str, Concept] — 客观记忆注册表
    - _memories: Dict[str, MemoryInstance] — 主观记忆图谱，key: "subject_id:concept_id"
    - _contacts: List[ContactRecord] — 接触记录历史
    - _entity_to_concept: Dict[int, str] — entity_id → concept_id 映射
    """

    _instance: Optional["MemoryLayer"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._concepts: Dict[str, Concept] = {}
        self._memories: Dict[str, MemoryInstance] = {}
        self._contacts: List[ContactRecord] = []
        self._entity_to_concept: Dict[int, str] = {}

        # 配置
        self.default_max_memories_per_subject = 100
        self.default_decay_rate = 0.01
        self.default_forget_threshold = 0.8

    # ========== 单例访问 ==========

    @classmethod
    def get_instance(cls) -> "MemoryLayer":
        """获取全局单例"""
        if cls._instance is None:
            cls._instance = MemoryLayer()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）"""
        cls._instance = None

    # ========== 客观记忆管理：Concept ==========

    def register_entity(
        self,
        entity_id: int,
        entity_type: str,
        description: SensoryDescription,
        physical_props: Optional[Dict] = None,
        name: Optional[str] = None,
    ) -> Concept:
        """
        实体创建时注册概念。

        Args:
            entity_id: 实体ID
            entity_type: 实体类型（如 "stone", "animal", "plant"）
            description: 客观感官描述
            physical_props: 物理属性字典
            name: 概念名称（默认自动生成）

        Returns:
            注册的 Concept
        """
        concept_id = f"entity_{entity_id}_{entity_type}"
        concept_name = name or f"{entity_type}_{entity_id}"

        concept = Concept(
            concept_id=concept_id,
            name=concept_name,
            concept_type=ConceptType.ENTITY,
            canonical_description=description,
            physical_properties=physical_props or {},
            source_entity_id=entity_id,
            source_entity_type=entity_type,
            created_at=self._get_current_time(),
            is_active=True,
        )

        self._concepts[concept_id] = concept
        self._entity_to_concept[entity_id] = concept_id

        return concept

    def entity_destroyed(self, entity_id: int, timestamp: Optional[float] = None) -> None:
        """
        实体消亡时标记概念为非活跃。

        概念本身不删除，只是标记 is_active=False。
        """
        concept_id = self._entity_to_concept.get(entity_id)
        if concept_id and concept_id in self._concepts:
            self._concepts[concept_id].mark_destroyed(timestamp or self._get_current_time())

    def create_abstract_concept(
        self,
        name: str,
        description: SensoryDescription,
        concept_type: ConceptType = ConceptType.ABSTRACT,
        physical_props: Optional[Dict] = None,
    ) -> Concept:
        """
        创建抽象/虚构概念（无实体来源）。

        用于神话、传说、抽象概念等。
        """
        concept_id = f"abstract_{name}_{uuid.uuid4().hex[:8]}"

        concept = Concept(
            concept_id=concept_id,
            name=name,
            concept_type=concept_type,
            canonical_description=description,
            physical_properties=physical_props or {},
            source_entity_id=None,
            is_active=False,  # 抽象概念从未有实体
            created_at=self._get_current_time(),
        )

        self._concepts[concept_id] = concept
        return concept

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """获取概念"""
        return self._concepts.get(concept_id)

    def get_concept_by_entity(self, entity_id: int) -> Optional[Concept]:
        """通过实体ID获取概念"""
        concept_id = self._entity_to_concept.get(entity_id)
        if concept_id:
            return self._concepts.get(concept_id)
        return None

    def get_all_concepts(self) -> List[Concept]:
        """获取所有概念"""
        return list(self._concepts.values())

    def get_active_concepts(self) -> List[Concept]:
        """获取仍有实体对应的概念"""
        return [c for c in self._concepts.values() if c.is_active]

    # ========== 接触记录管理 ==========

    def record_contact(
        self,
        subject_id: int,
        subject_type: SubjectType,
        entity_id: int,
        contact_type: str,
        intensity: float = 0.5,
        duration: float = 0.0,
        context: Optional[str] = None,
        emotional_state: Optional[str] = None,
        attention_level: float = 0.5,
    ) -> Optional[ContactRecord]:
        """
        记录主体与实体的接触。

        接触后自动形成或更新主观记忆。
        """
        concept_id = self._entity_to_concept.get(entity_id)
        if not concept_id:
            return None

        contact = ContactRecord(
            contact_id=f"contact_{uuid.uuid4().hex[:8]}",
            subject_id=subject_id,
            subject_type=subject_type.name,
            entity_id=entity_id,
            concept_id=concept_id,
            contact_type=contact_type,
            timestamp=self._get_current_time(),
            duration=duration,
            intensity=intensity,
            context=context,
            subject_emotional_state=emotional_state,
            subject_attention_level=attention_level,
        )

        self._contacts.append(contact)

        # 接触后自动形成/更新记忆
        self._form_or_update_memory(subject_id, subject_type, concept_id, contact)

        return contact

    # ========== 主观记忆管理：MemoryInstance ==========

    def _form_or_update_memory(
        self,
        subject_id: int,
        subject_type: SubjectType,
        concept_id: str,
        contact: ContactRecord,
    ) -> MemoryInstance:
        """
        基于接触记录形成或更新主观记忆。

        如果已有记忆则更新，否则创建新记忆。
        """
        key = f"{subject_id}:{concept_id}"
        concept = self._concepts.get(concept_id)
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")

        if key in self._memories:
            # 更新现有记忆
            memory = self._memories[key]
            memory.recall(contact.timestamp)

            # 根据新的接触信息更新感官印象（注意力越高，更新越多）
            if contact.subject_attention_level > 0.3:
                memory.sensory_impression = memory.sensory_impression.merge_with(
                    concept.canonical_description,
                    weight=contact.intensity * contact.subject_attention_level
                )

            # 情感可能变化
            if contact.subject_emotional_state:
                memory.emotional_tag = EmotionalTag(
                    primary=contact.subject_emotional_state,
                    intensity=contact.intensity,
                    reason=contact.context,
                )
        else:
            # 形成新记忆
            memory = self._form_new_memory(subject_id, subject_type, concept, contact)
            self._memories[key] = memory

        return memory

    def _form_new_memory(
        self,
        subject_id: int,
        subject_type: SubjectType,
        concept: Concept,
        contact: ContactRecord,
    ) -> MemoryInstance:
        """形成新的主观记忆"""
        # 主观印象 = 客观描述 + 注意力过滤 + 初始扭曲
        attention = contact.subject_attention_level
        subjective_description = self._filter_by_attention(
            concept.canonical_description,
            attention,
        )

        # 初始扭曲：注意力越低，扭曲越大
        initial_distortion = max(0.0, 1.0 - attention)

        return MemoryInstance(
            memory_id=f"mem_{uuid.uuid4().hex[:8]}",
            concept_id=concept.concept_id,
            subject_id=subject_id,
            subject_type=subject_type,
            sensory_impression=subjective_description,
            emotional_tag=EmotionalTag(
                primary=contact.subject_emotional_state or "neutral",
                intensity=contact.intensity,
                reason=contact.context,
            ),
            confidence=attention,
            distortion_level=initial_distortion,
            clarity=attention,
            first_contact=contact.timestamp,
            last_recall=contact.timestamp,
            formation_type="direct",
        )

    def recall_memory(self, subject_id: int, concept_id: str) -> Optional[MemoryInstance]:
        """
        主体回忆某概念的记忆。

        回忆操作会更新 last_recall 和 recall_count。
        """
        key = f"{subject_id}:{concept_id}"
        memory = self._memories.get(key)

        if memory:
            memory.recall(self._get_current_time())

        return memory

    def get_subject_memories(self, subject_id: int) -> List[MemoryInstance]:
        """获取某主体的所有记忆"""
        return [
            m for key, m in self._memories.items()
            if key.startswith(f"{subject_id}:")
        ]

    def get_concept_memories(self, concept_id: str) -> List[MemoryInstance]:
        """获取某概念的所有主体记忆"""
        return [
            m for m in self._memories.values()
            if m.concept_id == concept_id
        ]

    def get_all_memories(self) -> List[MemoryInstance]:
        """获取所有记忆"""
        return list(self._memories.values())

    # ========== 记忆传播：重新生成 ==========

    def narrate_memory(
        self,
        from_subject: int,
        to_subject: int,
        to_subject_type: SubjectType,
        concept_id: str,
    ) -> Optional[MemoryInstance]:
        """
        叙述传播：重新生成记忆。

        不是复制，而是基于：
        1. 叙述者的描述（可能不完整/扭曲）
        2. 接收者自身的认知框架
        3. 传播过程中的信息损失

        生成一个全新的 MemoryInstance。
        """
        narrator_memory = self.recall_memory(from_subject, concept_id)
        if not narrator_memory:
            return None

        concept = self._concepts.get(concept_id)
        if not concept:
            return None

        # 1. 信息损失：叙述者无法完美表达记忆
        expressed_description = self._express_with_loss(
            narrator_memory.sensory_impression,
            narrator_memory.confidence,
        )

        # 2. 接收者理解：基于自身认知框架重新解释
        # （简化版：添加随机扭曲）
        interpreted_description = self._add_random_distortion(
            expressed_description,
            distortion_level=0.3,
        )

        # 3. 情感传递损失
        transferred_emotion = narrator_memory.emotional_tag.transfer_with_loss(
            loss_factor=0.3
        )

        # 4. 生成新记忆（重新生成，不是复制）
        new_memory = MemoryInstance(
            memory_id=f"mem_{uuid.uuid4().hex[:8]}",
            concept_id=concept_id,
            subject_id=to_subject,
            subject_type=to_subject_type,
            sensory_impression=interpreted_description,
            emotional_tag=transferred_emotion,
            confidence=narrator_memory.confidence * 0.5,  # 间接记忆确信度更低
            distortion_level=min(1.0, narrator_memory.distortion_level + 0.3),
            clarity=0.6,  # 新记忆初始清晰度中等
            first_contact=self._get_current_time(),
            last_recall=self._get_current_time(),
            formation_type="narrative",
            source_subject_id=from_subject,
            narrative=f"从{from_subject}处听说: {narrator_memory.narrative or '关于' + concept.name}",
        )

        key = f"{to_subject}:{concept_id}"
        self._memories[key] = new_memory

        return new_memory

    def _express_with_loss(
        self,
        description: SensoryDescription,
        confidence: float,
    ) -> SensoryDescription:
        """叙述表达时的信息损失"""
        loss_probability = 1.0 - confidence
        result = SensoryDescription()

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(description, field)
            if value and random.random() > loss_probability:
                setattr(result, field, value)

        return result

    def _add_random_distortion(
        self,
        description: SensoryDescription,
        distortion_level: float,
    ) -> SensoryDescription:
        """添加随机扭曲（简化版认知框架）"""
        result = SensoryDescription()

        # 形状扭曲
        if description.shape and random.random() < distortion_level:
            shape_alternatives = {
                "圆形": ["椭圆形", "近似圆形"],
                "方形": ["长方形", "近似方形"],
            }
            alts = shape_alternatives.get(description.shape, [description.shape])
            result.shape = random.choice(alts)
        else:
            result.shape = description.shape

        # 颜色扭曲
        if description.color and random.random() < distortion_level:
            color_alternatives = {
                "灰色": ["暗色", "灰白色"],
                "红色": ["暗红色", "红褐色"],
            }
            alts = color_alternatives.get(description.color, [description.color])
            result.color = random.choice(alts)
        else:
            result.color = description.color

        # 其他字段直接复制（简化）
        result.texture = description.texture
        result.size = description.size
        result.smell = description.smell
        result.sound = description.sound
        result.temperature = description.temperature

        return result

    # ========== 遗忘机制 ==========

    def apply_forgetting(
        self,
        subject_id: Optional[int] = None,
        decay_rate: Optional[float] = None,
    ) -> int:
        """
        应用遗忘。

        Returns:
            被遗忘的记忆数量
        """
        rate = decay_rate or self.default_decay_rate
        current_time = self._get_current_time()
        to_forget = []

        for key, memory in self._memories.items():
            if subject_id is not None and memory.subject_id != subject_id:
                continue

            # 自然衰减
            memory.decay(rate)

            # 遗忘判断
            time_since_recall = current_time - memory.last_recall
            emotional_anchor = memory.emotional_tag.intensity
            importance = memory.calculate_importance()

            # 遗忘概率 = f(清晰度, 时间, 情感锚定, 重要性)
            forget_probability = (
                (1 - memory.clarity) * 0.3
                + (time_since_recall / 1000) * 0.3
                - emotional_anchor * 0.2
                - importance * 0.2
            )

            if forget_probability > self.default_forget_threshold:
                to_forget.append(key)

        for key in to_forget:
            del self._memories[key]

        return len(to_forget)

    def enforce_capacity_limit(
        self,
        subject_id: int,
        max_memories: Optional[int] = None,
    ) -> int:
        """
        强制记忆容量上限：遗忘最不重要的记忆。

        Returns:
            被遗忘的记忆数量
        """
        limit = max_memories or self.default_max_memories_per_subject

        subject_memories = [
            (key, m) for key, m in self._memories.items()
            if m.subject_id == subject_id
        ]

        if len(subject_memories) <= limit:
            return 0

        # 按重要性排序（保留重要的）
        subject_memories.sort(key=lambda kv: kv[1].calculate_importance(), reverse=True)

        # 遗忘超出容量的
        forgotten = 0
        for key, _ in subject_memories[limit:]:
            del self._memories[key]
            forgotten += 1

        return forgotten

    # ========== 序列化/反序列化 ==========

    def to_dict(self) -> dict:
        """序列化所有记忆数据（兼容持久化接口）"""
        return {
            "concepts": {cid: c.to_dict() for cid, c in self._concepts.items()},
            "memories": {key: m.to_dict() for key, m in self._memories.items()},
            "contacts": [c.to_dict() for c in self._contacts],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryLayer":
        """从字典反序列化（兼容持久化接口）"""
        ml = cls.get_instance()
        ml._concepts.clear()
        ml._memories.clear()
        ml._contacts.clear()
        ml._entity_to_concept.clear()

        # 恢复概念
        for cid, cdata in data.get("concepts", {}).items():
            ml._concepts[cid] = Concept.from_dict(cdata)
            if ml._concepts[cid].source_entity_id:
                ml._entity_to_concept[ml._concepts[cid].source_entity_id] = cid

        # 恢复记忆
        for key, mdata in data.get("memories", {}).items():
            ml._memories[key] = MemoryInstance.from_dict(mdata)

        # 恢复接触记录
        for cdata in data.get("contacts", []):
            ml._contacts.append(ContactRecord.from_dict(cdata))

        return ml

    def serialize(self) -> dict:
        """序列化所有记忆数据（兼容旧接口）"""
        return self.to_dict()

    def deserialize(self, data: dict) -> None:
        """从存档恢复（兼容旧接口）"""
        self.from_dict(data)

    # ========== 工具方法 ==========

    def _get_current_time(self) -> float:
        """获取当前时间（简化版，实际应从 World 获取）"""
        import time
        return time.time()

    def _filter_by_attention(
        self,
        description: SensoryDescription,
        attention: float,
    ) -> SensoryDescription:
        """根据注意力水平过滤感官描述"""
        result = SensoryDescription()
        missing_probability = 1.0 - attention

        for field in ["shape", "color", "texture", "size", "smell", "sound", "temperature"]:
            value = getattr(description, field)
            if value and random.random() > missing_probability:
                setattr(result, field, value)

        return result

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "concept_count": len(self._concepts),
            "active_concepts": len([c for c in self._concepts.values() if c.is_active]),
            "memory_count": len(self._memories),
            "contact_count": len(self._contacts),
            "subjects": len(set(m.subject_id for m in self._memories.values())),
        }
