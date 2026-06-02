#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/components/energy_component.py → biology/lifecycle/components/energy_component.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.components.energy_component import EnergyComponent
"""

import warnings

warnings.warn(
    "biology.components.energy_component is deprecated. "
    "Use biology.lifecycle.components.energy_component instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.components.energy_component import EnergyComponent
