#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
DeadTagComponent — 死亡状态标记组件

DeathSystem 执行完死亡流程后挂载此组件，将实体状态从 Alive 显式标记为 Dead。
后续系统（CorpseSystem、统计系统等）通过查询此组件识别已死亡实体。
"""

from dataclasses import dataclass
from core.component import Component


@dataclass
class DeadTagComponent(Component):
    """
    死亡状态标记。一旦挂载，表示该实体已完成死亡流程。

    与 PendingDeathComponent 的区别：
        - PendingDeath: "即将死亡"（业务系统挂载）
        - DeadTag: "已经死亡"（DeathSystem 挂载）
    """
    # 死亡是否已被处理（防止重复执行）
    processed: bool = False
