#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快照服务 — 业务逻辑层

提供快照的序列化/反序列化:
    - save: 保存当前 World 状态
    - load: 加载快照到 World
    - list: 获取快照列表
    - delete: 删除快照

版本: v4.0
"""

import pickle
from typing import List, Optional

from db.repositories.snapshot_repository import SnapshotRepository
from db.models.snapshot import Snapshot
from api.dependencies import WorldManager


class SnapshotService:
    """快照服务"""

    @staticmethod
    def save(name: str, description: Optional[str] = None) -> Snapshot:
        """保存当前 World 状态"""
        manager = WorldManager()
        world = manager.get_world()
        
        # 序列化 World 状态
        world_data = pickle.dumps(world)
        stats = str(world.get_stats())
        
        snapshot = Snapshot(
            name=name,
            description=description,
            world_data=world_data,
            stats=stats,
        )
        
        return SnapshotRepository.create(snapshot)

    @staticmethod
    def load(snapshot_id: int) -> bool:
        """加载快照到 World"""
        snapshot = SnapshotRepository.get_by_id(snapshot_id)
        if not snapshot:
            return False
        
        # 反序列化 World 状态
        world = pickle.loads(snapshot.world_data)
        
        # 替换当前 World
        manager = WorldManager()
        manager._world = world
        
        return True

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> List[dict]:
        """获取快照列表"""
        snapshots = SnapshotRepository.list_all(limit, offset)
        return [s.to_dict() for s in snapshots]

    @staticmethod
    def get_by_id(snapshot_id: int) -> Optional[Snapshot]:
        """根据 ID 获取快照"""
        return SnapshotRepository.get_by_id(snapshot_id)

    @staticmethod
    def delete(snapshot_id: int) -> bool:
        """删除快照"""
        return SnapshotRepository.delete(snapshot_id)

    @staticmethod
    def count() -> int:
        """获取快照数量"""
        return SnapshotRepository.count()