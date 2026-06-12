"""
resource/stone 子模块

依赖:
    - core/
    - biology/
    - environment/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石头资源模块 — 石材的创建与风化

职责：
    - StoneComponent: 石材属性（类型、硬度、风化程度、尺寸）
    - StoneFactory: 创建石头资源实体
    - StoneWeatherSystem: 模拟温度循环和湿度导致的风化剥落

与 human/ 的关系：
    - 人类采集石材用于建筑和工具制造
    - 风化降低石材可用性，促使人类寻找新矿源
"""


