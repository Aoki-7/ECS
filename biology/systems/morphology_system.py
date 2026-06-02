#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/systems/morphology_system.py → biology/lifecycle/growth/systems/morphology_system.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.growth.systems.morphology_system import MorphologySystem
"""

import warnings

warnings.warn(
    "biology.systems.morphology_system is deprecated. "
    "Use biology.lifecycle.growth.systems.morphology_system instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.growth.systems.morphology_system import MorphologySystem
