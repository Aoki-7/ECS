"""
physiology 模块

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生理系统模块 — 生物体内部机能的组件与系统

职责：
    - 提供描述生理状态的组件（代谢、体液、体温、疲劳、毒素、疾病等）
    - 提供更新生理状态的系统（按固定优先级顺序执行）

系统执行顺序：
    1. MetabolismSystem      — 代谢：能量消耗、营养转化
    2. HydrationSystem       — 体液：水分平衡、脱水判定
    3. ThermoregulationSystem — 体温：环境温度耦合、失温/过热判定
    4. ToxicitySystem        — 毒素：毒物积累与衰减
    5. DiseaseSystem         — 疾病：感染传播与病程推进
    6. FatigueSystem         — 疲劳：活动消耗与休息恢复
    7. HealthSystem          — 健康：综合损伤计算与恢复（最后执行）

与 human/ 的关系：
    - human/ 负责"行为决策"（去找水、去休息）
    - physiology/ 负责"身体变化"（口渴加剧、体力恢复）
    - 两者通过组件数据耦合：生理系统更新数值，人类系统读取数值并决策

与 biology/ 的关系：
    - biology/ 关注物种级别的生命周期与遗传
    - physiology/ 关注个体级别的实时机能运转
"""

