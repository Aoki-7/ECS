#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物需求组件

存储动物的基本生理需求状态，驱动行为决策。
所有值域为 0.0~1.0，1.0 表示需求极度强烈。
"""

from dataclasses import dataclass

from core.component import Component


@dataclass(slots=True)
class AnimalNeedsComponent(Component):
    """
    动物需求组件

    属性:
        hunger: 饥饿度 (0=饱足, 1=极度饥饿)
        thirst: 口渴度 (0=不渴, 1=极度口渴)
        sleepiness: 困倦度 (0=清醒, 1=极度困倦)
        fear: 恐惧度 (0=安全, 1=极度恐惧)
        reproductive_urge: 繁殖欲望 (0=无, 1=强烈)
        last_satisfied: 上次满足需求的时间戳 (世界小时)
    """
    hunger: float = 0.0
    thirst: float = 0.0
    sleepiness: float = 0.0
    fear: float = 0.0
    reproductive_urge: float = 0.0
    last_satisfied: float = 0.0

    def get_dominant_need(self) -> str:
        """返回当前最强烈的需求名称"""
        needs = {
            "hunger": self.hunger,
            "thirst": self.thirst,
            "sleepiness": self.sleepiness,
            "fear": self.fear,
            "reproductive_urge": self.reproductive_urge,
        }
        return max(needs, key=needs.get)

    def is_critical(self, threshold: float = 0.8) -> bool:
        """是否有任何需求达到临界值"""
        return any(
            v >= threshold
            for v in [self.hunger, self.thirst, self.sleepiness, self.fear]
        )
