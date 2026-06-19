"""
遗传子模块 — 基因原子定义与遗传机制

依赖:
    - biology/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遗传学子模块 — 基因原子定义与遗传算法

职责：
    - Gene: 定义单个基因的属性（名称、位点、等位基因、显隐性）
    - 提供基因交叉（Crossover）和变异（Mutation）算法
    - 支持 16 维基因组的创建、复制、重组

与 components/ 的关系：
    - genetics/ 提供基因的数据结构和算法
    - GenomeComponent 使用 genetics.Gene 存储个体的完整基因型
"""


