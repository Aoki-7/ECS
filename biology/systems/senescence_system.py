#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/systems/senescence_system.py → biology/lifecycle/aging/systems/senescence_system.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.aging.systems.senescence_system import SenescenceSystem
"""

import warnings

warnings.warn(
    "biology.systems.senescence_system is deprecated. "
    "Use biology.lifecycle.aging.systems.senescence_system instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.aging.systems.senescence_system import SenescenceSystem