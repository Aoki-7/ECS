#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库测试

版本: v4.0
"""

import pytest
import os
import tempfile
from db.config import init_db, get_db, DB_PATH
from db.models.snapshot import Snapshot
from db.models.history import HistoryEntry
from db.repositories.snapshot_repository import SnapshotRepository
from db.repositories.history_repository import HistoryRepository


@pytest.fixture
def temp_db():
    """临时数据库"""
    # 使用临时文件
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # 修改数据库路径
    import db.config
    original_path = db.config.DB_PATH
    db.config.DB_PATH = path
    
    init_db()
    
    yield path
    
    # 恢复路径
    db.config.DB_PATH = original_path
    
    # 清理
    if os.path.exists(path):
        os.remove(path)


class TestSnapshotRepository:
    """快照仓库测试"""

    def test_create(self, temp_db):
        """测试创建快照"""
        snapshot = Snapshot(
            name="test_snapshot",
            description="Test description",
            world_data=b"test_data",
            stats="{}",
        )
        result = SnapshotRepository.create(snapshot)
        
        assert result.id is not None
        assert result.name == "test_snapshot"

    def test_get_by_id(self, temp_db):
        """测试根据 ID 获取"""
        snapshot = Snapshot(
            name="test_snapshot",
            world_data=b"test_data",
        )
        created = SnapshotRepository.create(snapshot)
        
        found = SnapshotRepository.get_by_id(created.id)
        assert found is not None
        assert found.name == "test_snapshot"

    def test_list_all(self, temp_db):
        """测试获取所有快照"""
        for i in range(3):
            snapshot = Snapshot(
                name=f"snapshot_{i}",
                world_data=b"data",
            )
            SnapshotRepository.create(snapshot)
        
        snapshots = SnapshotRepository.list_all()
        assert len(snapshots) == 3

    def test_delete(self, temp_db):
        """测试删除快照"""
        snapshot = Snapshot(
            name="to_delete",
            world_data=b"data",
        )
        created = SnapshotRepository.create(snapshot)
        
        success = SnapshotRepository.delete(created.id)
        assert success is True
        
        found = SnapshotRepository.get_by_id(created.id)
        assert found is None


class TestHistoryRepository:
    """历史记录仓库测试"""

    def test_create(self, temp_db):
        """测试创建历史记录"""
        entry = HistoryEntry(
            tick=10,
            entity_id=1,
            event_type="test_event",
            event_data={"key": "value"},
        )
        result = HistoryRepository.create(entry)
        
        assert result.id is not None
        assert result.tick == 10

    def test_get_by_tick(self, temp_db):
        """测试根据 tick 获取"""
        for i in range(3):
            entry = HistoryEntry(
                tick=10,
                event_type=f"event_{i}",
            )
            HistoryRepository.create(entry)
        
        entries = HistoryRepository.get_by_tick(10)
        assert len(entries) == 3

    def test_get_by_entity(self, temp_db):
        """测试根据实体 ID 获取"""
        entry = HistoryEntry(
            tick=10,
            entity_id=42,
            event_type="entity_event",
        )
        HistoryRepository.create(entry)
        
        entries = HistoryRepository.get_by_entity(42)
        assert len(entries) == 1
        assert entries[0].event_type == "entity_event"

    def test_get_timeline(self, temp_db):
        """测试获取时间轴"""
        for i in range(5):
            entry = HistoryEntry(
                tick=i,
                event_type=f"event_{i}",
            )
            HistoryRepository.create(entry)
        
        entries = HistoryRepository.get_timeline(1, 3)
        assert len(entries) == 3

    def test_count(self, temp_db):
        """测试计数"""
        for i in range(5):
            entry = HistoryEntry(
                tick=i,
                event_type="test",
            )
            HistoryRepository.create(entry)
        
        count = HistoryRepository.count()
        assert count == 5
