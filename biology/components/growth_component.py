#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件:biology/components/growth_component.py
@说明:生长组件（已弃用）

⚠️ 该组件已停用，不再被任何系统使用。
当前生长逻辑已迁移至 EnergyComponent.growth_pool + MorphologySystem 的组合。

保留原因：
    - 向后兼容（若旧存档/测试用例仍引用该组件）
    - 作为历史参考

建议：新项目或新系统请勿使用此组件。
"""

import warnings
from core.component import Component


class GrowthComponent(Component):
    """生长组件（已弃用，请使用 EnergyComponent + MorphologySystem）"""

    def __init__(self, rate: float = 0.0, max_size: float = 100.0):
        warnings.warn(
            "GrowthComponent is deprecated. Use EnergyComponent.growth_pool + MorphologySystem instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.size: float = 1.0
        self.rate: float = rate
        self.max_size: float = max_size
