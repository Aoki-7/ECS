#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/systems/growth_system.py → biology/lifecycle/growth/systems/growth_system.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.growth.systems.growth_system import GrowthSystem
"""

import warnings

warnings.warn(
    "biology.systems.growth_system is deprecated. "
    "Use biology.lifecycle.growth.systems.growth_system instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.growth.systems.growth_system import GrowthSystem