#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic 模型 — World 相关

版本: v4.0
"""

from pydantic import BaseModel
from typing import Dict, List, Any, Optional


class WorldStats(BaseModel):
    """World 统计信息"""
    entities: Dict[str, int] = {}
    components: Dict[str, Any] = {}
    systems: Dict[str, int] = {}


class QueryResult(BaseModel):
    """查询结果"""
    query: List[str]
    count: int
    results: List[Dict[str, Any]]


class ArchetypeInfo(BaseModel):
    """Archetype 信息"""
    id: int
    component_types: List[str]
    entity_count: int
