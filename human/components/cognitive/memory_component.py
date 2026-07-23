#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:memory_component.py
@说明:记忆组件 - 统一入口（转发到v4版本）
@时间:2026/07/20
@版本:4.0

注意：此文件现在重定向到 memory_component_v4.py，以实现版本统一。
旧的 v2 实现已备份到 memory_component_legacy.py。
新版组件提供完整的 v2 API 兼容属性（events/places/people/MAX_EVENTS/MAX_PEOPLE 等）。
'''

from human.components.cognitive.memory_component_v4 import (
    MemoryManagerComponent,
    Memory,
    MemoryType,
    MemoryStrength,
    RetrievalType,
)

# 为旧版导入提供兼容别名
MemoryComponent = MemoryManagerComponent

__all__ = [
    "MemoryComponent",
    "MemoryManagerComponent",
    "Memory",
    "MemoryType",
    "MemoryStrength",
    "RetrievalType",
]