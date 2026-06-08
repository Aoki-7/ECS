#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
TickInterval — 系统执行间隔常量

集中管理所有 ECS System 的 tick_interval 值，避免魔法值分散在 100+ 个文件中。

规则：
    - tick_interval = 1  表示每帧执行
    - tick_interval = 2  表示隔 1 帧执行
    - tick_interval = N  表示每 N 帧执行一次
    - 数值越大，执行频率越低
"""


class TickInterval:
    """系统执行间隔枚举"""

    # 高频 — 每帧执行（关键响应系统）
    EVERY_FRAME = 1

    # 较快 — 隔 1 帧执行（环境基础同步）
    FAST = 2

    # 中频 — 每 5 帧执行（事件、归档、部分认知）
    MODERATE_FAST = 5

    # 中频 — 每 10 帧执行（社交、身份、健康护理）
    MODERATE = 10

    # 特定 — 每 15 帧执行（捕食系统）
    PREDATION = 15

    # 标准 — 每 20 帧执行（最常见的默认值）
    STANDARD = 20

    # 较低频 — 每 30 帧执行（营养级）
    SLOW = 30

    # 低频 — 每 50 帧执行（种群动态、种子扩散）
    VERY_SLOW = 50

    # 极低频 — 每 80 帧执行（物种形成）
    RARE = 80

    # 极低频 — 每 100 帧执行（生态平衡）
    VERY_RARE = 100
