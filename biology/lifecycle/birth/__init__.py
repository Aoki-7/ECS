#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出生子模块 — 新生命的创建与初始化

职责：
    - 处理怀孕、孵化、萌芽等新生命诞生过程
    - 继承父代基因并施加变异（与 biology/genetics/ 协作）
    - 为新实体初始化生命周期组件和形态组件

子模块：
    - systems/ : BirthSystem（出生系统）

触发条件：
    - 动物/人类：ReproductionSystem 判定配对成功后生成 PregnancyComponent
    - 植物：ReproductionSystem 判定成熟后生成 SeedComponent 或直接萌芽
"""
