"""
组件包 — 纯数据组件定义

依赖：
    - core/
    - biology/
    - environment/

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源通用组件包 — 所有资源类型共享的基础组件

包含：
    - ResourceComponent : 资源通用属性（数量、质量、可采集性）
    - 为 food/, water/, wood/, stone/, metal/ 提供基础抽象

设计原则：
    - 本层放置跨资源类型的通用组件
    - 各资源子目录放置特定类型的专用组件
"""

