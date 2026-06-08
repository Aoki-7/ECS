#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物学习组件

存储动物的行为学习状态，包括行为-结果关联、习惯化、敏感化等。
"""

from dataclasses import dataclass, field
from typing import Dict, List

from core.component import Component


@dataclass
class BehaviorRecord:
    """单条行为记录"""
    behavior: str  # 行为名称（如 "graze", "flee", "attack"）
    context: str   # 上下文（如 "near_predator", "food_rich"）
    outcome: float  # 结果评分 (-1.0 ~ 1.0)
    count: int = 1  # 发生次数


@dataclass(slots=True)
class AnimalLearningComponent(Component):
    """
    动物学习组件

    属性:
        behavior_records: 行为记录列表
        habituation: 习惯化程度 {stimulus: level}（0=敏感, 1=习惯化）
        sensitization: 敏感化标记 {stimulus: level}
        learning_rate: 学习速率 (0.0~1.0)
        max_records: 最大记录数
    """
    behavior_records: List[BehaviorRecord] = field(default_factory=list)
    habituation: Dict[str, float] = field(default_factory=dict)
    sensitization: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.1
    max_records: int = 50

    def record_behavior(self, behavior: str, context: str, outcome: float) -> None:
        """记录一次行为及其结果"""
        # 查找是否已有相同行为-上下文记录
        for record in self.behavior_records:
            if record.behavior == behavior and record.context == context:
                # 更新现有记录（加权平均）
                total = record.outcome * record.count + outcome
                record.count += 1
                record.outcome = total / record.count
                return

        # 新增记录
        if len(self.behavior_records) >= self.max_records:
            # 淘汰最弱的记录
            self.behavior_records.sort(key=lambda r: abs(r.outcome))
            self.behavior_records.pop(0)

        self.behavior_records.append(BehaviorRecord(behavior, context, outcome))

    def get_behavior_value(self, behavior: str, context: str) -> float:
        """获取某行为在特定上下文中的预期价值"""
        for record in self.behavior_records:
            if record.behavior == behavior and record.context == context:
                return record.outcome
        return 0.0  # 未知行为中性评价

    def update_habituation(self, stimulus: str, exposure_count: int) -> None:
        """更新习惯化程度：重复暴露导致反应减弱"""
        # 习惯化公式：level = 1 - exp(-exposure_count / 10)
        import math
        self.habituation[stimulus] = 1.0 - math.exp(-exposure_count / 10.0)

    def update_sensitization(self, stimulus: str, intensity: float) -> None:
        """更新敏感化：强烈刺激导致反应增强"""
        current = self.sensitization.get(stimulus, 0.0)
        self.sensitization[stimulus] = min(1.0, current + intensity * self.learning_rate)

    def get_best_behavior(self, context: str) -> str | None:
        """获取在特定上下文中的最佳行为"""
        relevant = [r for r in self.behavior_records if r.context == context]
        if not relevant:
            return None
        best = max(relevant, key=lambda r: r.outcome)
        return best.behavior if best.outcome > 0 else None
