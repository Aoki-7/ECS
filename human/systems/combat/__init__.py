#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
战斗系统包 — 冲突与战斗逻辑

包含：
    - CombatSystem    : 战斗执行（攻击判定、伤害计算、防御修正）
    - CombatAISystem  : 战斗 AI（目标选择、逃跑/反击决策）
    - ThreatSystem    : 威胁评估（扫描敌对实体、计算危险等级）

与 equipment/ 的关系：
    - 读取 EquipmentComponent 修正攻击力和防御力
    - 武器耐久在战斗中消耗
"""
