#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生理需求组件包 — 人类的基础生存需求

包含：
    - PhysiologyNeedsComponent : 综合生理需求（饥饿、口渴、精力、社交需求）

与 physiology/ 模块的关系：
    - human/components/physiological/ → 需求状态的数据容器
    - physiology/                   → 需求更新的逻辑系统
    - 两者通过 PhysiologyNeedsComponent 耦合
"""
