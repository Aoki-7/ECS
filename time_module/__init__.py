#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间系统模块 — 世界时间推进与调度

职责：
    - TimeComponent: 存储世界时间状态（年、日、时、总步数）
    - TimeSystem: 每步推进世界时间，支持时间倍率控制
    - 为环境系统（季节、太阳位置、辐射）提供时间输入
    - 为生物系统（生命周期、生长积温）提供时间基准

时间尺度：
    - 1 步 = 1 小时（默认）
    - 1 日 = 24 步
    - 1 年 = 360 日（简化历法）

调度优先级：
    - TimeSystem 通常以极高优先级运行（priority ~5）
    - 确保所有依赖时间的系统在同一帧内看到一致的时间状态
"""

from .time_component import TimeComponent
from .time_system import TimeSystem

__all__ = [
    "TimeComponent",
    "TimeSystem",
]
