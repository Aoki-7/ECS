"""
人类系统 — 最复杂的智能实体（认知、社交、经济、行动流水线） 的 子模块

依赖：
    - human.components/
    - core/
    - biology/
    - space/
    - environment/
    - animal/
    - plant/
    - resource/
    - civilization/
    - memory_layer/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康组件包 — 人类的伤病与恢复状态

包含：
    - InjuryComponent   : 具体伤势（部位、严重程度、出血状态）
    - RecoveryComponent : 恢复进程（治疗中、康复倒计时）

与 physiology/ 和 biology/ 的关系：
    - physiology/ 处理机能层面的健康（代谢、体温）
    - health/ 处理结构层面的损伤（伤口、骨折）
    - biology/ 的 HealthStatusComponent 提供综合健康评估
"""

