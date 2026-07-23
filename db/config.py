#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置 — SQLite 连接管理

提供:
    - 数据库连接池
    - 表初始化
    - 迁移支持

版本: v4.0
"""

import sqlite3
import os
from typing import Optional
from contextlib import contextmanager

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'ecs_world.db')

# 确保数据目录存在
os.makedirs(DB_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """初始化数据库表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 快照表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                world_data BLOB NOT NULL,
                stats TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tick INTEGER NOT NULL,
                entity_id INTEGER,
                event_type TEXT NOT NULL,
                event_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_tick ON history(tick)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_entity ON history(entity_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_type ON history(event_type)
        ''')
        
        conn.commit()
        print(f"Database initialized at {DB_PATH}")


if __name__ == '__main__':
    init_db()