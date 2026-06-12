#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存档系统 — 世界序列化、增量存档、自动保存

目录结构:
    save_load/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── systems/
    │   └── save_load_system.py      # SaveLoadSystem: 存档/读档/自动保存
    ├── serializers/
    │   ├── world_serializer.py      # WorldSerializer: 世界状态序列化 (v4.0 使用 ComponentSerializer)
    │   ├── entity_serializer.py     # EntitySerializer: 实体序列化
    │   └── component_serializer.py  # ComponentSerializer: 组件序列化 (legacy)
    ├── incremental_save.py      # IncrementalSave: 增量存档 (只保存差异)
    ├── auto_save.py             # AutoSave: 自动保存 (定时/事件触发)
    └── tests/                   # 存档测试包 (8 测试)

核心职责:
    1. 世界序列化:
       - WorldSerializer: 将整个世界状态序列化为 JSON/二进制
       - v4.0: 使用 core/component_serializer.py 的统一序列化框架
       - @register_component 自动注册所有组件类型
       - 支持版本检测 (v3.9 vs v4.0 格式自动识别)

    2. 实体序列化:
       - EntitySerializer: 序列化实体 ID 和生成号
       - 支持实体引用解析 (跨实体引用)

    3. 组件序列化:
       - ComponentSerializer: 序列化组件数据
       - 支持自定义序列化 (to_dict/from_dict)
       - 支持类型注册 (自动/手动)

    4. 增量存档:
       - IncrementalSave: 只保存自上次存档后的变更
       - 变更检测: 组件添加/移除/修改
       - 合并加载: 基础存档 + 增量补丁

    5. 自动保存:
       - AutoSave: 定时自动保存 (可配置间隔)
       - 事件触发保存 (关键事件后自动保存)
       - 存档管理: 保留最近 N 个存档，自动清理旧存档

    6. 存档加载:
       - 完整加载: 从完整存档恢复世界状态
       - 增量加载: 基础存档 + 增量补丁合并
       - 版本兼容: 自动检测并转换旧版本存档

与其他模块的关系:
    - core/: 依赖 ECS 框架和 ComponentSerializer (v4.0)
    - memory_layer/: 使用 MemoryPersistence 进行记忆序列化
    - world/: 世界配置组件存档
    - 所有模块: 所有组件和实体都需要序列化支持

设计原则:
    - 统一序列化: 所有组件使用统一的序列化框架
    - 自动注册: @register_component 自动注册，无需手动维护
    - 向后兼容: 自动检测旧版本存档并转换
    - 增量保存: 只保存差异，减少存档大小和保存时间
    - 自动管理: 自动保存 + 自动清理，无需手动干预

版本: v4.0
"""

from save_load.systems.save_load_system import SaveLoadSystem

__all__ = ["SaveLoadSystem"]
