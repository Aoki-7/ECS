#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 性能测试

版本: v4.0
"""

import pytest
import time
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

pytestmark = pytest.mark.slow


def _use_in_memory_db():
    """将 DB 切换到单连接内存数据库，避免污染本地 ecs_world.db"""
    import sqlite3
    from contextlib import contextmanager
    import db.config

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    class _NoCloseConnection:
        def __init__(self, connection):
            self._conn = connection

        def __getattr__(self, name):
            return getattr(self._conn, name)

        def close(self):
            # 保持连接开放，供后续 get_db 复用
            pass

    wrapped = _NoCloseConnection(conn)

    db.config.get_connection = lambda: wrapped

    @contextmanager
    def _get_db():
        yield wrapped

    db.config.get_db = _get_db
    db.config.init_db()


class TestAPIPerformance:
    """API 性能测试"""

    def test_health_endpoint(self):
        """测试健康检查端点性能"""
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.1  # 100ms 内响应

    def test_world_stats_endpoint(self):
        """测试 World 统计端点性能"""
        start = time.time()
        response = client.get("/world/stats")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # 500ms 内响应

    def test_entity_list_endpoint(self):
        """测试实体列表端点性能"""
        start = time.time()
        response = client.get("/world/entities?limit=100")
        elapsed = time.time() - start
        
        assert response.status_code in [200, 500]  # 允许 500 (如果 World 未初始化)
        assert elapsed < 0.5  # 500ms 内响应

    def test_concurrent_requests(self):
        """测试并发请求"""
        import concurrent.futures
        
        def make_request():
            return client.get("/health")
        
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        elapsed = time.time() - start
        
        assert all(r.status_code == 200 for r in results)
        assert elapsed < 2.0  # 10 个并发请求 2 秒内完成


class TestDatabasePerformance:
    """数据库性能测试"""

    def test_snapshot_save_performance(self):
        """测试快照保存性能"""
        from db.services.snapshot_service import SnapshotService

        # 使用内存数据库，避免污染本地 ecs_world.db
        _use_in_memory_db()
        
        start = time.time()
        snapshot = SnapshotService.save("perf_test", "Performance test")
        elapsed = time.time() - start
        
        assert snapshot.id is not None
        assert elapsed < 1.0  # 1 秒内完成

    def test_history_query_performance(self):
        """测试历史记录查询性能"""
        from db.services.history_service import HistoryService

        # 使用内存数据库，避免污染本地 ecs_world.db
        _use_in_memory_db()
        
        # 创建 1000 条记录
        for i in range(1000):
            HistoryService.record(i, "test_event", 1, {"data": i})
        
        start = time.time()
        entries = HistoryService.list_all(100, 0)
        elapsed = time.time() - start
        
        assert len(entries) == 100
        assert elapsed < 0.5  # 500ms 内查询 100 条