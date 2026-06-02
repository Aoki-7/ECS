#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物学系统包 — 跨物种共享的生物逻辑

包含：
    - GeneExpressionSystem   : 基因型 → 表现型转换
    - CompetitionSystem      : 生态竞争（光照遮阴 + 水分竞争）
    - GrowthSystem           : 光合作用 + 呼吸 + 能量分配
    - MorphologySystem       : 生长池 → 形态更新
    - NutrientSystem         : N/P/K 吸收与消耗
    - LifeCycleSystem        : 积温累积(GDD) + 阶段推进
    - SenescenceSystem       : 衰老退化
    - DamageRepairSystem     : 损伤修复
    - MutationSystem         : 持续环境诱变
    - ReproductionSystem     : 成熟期繁殖（遗传 + 变异 + 空间散布）
    - ImmuneSystem           : 感染传播与免疫反应
    - CreatureDeathTriggerSystem : 生物死亡条件检测

执行优先级：
    - 通常在 SimulationLoop 中以 priority 50 统一调度
    - 确保在环境系统（priority 20）之后、规则系统（priority 60）之前执行
"""
