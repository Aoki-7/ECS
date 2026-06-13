#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic 模型 — System 相关

版本: v4.0
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class SystemStatus(BaseModel):
    """系统状态"""
    running: bool = False
    paused: bool = False
    stats: Dict[str, Any] = {}


class SystemInfo(BaseModel):
    """系统信息"""
    name: str
    enabled: bool = True
    tick_interval: int = 1
    priority: int = 0


class RunConfig(BaseModel):
    """运行配置"""
    steps: int = 1
    dt: float = 1.0
    realtime: bool = False
