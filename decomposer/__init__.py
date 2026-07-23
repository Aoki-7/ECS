"""
分解者系统 — 尸体分解、养分循环、土壤肥力

职责：

依赖：
    - core/
    - biology/
    - environment/

"""
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
分解者模块 — 尸体分解与物质循环

职责：
    - DecompositionComponent: 记录尸体分解过程中的剩余养分、微生物活性
    - DecomposerSystem      : 将尸体（CorpseComponent）分解为土壤养分

生态闭环：
    尸体 → DecomposerSystem → 土壤养分（N/P/K/有机质）→ 植物吸收 → 生长

与 CorpseSystem 的关系：
    - CorpseSystem 负责推进 decay_progress（受温度影响）
    - DecomposerSystem 负责根据 decay_progress 和 DecompositionComponent 释放养分
    - 两者协同工作：CorpseSystem "腐败"，DecomposerSystem "分解"

使用示例：
    from decomposer import DecomposerSystem, DecompositionComponent
"""

from decomposer.components.decomposition_component import DecompositionComponent
from decomposer.systems.decomposer_system import DecomposerSystem

__all__ = [
    "DecompositionComponent",
    "DecomposerSystem",
]
