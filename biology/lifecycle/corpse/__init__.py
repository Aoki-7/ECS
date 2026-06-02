#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尸体子模块 — 死亡后的分解与物质回收

职责：
    - 管理尸体（CorpseEntity）的腐败、分解过程
    - 将尸体中的有机物和养分逐步归还到环境（soil/）
    - 最终清理尸体实体，防止无限积累

子模块：
    - components/ : CorpseComponent（尸体状态：新鲜度、养分含量）
    - systems/    : CorpseSystem（腐败推进、养分释放、实体清理）

与 environment/ 的关系：
    - 尸体分解增加土壤肥力（SoilFertilityComponent）
    - 分解过程受环境温度和湿度影响
"""
