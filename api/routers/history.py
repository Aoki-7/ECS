#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
History API 路由

提供历史记录查询:
    - GET /history         : 历史记录列表
    - GET /history/timeline : 时间轴
    - GET /history/events   : 事件列表

版本: v4.0
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from api.dependencies import get_world_manager, WorldManager
from api.schemas.history import HistoryEntry, TimelineEvent
from db.services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/")
async def get_history(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    entity_id: Optional[int] = None,
    event_type: Optional[str] = None,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取历史记录
    
    Args:
        limit: 每页数量
        offset: 偏移量
        entity_id: 实体 ID 过滤
        event_type: 事件类型过滤
    
    Returns:
        历史记录列表
    """
    entries = HistoryService.list_all(limit, offset)
    
    # 过滤
    if entity_id is not None:
        entries = [e for e in entries if e.get("entity_id") == entity_id]
    if event_type is not None:
        entries = [e for e in entries if e.get("event_type") == event_type]
    
    return entries


@router.get("/timeline")
async def get_timeline(
    start_tick: int = Query(0, ge=0),
    end_tick: Optional[int] = None,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取时间轴
    
    Args:
        start_tick: 起始 tick
        end_tick: 结束 tick
    
    Returns:
        时间轴事件
    """
    entries = HistoryService.get_timeline(start_tick, end_tick)
    return entries


@router.get("/events")
async def get_events(
    tick: Optional[int] = None,
    entity_id: Optional[int] = None,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取事件列表
    
    Args:
        tick: tick 过滤
        entity_id: 实体 ID 过滤
    
    Returns:
        事件列表
    """
    if tick is not None:
        entries = HistoryService.get_by_tick(tick)
    elif entity_id is not None:
        entries = HistoryService.get_by_entity(entity_id)
    else:
        entries = HistoryService.list_all(100, 0)
    
    return entries