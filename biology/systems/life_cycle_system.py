#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/systems/life_cycle_system.py → biology/lifecycle/systems/life_cycle_system.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
"""

import warnings

warnings.warn(
    "biology.systems.life_cycle_system is deprecated. "
    "Use biology.lifecycle.systems.life_cycle_system instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem