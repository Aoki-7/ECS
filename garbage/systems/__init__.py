"""
垃圾系统包 — 垃圾生成、分解、清理

依赖:
    - garbage/
    - core/
    - environment/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
垃圾系统包 — 实体清理执行

包含：
    - GarbageCleanupSystem : 扫描 DeleteMarkerComponent，批量移除实体
    - 支持阈值控制：当世界实体数超过上限时触发紧急清理

设计原则：
    - 延迟清理避免在系统迭代过程中修改实体集合
    - 批量移除减少 World 索引更新的开销
"""


