"""
生命周期系统包 — 生长、衰老、死亡、繁殖

依赖:
    - biology/lifecycle/
    - biology/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生命周期系统包 — 协调生长、衰老、繁殖、死亡的系统集合

本包聚合了 lifecycle 下各子领域的系统，提供统一导入接口。
各子系统按 priority 顺序在 world.update() 中调度执行。
"""


