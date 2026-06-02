#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物学通用组件包 — 跨物种共享的生物属性

包含：
    - GenomeComponent      : 16维基因组（遗传信息存储）
    - PhenotypeComponent   : 表现型（基因表达后的实际性状）
    - ImmuneComponent      : 免疫系统状态（抗体水平、感染标记）
    - HealthStatusComponent: 健康综合状态（损伤、疾病、虚弱）
    - NutrientComponent    : 营养状态（N/P/K 等养分储备）

与 lifecycle/components/ 的区别：
    - biology/components/     → 通用生物属性（基因、免疫、健康）
    - biology/lifecycle/components/ → 生命周期特有（能量、形态、阶段）
"""
