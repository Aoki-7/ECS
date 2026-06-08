#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:search_component.py
@说明:搜索组件 — 智能目标发现与策略管理
@时间:2026/03/31 15:17:57
@作者:AI Assistant
@版本:2.0

增强说明（v2.0）：
    - 新增搜索策略系统（visual → memory → explore → random）
    - 引入搜索历史，避免在同一区域重复搜索
    - 基于历史成功率动态评估找到目标的概率
    - 发现目标后立即记录到 discoveries，供记忆系统读取

认知模型：
    人类搜索遵循"就近原则"：先视觉扫描 → 再回忆已知位置 →
    再扩大范围探索 → 最后随机尝试。组件中的 strategy 字段
    记录当前所处的搜索阶段。
'''

from dataclasses import dataclass, field
from core.component import Component
from typing import Optional, Type


@dataclass(slots=True)
class SearchComponent(Component):
    """
    智能搜索组件 — 模拟人类的目标发现过程

    字段分组：
        1) 搜索目标：target_component, max_distance, result_entity
        2) 搜索策略：strategy, strategy_history
        3) 搜索历史：search_history, max_history_size
        4) 搜索期望：estimated_probability, confidence_threshold
        5) 搜索统计：last_search_tick, total_searches, successful_searches
        6) 发现记录：discoveries
    """

    # ── 搜索目标 ──
    target_component: Optional[Type[Component]] = None
    """目标组件类型（用于筛选目标实体）。
    示例：FoodComponent → 查找所有拥有 FoodComponent 的实体。"""

    max_distance: float = float("inf")
    """最大搜索距离。限制搜索范围，避免全图扫描（性能关键）。"""

    result_entity: Optional[int] = None
    """搜索结果（目标实体 ID）。由 SearchSystem 写入。
    表示当前找到的最优目标（通常是最近的）。未找到时为 None。"""

    # ── 搜索策略 ──
    strategy: str = "visual"
    """当前搜索策略，取值：
        - "visual"   : 视觉扫描（依赖 VisionComponent，半径内最近目标）
        - "memory"   : 记忆回溯（从 MemoryComponent 读取已知位置）
        - "explore"  : 扩大探索（使用空间索引 query_radius 大范围扫描）
        - "random"   : 随机漫游（无目的移动以扩大覆盖范围）
    策略由 SearchSystem 按递进顺序自动切换。"""

    strategy_history: list = field(default_factory=list)
    """最近使用的策略记录（最多保留 10 条）。
    格式：[(tick, strategy, found), ...]，用于分析搜索行为模式。"""

    # ── 搜索历史（避免在同一区域重复搜索）──
    search_history: list = field(default_factory=list)
    """搜索过的位置历史。格式：[(tick, x, y, strategy, found), ...]。
    长度上限由 max_history_size 控制。"""

    max_history_size: int = 20
    """搜索历史最大保留条数。超过后丢弃最旧的记录。"""

    # ── 搜索期望（基于记忆预估）──
    estimated_probability: float = 0.5
    """估计找到目标的概率 (0~1)。
    由 SearchSystem 根据历史成功率动态更新：
        P = (successful_searches + 1) / (total_searches + 2)
    当 P < confidence_threshold 时，系统可能建议改变策略或放弃。"""

    confidence_threshold: float = 0.3
    """置信度阈值。当 estimated_probability 低于此值时，
    SearchSystem 会尝试切换策略或标记搜索为低信心状态。"""

    # ── 搜索统计 ──
    last_search_tick: int = 0
    """上次执行搜索的 world tick。"""

    total_searches: int = 0
    """累计搜索次数（成功 + 失败）。"""

    successful_searches: int = 0
    """累计成功搜索次数（找到目标）。"""

    # ── 发现记录（供记忆系统读取）──
    discoveries: list = field(default_factory=list)
    """本次搜索过程中的发现记录。格式：[(tick, entity_id, x, y, target_type), ...]。
    SearchSystem 在发现目标后立即写入，不等到动作完成。
    可被 MemorySystem 读取并转化为长期记忆（record_place）。"""
