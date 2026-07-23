#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic 模型 — Entity 相关

版本: v4.0
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class EntityCreate(BaseModel):
    """创建实体请求"""
    components: Dict[str, Dict[str, Any]] = {}


class EntityUpdate(BaseModel):
    """更新实体请求"""
    components: Dict[str, Dict[str, Any]] = {}


class EntityDetail(BaseModel):
    """实体详情"""
    id: int
    generation: int
    components: Dict[str, Any] = {}