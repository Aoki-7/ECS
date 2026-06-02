#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金属资源模块 — 金属矿物的创建、氧化与风化

职责：
    - MetalComponent: 金属属性（类型、纯度、氧化程度、耐久）
    - MetalFactory: 创建金属资源实体
    - MetalOxidationSystem: 模拟金属在潮湿环境中的氧化过程

与 rules/ 的关系：
    - 氧化规则通过 TransformationRule 声明式配置
    - 氧化产物可能影响土壤 pH（未来扩展）

与 human/ 的关系：
    - 人类通过采集/采矿行为获取金属
    - 金属用于制造装备（equipment/）和建筑（civilization/）
"""
