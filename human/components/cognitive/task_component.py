#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:task_component.py
@说明:任务组件
@时间:2026/04/01 13:58:18
@作者:Sherry
@版本:1.0
'''

from dataclasses import dataclass
from enum import Enum, auto

from core.component import Component


class TaskType(Enum):
    """
    任务类型枚举
    """
    IDLE = auto()
    FIND_FOOD = auto()
    DRINK_WATER = auto()
    GO_HOME = auto()
    SLEEP = auto()
    EXPLORE = auto()
    FIGHT = auto()
    FIND_PARTNER = auto()
    MOVE_TO_TARGET = auto()
    EAT_FOOD = auto()


class TaskStatus(Enum):
    """
    任务状态枚举
    """
    IDLE = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()


@dataclass(slots=True)
class TaskComponent(Component):
    """
    中层任务（由规划系统生成）

    任务是对高层意图的具体化，包含执行细节和状态流转。

    示例流程：
        意图：EAT
            -> 任务：FIND_FOOD
            -> 任务：MOVE_TO_TARGET
            -> 任务：EAT_FOOD
    """
    task: TaskType = TaskType.IDLE
    status: TaskStatus = TaskStatus.IDLE