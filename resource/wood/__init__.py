#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
木材资源模块 — 木材的创建、腐朽与利用

职责：
    - WoodComponent: 木材属性（树种、含水率、腐朽程度、燃烧值）
    - WoodFactory: 创建木材资源实体（伐木后的木材堆）
    - WoodDecaySystem: 模拟真菌腐朽和湿度导致的强度下降

与 plant/ 的关系：
    - 木材来源于植物（plant/）的砍伐
    - 木材腐朽后释放养分，与环境 soil/ 形成循环

与 human/ 的关系：
    - 人类采集木材用于建筑、燃料、工具
    - 干燥木材 vs 湿木材有不同的燃烧效率和腐败速率
"""
