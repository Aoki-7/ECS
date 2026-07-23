#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆层 — 客观概念、主观记忆、认知框架、记忆扭曲

目录结构:
    memory_layer/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── memory_layer.py          # MemoryLayer: 全局管理器 (单例模式)
    ├── concept.py               # Concept: 客观记忆 (独立于实体存在)
    ├── memory_instance.py       # MemoryInstance: 主观记忆 (实体视角)
    ├── sensory_description.py   # SensoryDescription: 结构化感官描述 (形状/颜色/质地/大小/气味/声音/温度)
    ├── emotional_tag.py         # EmotionalTag: 情感标签 (愉悦/恐惧/愤怒/悲伤)
    ├── contact_record.py        # ContactRecord: 接触记录 (时间/地点/方式/强度)
    ├── association_link.py      # AssociationLink: 联想链接 (概念间关联)
    ├── cognitive_framework.py   # CognitiveFramework: 认知框架 (分类/因果/时空)
    ├── memory_distortion.py     # MemoryDistortionEngine: 扭曲引擎 (遗忘/美化/恐惧放大)
    ├── memory_registration_system.py # MemoryRegistrationSystem: 自动注册系统
    ├── memory_persistence.py    # MemoryPersistence: 持久化 (序列化/反序列化)
    └── tests/                 # 记忆测试包 (53 测试)
        ├── test_memory_layer.py             # 23 核心测试
        ├── test_memory_layer_integration.py # 6 集成测试
        ├── test_phase3.py                   # 13 高级特性测试
        └── test_phase4.py                   # 11 性能/持久化测试

核心职责:
    1. 独立于 ECS 的元层服务:
       - 实体消亡后概念仍然保留 (Concept 独立于 Entity)
       - 支持跨实体记忆共享 (不同实体对同一概念的不同记忆)

    2. 主客观分离:
       - Concept (客观): 独立于任何实体视角的事实
         - 属性: 名称/类型/感官描述/物理属性/时间戳
         - 类型: OBJECT/ENTITY/EVENT/LOCATION/KNOWLEDGE/EMOTION
       - MemoryInstance (主观): 特定实体对概念的主观记忆
         - 属性: 概念引用/情感标签/接触记录/联想链接/可信度
         - 可信度: 随时间和冲突降低

    3. 记忆传播 = 重新生成:
       - 不是复制粘贴，而是基于描述 + 接收者认知重新生成
       - 每次传播产生信息损失 (细节丢失/情感偏差/理解差异)
       - 类比: 传话游戏，每次传递内容变化

    4. 结构化感官描述:
       - 形状/颜色/质地/大小/气味/声音/温度
       - 支持 to_text() 生成自然语言描述
       - 支持相似度计算 (用于记忆匹配)

    5. 记忆扭曲 (Phase 3):
       - 遗忘: 时间衰减 + 重要性保护 (重要记忆衰减慢)
       - 美化: 积极记忆增强，消极记忆淡化
       - 恐惧放大: 威胁记忆强度增加，细节模糊
       - 认知框架影响: 分类/因果/时空框架改变记忆编码

    6. 持久化 (Phase 4):
       - MemoryPersistence: 序列化/反序列化
       - 支持增量保存 (只保存变更)
       - 支持跨会话恢复

与其他模块的关系:
    - core/: 依赖 ECS 框架 (Entity/Component 用于实体引用)
    - human/: 人类使用 MemoryLayer 进行跨实体记忆共享
      - 对话: 实体 A 描述概念 → 实体 B 重新生成记忆
      - 教育: 教师传递知识 → 学生重新生成理解
      - 历史: 事件记录 → 后代重新生成历史记忆
    - animal/: 动物使用简化版记忆 (SensoryDescription + ContactRecord)
    - civilization/: 知识积累存储于记忆层，技术失传风险
    - save_load/: 使用 MemoryPersistence 进行记忆序列化

设计原则:
    - 独立元层: 记忆层独立于 ECS，实体消亡不影响概念
    - 主客观分离: 客观事实 vs 主观观点，支持多视角
    - 信息损失: 记忆传播不是复制，而是重新生成
    - 结构化感官: 形状/颜色/质地等属性支持机器处理
    - 主体限定: 只有动物/人类 (SubjectType.ANIMAL/HUMAN) 拥有记忆

快速开始:
    >>> from memory_layer import MemoryLayer, SensoryDescription, SubjectType
    >>> ml = MemoryLayer.get_instance()
    >>> desc = SensoryDescription(shape="圆形", color="灰色")
    >>> ml.register_entity(42, "stone", desc)
    >>> ml.record_contact(subject_id=1, subject_type=SubjectType.ANIMAL,
    ...                   entity_id=42, contact_type="visual", intensity=0.8)
    >>> mem = ml.recall_memory(1, "entity_42_stone")
    >>> print(mem.sensory_impression.to_text())

版本: v4.0
"""

from .memory_layer import MemoryLayer
from .concept import Concept, ConceptType
from .memory_instance import MemoryInstance, SubjectType
from .sensory_description import SensoryDescription
from .emotional_tag import EmotionalTag
from .contact_record import ContactRecord
from .association_link import AssociationLink
from .cognitive_framework import CognitiveFramework
from .memory_distortion import MemoryDistortionEngine
from .memory_registration_system import MemoryRegistrationSystem
from .memory_persistence import MemoryPersistence

__all__ = [
    "MemoryLayer",
    "Concept",
    "ConceptType",
    "MemoryInstance",
    "SubjectType",
    "SensoryDescription",
    "EmotionalTag",
    "ContactRecord",
    "AssociationLink",
    "CognitiveFramework",
    "MemoryDistortionEngine",
    "MemoryRegistrationSystem",
    "MemoryPersistence",
]