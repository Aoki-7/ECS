"""
死亡系统包 — 健康检查、寿命检查、死亡执行

依赖:
    - biology/lifecycle/death/
    - biology/lifecycle/
    - biology/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
死亡系统包 — 死亡判定与执行逻辑

包含：
    - CreatureDeathTriggerSystem : 扫描健康状态，判定是否满足死亡条件
    - DeathSystem                : 执行死亡：销毁实体、创建尸体、记录事件
    - DeathEventSystem           : 记录死亡事件
    - HumanDeathTriggerSystem    : 扫描健康状态，判定是否满足死亡条件
"""

