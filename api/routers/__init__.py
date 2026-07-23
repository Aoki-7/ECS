#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由包初始化

版本: v4.0
"""

from .world import router as world_router
from .entity import router as entity_router
from .system import router as system_router
from .snapshot import router as snapshot_router
from .history import router as history_router

__all__ = [
    "world_router",
    "entity_router",
    "system_router",
    "snapshot_router",
    "history_router",
]