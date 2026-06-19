#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic 模型 — Snapshot 相关

版本: v4.0
"""

from pydantic import BaseModel
from typing import Optional


class SnapshotCreate(BaseModel):
    """创建快照请求"""
    name: str
    description: Optional[str] = None


class SnapshotInfo(BaseModel):
    """快照信息"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: str
    size: int = 0
