#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:action_component.py
@说明:行为组件
@时间:2026/03/13 11:16:43
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass, field
from enum import Enum, auto

from core.component import Component


class ActionType(Enum):
    # === 基础 ===
    IDLE = auto()
    WAIT = auto()

    # === 移动 ===
    MOVE_TO = auto()          # 移动到目标点
    MOVE_RANDOM = auto()      # 随机移动
    PATHFIND = auto()         # 路径规划（可选拆分）

    # === 感知 ===
    LOOK_AROUND = auto()      # 环顾
    SCAN = auto()             # 扫描环境
    SEARCH = auto()           # 主动搜索

    # === 生存 ===
    EAT = auto()
    DRINK = auto()
    SLEEP = auto()
    REST = auto()

    # === 资源 ===
    PICKUP = auto()
    DROP = auto()
    STORE = auto()
    HARVEST = auto()
    GATHER = auto()

    # === 战斗 ===
    ATTACK = auto()
    DEFEND = auto()
    FLEE = auto()
    CHASE = auto()

    # === 社交 ===
    INTERACT = auto()
    TALK = auto()
    SOCIALIZE = auto()
    TRADE = auto()

    # === 建造 ===
    BUILD = auto()
    REPAIR = auto()
    CRAFT = auto()

    # === 工作 ===
    WORK = auto()
    OPERATE = auto()

    # === 特殊 ===
    USE_ITEM = auto()
    EQUIP = auto()
    UNEQUIP = auto()


class ActionStatus(Enum):
    """
    行为执行状态（比 Task 更细粒度）
    """
    IDLE = auto()         # 空闲（未开始）
    RUNNING = auto()      # 执行中
    SUCCESS = auto()      # 成功完成
    FAILED = auto()       # 执行失败
    INTERRUPTED = auto()  # 被打断（比如被攻击/重新规划）



@dataclass
class ActionComponent(Component):
    """
    原子行为组件（由 Task 拆解执行）

    - Task 决定“做什么”
    - Action 决定“怎么做”
    """

    current_action: ActionType = ActionType.IDLE
    status: ActionStatus = ActionStatus.IDLE

    # 动作队列（行为序列）
    action_queue: list[ActionType] = field(default_factory=list)

    # 目标信息
    target_entity: int | None = None
    target_pos: tuple[int, int] | None = None

    # 执行进度（0~1）
    progress: float = 0.0

    def reset(self):
        """
        重置当前动作（用于切换或中断）
        """
        self.current_action = ActionType.IDLE
        self.status = ActionStatus.IDLE
        self.progress = 0.0
        self.target_entity = None
        self.target_pos = None


