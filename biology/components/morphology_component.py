#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] biology/components/morphology_component.py → biology/lifecycle/components/morphology_component.py

保留本文件仅用于向后兼容。
请从新路径导入：
    from biology.lifecycle.components.morphology_component import MorphologyComponent
"""

import warnings

warnings.warn(
    "biology.components.morphology_component is deprecated. "
    "Use biology.lifecycle.components.morphology_component instead.",
    DeprecationWarning,
    stacklevel=2,
)

from biology.lifecycle.components.morphology_component import MorphologyComponent
