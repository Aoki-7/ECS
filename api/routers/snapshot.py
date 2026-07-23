#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snapshot API 路由 (更新版)

使用数据库服务:
    - POST /snapshot/save    : 保存快照
    - POST /snapshot/load    : 加载快照
    - GET  /snapshot/list    : 快照列表
    - GET  /snapshot/{id}    : 快照详情
    - DELETE /snapshot/{id}  : 删除快照

版本: v4.0
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from api.dependencies import get_world_manager, WorldManager
from api.schemas.snapshot import SnapshotCreate, SnapshotInfo
from db.services.snapshot_service import SnapshotService

router = APIRouter(prefix="/snapshot", tags=["Snapshot"])


@router.post("/save")
async def save_snapshot(
    data: SnapshotCreate,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    保存快照
    
    Args:
        data: 快照信息 (名称/描述)
    
    Returns:
        快照 ID
    """
    snapshot = SnapshotService.save(data.name, data.description)
    
    return {
        "id": snapshot.id,
        "name": snapshot.name,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
    }


@router.post("/load/{snapshot_id}")
async def load_snapshot(
    snapshot_id: int,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    加载快照
    
    Args:
        snapshot_id: 快照 ID
    
    Returns:
        加载结果
    """
    success = SnapshotService.load(snapshot_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
    
    return {
        "id": snapshot_id,
        "loaded": True,
    }


@router.get("/list")
async def list_snapshots(
    limit: int = 100,
    offset: int = 0,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取快照列表
    
    Returns:
        快照列表
    """
    snapshots = SnapshotService.list_all(limit, offset)
    return snapshots


@router.get("/{snapshot_id}")
async def get_snapshot(
    snapshot_id: int,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取快照详情
    
    Args:
        snapshot_id: 快照 ID
    
    Returns:
        快照详情
    """
    snapshot = SnapshotService.get_by_id(snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")

    return snapshot.to_dict()


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: int,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    删除快照
    
    Args:
        snapshot_id: 快照 ID
    
    Returns:
        删除结果
    """
    success = SnapshotService.delete(snapshot_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Snapshot {snapshot_id} not found")
    
    return {
        "id": snapshot_id,
        "deleted": True,
    }