#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:intent_component.py
@说明:意图组件
@时间:2026/04/01 13:57:45
@作者:Sherry
@版本:1.0
'''


# 生存（Survival）
# 安全（Safety）
# 发展（Growth）
# 社会（Social）


from enum import Enum, auto


class IntentType(Enum):
    """
    高层意图类型（驱动力）
    """

    # === 基础 ===
    IDLE = auto()
    EXPLORE = auto()          # 探索环境

    # === 生存 ===
    EAT = auto()              # 进食（解决饥饿）
    DRINK = auto()            # 饮水
    SLEEP = auto()            # 睡眠
    REST = auto()             # 休息（恢复体力）

    # === 安全 ===
    FLEE = auto()             # 逃避危险
    HIDE = auto()             # 躲藏
    HEAL = auto()             # 恢复生命

    # === 资源 ===
    COLLECT = auto()          # 收集资源
    STORE = auto()            # 存储资源

    # === 发展 ===
    WORK = auto()             # 工作
    BUILD = auto()            # 建造
    CRAFT = auto()            # 制造

    # === 战斗 ===
    ATTACK = auto()           # 主动攻击
    DEFEND = auto()           # 防御

    # === 社交 ===
    SOCIALIZE = auto()        # 社交
    PAIR = auto()             # 配对
    TRADE = auto()            # 交易
    COMMUNICATE = auto()      # 沟通

    # === 特殊 ===
    FOLLOW = auto()           # 跟随某个目标（高层意图）
    INVESTIGATE = auto()      # 调查（对异常感兴趣）
    

    


from dataclasses import dataclass, field
from typing import Any
from core.component import Component


@dataclass(slots=True)
class IntentComponent(Component):
    """
    高层意图组件
    """

    intent: IntentType = IntentType.IDLE

    # 优先级（用于多意图竞争）
    priority: float = 0.0

    # 意图目标（比 action 更抽象）
    target_entity: int | None = None
    target_pos: tuple[int, int] | None = None

    # 参数（关键扩展点）
    params: dict[str, Any] = field(default_factory=dict)

    # 是否锁定（防止频繁切换）
    locked: bool = False

    # 用于行为可视化的字段
    current_action: Any = None
    cooperation_partners: list[int] = field(default_factory=list)
    goal_type: str | None = None