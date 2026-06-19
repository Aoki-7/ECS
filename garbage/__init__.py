"""
garbage 模块

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垃圾清理系统模块 — 实体生命周期末端管理

职责：
    - 定期扫描并清理无效、耗尽或标记为删除的实体
    - 防止世界中实体数量无限增长导致的内存泄漏
    - 与 resource/、biology/ 等模块协作，处理腐败/死亡后的残留物

子模块：
    - components/: 垃圾标记组件（如 DeleteMarkerComponent）
    - systems/:   清理执行系统（GarbageCleanupSystem）

设计原则：
    - 延迟清理：实体先被标记，再由本系统在合适时机批量移除
    - 阈值控制：可配置最大垃圾数量，超过时触发紧急清理
"""

