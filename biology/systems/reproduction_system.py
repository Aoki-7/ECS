#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/systems/reproduction_system.py → biology/lifecycle/birth/systems/reproduction_system.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.birth.systems.reproduction_system import BiologyReproductionSystem
"""

import warnings

warnings.warn(
    "biology.systems.reproduction_system is deprecated. "
    "Use biology.lifecycle.birth.systems.reproduction_system instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.birth.systems.reproduction_system import BiologyReproductionSystem