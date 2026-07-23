"""
死亡子模块 — 死亡触发与执行

依赖:
    - biology/lifecycle/
    - biology/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
死亡子模块 — 死亡判定与执行

职责：
    - 统一收集各业务系统产生的 PendingDeathComponent（死亡原因标记）
    - 执行死亡：销毁生物实体，创建尸体实体（与 corpse/ 协作）
    - 触发死亡事件日志，供统计和观察使用

设计原则：
    - 死亡原因由各业务系统（疾病、饥饿、天气、战斗）产生
    - 死亡执行由本模块统一处理，确保数据一致性
    - 支持"临终状态"（濒死期），允许其他系统做最后处理

子模块：
    - components/ : PendingDeathComponent, DeathCauseComponent
    - systems/    : DeathSystem（死亡执行）、CreatureDeathTriggerSystem（死亡触发检测）
"""

