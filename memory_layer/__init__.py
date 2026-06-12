"""
统一记忆层 — 客观概念、主观记忆、认知框架、记忆扭曲

职责：
    - 独立于 ECS 的元层记忆服务
    - 客观概念（Concept）与主观记忆（MemoryInstance）分离
    - 记忆传播 = 重新生成（信息损失模型）

依赖：
    - core/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一记忆层（Memory Layer）

独立于 ECS 的元层服务，管理客观记忆（Concept）和主观记忆（MemoryInstance）。

核心设计：
    1. 独立于实体存在：实体消亡后概念仍然保留
    2. 主客观分离：Concept（客观事实） vs MemoryInstance（主观观点）
    3. 记忆传播 = 重新生成：不是复制，而是基于描述 + 接收者认知重新生成
    4. 结构化感官描述：形状/颜色/质地/大小/气味/声音/温度
    5. 主体限定动物/人类（SubjectType.ANIMAL / SubjectType.HUMAN）

快速开始：
    >>> from memory_layer import MemoryLayer, SensoryDescription, SubjectType
    >>> ml = MemoryLayer.get_instance()
    >>> desc = SensoryDescription(shape="圆形", color="灰色")
    >>> ml.register_entity(42, "stone", desc)
    >>> ml.record_contact(subject_id=1, subject_type=SubjectType.ANIMAL,
    ...                   entity_id=42, contact_type="visual", intensity=0.8)
    >>> mem = ml.recall_memory(1, "entity_42_stone")
    >>> print(mem.sensory_impression.to_text())

模块结构：
    memory_layer/
    ├── __init__.py              # 包导出（本文件）
    ├── README.md                # 文档
    ├── memory_layer.py          # 全局管理器（核心）
    ├── concept.py               # 客观记忆
    ├── memory_instance.py       # 主观记忆
    ├── sensory_description.py   # 结构化感官描述
    ├── emotional_tag.py         # 情感标签
    ├── contact_record.py        # 接触记录
    ├── association_link.py      # 联想链接
    ├── cognitive_framework.py   # 认知框架（Phase 3）
    ├── memory_distortion.py     # 扭曲引擎（Phase 3）
    ├── memory_registration_system.py  # 自动注册系统（Phase 2）
    ├── memory_persistence.py    # 持久化（Phase 4）
    └── tests/
        ├── test_memory_layer.py             # 23 个核心测试
        ├── test_memory_layer_integration.py # 6 个集成测试
        ├── test_phase3.py                   # 13 个高级特性测试
        └── test_phase4.py                   # 11 个性能/持久化测试
"""

from .memory_layer import MemoryLayer
from .concept import Concept, ConceptType
from .memory_instance import MemoryInstance, SubjectType
from .sensory_description import SensoryDescription
from .emotional_tag import EmotionalTag
from .contact_record import ContactRecord
from .association_link import AssociationLink
from .cognitive_framework import CognitiveFramework
from .memory_distortion import MemoryDistortionEngine, simulate_telephone_game
from .memory_persistence import MemoryPersistence
from .memory_registration_system import MemoryRegistrationSystem

__all__ = [
    # 核心类
    "MemoryLayer",
    "Concept",
    "ConceptType",
    "MemoryInstance",
    "SubjectType",
    "SensoryDescription",
    "EmotionalTag",
    "ContactRecord",
    "AssociationLink",
    # Phase 3 高级特性
    "CognitiveFramework",
    "MemoryDistortionEngine",
    "simulate_telephone_game",
    # Phase 4 持久化
    "MemoryPersistence",
    # Phase 2 ECS 集成
    "MemoryRegistrationSystem",
]

__version__ = "1.3.0"

