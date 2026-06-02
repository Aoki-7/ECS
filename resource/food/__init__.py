#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
食物资源模块 — 食物的创建、腐败与清理

职责：
    - FoodComponent: 食物属性（类型、热量、新鲜度、营养价值）
    - FoodFactory: 创建食物实体（野果、猎物肉、农作物等）
    - FoodDecaySystem: 新鲜度随时间衰减，最终腐败甚至产生毒素
    - FoodCleanupSystem: 清理已完全腐败或耗尽的食物实体

与 biology/ 的关系：
    - 植物通过 ReproductionSystem 产生果实（转化为食物实体）
    - 动物/人类死亡后可通过 rules/ 转化为肉类资源

与 human/ 的关系：
    - 人类通过 SearchSystem 发现食物，通过 PickupSystem 采集
    - 通过 EatSystem 消耗食物，恢复 HungerComponent
    - 腐败食物可能导致 DiseaseSystem 触发
"""
