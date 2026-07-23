"""
生命周期子模块 — 出生、成长、衰老、死亡

依赖:
    - biology/
    - core/

版本: v4.0
"""
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
biology/lifecycle/ — 生命周期子领域

涵盖实体从出生到死亡的完整生命周期：
    - birth/     : 出生/孵化系统
    - growth/    : 成长/发育系统
    - aging/     : 衰老系统
    - death/     : 死亡判定与执行系统
    - corpse/    : 尸体腐败与分解系统

设计原则：
    - 死亡原因由各业务系统（疾病、饥饿、天气、战斗）产生 PendingDeathComponent
    - 死亡执行由 death/systems/death_system.py 统一处理
    - 尸体处理由 corpse/systems/corpse_system.py 负责
"""

