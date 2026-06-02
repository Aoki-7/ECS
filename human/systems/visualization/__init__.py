#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
[已迁移] 可视化模块已迁移至 presentation/

旧路径保留兼容导入：
    from presentation.human_panel import HumanStatePanel
    from presentation.human_observation_system import HumanObservationSystem
    from presentation.human_observation_component import HumanObservationComponent
"""

import warnings

warnings.warn(
    "human.systems.visualization is deprecated. "
    "Use presentation.human_panel, presentation.human_observation_system instead.",
    DeprecationWarning,
    stacklevel=2,
)

from presentation.human_panel import HumanStatePanel
from presentation.human_observation_system import HumanObservationSystem
from presentation.human_observation_component import HumanObservationComponent

__all__ = ["HumanStatePanel", "HumanObservationSystem", "HumanObservationComponent"]
