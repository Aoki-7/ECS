#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
行为组件

v3.9 迁移：从 core/components/ 移回 human/components/action/
保持 core 层纯粹性。
"""

from dataclasses import dataclass, field
from enum import Enum, auto

from core.component import Component


class ActionType(Enum):
    """行为类型枚举"""
    # 基础
    IDLE = auto()
    WAIT = auto()

    # 移动
    MOVE_TO = auto()
    MOVE_RANDOM = auto()
    PATHFIND = auto()

    # 感知
    LOOK_AROUND = auto()
    SCAN = auto()
    SEARCH = auto()

    # 生存
    EAT = auto()
    DRINK = auto()
    SLEEP = auto()
    REST = auto()

    # 资源
    PICKUP = auto()
    DROP = auto()
    STORE = auto()
    HARVEST = auto()
    GATHER = auto()
    PLANT = auto()

    # 战斗
    ATTACK = auto()
    DEFEND = auto()
    FLEE = auto()
    CHASE = auto()

    # 社交
    INTERACT = auto()
    TALK = auto()
    SOCIALIZE = auto()
    TRADE = auto()

    # 建造
    BUILD = auto()
    REPAIR = auto()
    CRAFT = auto()

    # 工作
    WORK = auto()
    OPERATE = auto()

    # 特殊
    USE_ITEM = auto()
    EQUIP = auto()
    UNEQUIP = auto()


class ActionStatus(Enum):
    """行为执行状态"""
    IDLE = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    INTERRUPTED = auto()


@dataclass(slots=True)
class ActionComponent(Component):
    """原子行为组件（由 Task 拆解执行）"""

    current_action: ActionType = ActionType.IDLE
    status: ActionStatus = ActionStatus.IDLE
    action_queue: list[ActionType] = field(default_factory=list)
    target_entity: int | None = None
    target_pos: tuple[int, int] | None = None
    progress: float = 0.0
    _path: list = field(default_factory=list, repr=False)
    _path_index: int = field(default=0, repr=False)

    def reset(self):
        """重置当前动作"""
        self.current_action = ActionType.IDLE
        self.status = ActionStatus.IDLE
        self.progress = 0.0
        self.target_entity = None
        self.target_pos = None
        self._path = []
        self._path_index = 0
