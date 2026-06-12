"""
水包 — 水体、水源、水分资源

依赖：
    - core/
    - biology/
    - environment/

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水资源模块 — 水源实体的创建与管理

职责：
    - WaterComponent: 水源属性（水量、水质、盐度、污染程度）
    - WaterFactory: 创建水源实体（河流、湖泊、水井、雨水收集）

与 environment/ 的关系：
    - 降水（physics_weather/）补充地表水源
    - 蒸发（light_field/ + 温度）消耗水源
    - 土壤湿度（soil/）与地下水交换

与 human/ 的关系：
    - 人类通过 DrinkSystem 从水源获取水分
    - 水质影响健康（污染水源可能导致 DiseaseSystem 触发）
"""

