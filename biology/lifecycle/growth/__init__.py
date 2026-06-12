"""
生长包 — 形态发育与体型变化

依赖：
    - biology.lifecycle/
    - core/
    - identity/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成长子模块 — 生物体发育与形态变化

职责：
    - 管理生物体从幼体到成体的能量分配与形态增长
    - 植物：光合作用、茎高增粗、冠幅扩展、根系发育
    - 动物/人类：体型增长、器官发育（与 physiology/ 协作）

子模块：
    - systems/ : GrowthSystem（生长系统）、MorphologySystem（形态更新系统）

与 lifecycle/ 的关系：
    - growth/ 负责"体量增长"
    - lifecycle/ 负责"阶段推进"（种子→幼苗→成熟→衰老）
    - 两者通过 LifeCycleComponent 和 MorphologyComponent 数据耦合
"""

