#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增量存档系统

v3.0.1 新增 — P1

核心设计原则：
- 只保存自上次存档以来变化的数据
- 使用快照对比减少 I/O
- 支持增量读档（合并基础存档 + 增量）
- 自动压缩和清理
"""

import json
import os
import time
import zlib
from typing import Dict, List, Optional, Set

import logging

logger = logging.getLogger(__name__)


class IncrementalSaveSystem:
    """
    增量存档系统

    基于快照对比的增量存档，减少存档时间和存储空间。
    """

    def __init__(self, base_path: str = "saves"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self._last_snapshot: Optional[Dict] = None
        self._base_save_path: Optional[str] = None
        self._incremental_counter = 0

    def create_base_save(self, world_data: Dict, name: str = "base") -> str:
        """
        创建基础存档（完整存档）

        Returns:
            存档路径
        """
        path = os.path.join(self.base_path, f"{name}.json")
        self._save_to_file(path, world_data)
        self._base_save_path = path
        self._last_snapshot = self._flatten(world_data)
        self._incremental_counter = 0

        logger.info(f"[IncrementalSave] 基础存档创建: {path}")
        return path

    def create_incremental_save(self, world_data: Dict) -> str:
        """
        创建增量存档

        只保存与上次快照的差异。

        Returns:
            增量存档路径
        """
        if self._last_snapshot is None:
            # 没有基础存档，创建基础存档
            return self.create_base_save(world_data)

        current = self._flatten(world_data)
        diff = self._calculate_diff(self._last_snapshot, current)

        if not diff:
            logger.debug("[IncrementalSave] 无变化，跳过存档")
            return ""

        self._incremental_counter += 1
        path = os.path.join(
            self.base_path,
            f"incremental_{self._incremental_counter:04d}.json"
        )

        incremental_data = {
            "type": "incremental",
            "base": self._base_save_path,
            "counter": self._incremental_counter,
            "timestamp": time.time(),
            "diff": diff,
        }

        self._save_to_file(path, incremental_data)
        self._last_snapshot = current

        logger.info(
            f"[IncrementalSave] 增量存档 #{self._incremental_counter} "
            f"({len(diff)} 处变化)"
        )
        return path

    def load_full_state(self, base_path: str, incremental_paths: List[str]) -> Dict:
        """
        加载完整状态

        合并基础存档和所有增量。
        """
        # 加载基础
        state = self._load_from_file(base_path)
        flat_state = self._flatten(state)

        # 按顺序应用增量
        for inc_path in sorted(incremental_paths):
            inc_data = self._load_from_file(inc_path)
            if inc_data.get("type") != "incremental":
                continue

            for key, value in inc_data.get("diff", {}).items():
                if value is None:
                    flat_state.pop(key, None)
                else:
                    flat_state[key] = value

        return self._unflatten(flat_state)

    def _flatten(self, data: Dict, prefix: str = "") -> Dict[str, any]:
        """将嵌套字典扁平化"""
        result = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten(value, full_key))
            else:
                result[full_key] = value
        return result

    def _unflatten(self, flat: Dict[str, any]) -> Dict:
        """将扁平化字典还原"""
        result = {}
        for key, value in flat.items():
            parts = key.split(".")
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        return result

    def _calculate_diff(self, old: Dict, new: Dict) -> Dict:
        """计算两个字典的差异"""
        diff = {}
        all_keys = set(old.keys()) | set(new.keys())

        for key in all_keys:
            if key not in old:
                diff[key] = new[key]  # 新增
            elif key not in new:
                diff[key] = None  # 删除
            elif old[key] != new[key]:
                diff[key] = new[key]  # 修改

        return diff

    def _save_to_file(self, path: str, data: Dict) -> None:
        """保存到文件（带压缩）"""
        json_str = json.dumps(data, separators=(',', ':'))
        compressed = zlib.compress(json_str.encode('utf-8'))
        with open(path + ".gz", 'wb') as f:
            f.write(compressed)

    def _load_from_file(self, path: str) -> Dict:
        """从文件加载（带解压）"""
        gz_path = path + ".gz"
        if not os.path.exists(gz_path):
            # 尝试无压缩版本
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}

        with open(gz_path, 'rb') as f:
            compressed = f.read()
        json_str = zlib.decompress(compressed).decode('utf-8')
        return json.loads(json_str)

    def cleanup_old_incrementals(self, keep_count: int = 10) -> int:
        """
        清理旧增量存档

        Args:
            keep_count: 保留最近的增量数量

        Returns:
            删除的文件数
        """
        files = sorted([
            f for f in os.listdir(self.base_path)
            if f.startswith("incremental_") and f.endswith(".json.gz")
        ])

        to_delete = files[:-keep_count] if len(files) > keep_count else []
        deleted = 0
        for f in to_delete:
            os.remove(os.path.join(self.base_path, f))
            deleted += 1

        if deleted > 0:
            logger.info(f"[IncrementalSave] 清理 {deleted} 个旧增量存档")

        return deleted

    def get_save_info(self) -> Dict:
        """获取存档信息"""
        info = {
            "base_path": self._base_save_path,
            "incremental_count": self._incremental_counter,
            "total_size_mb": 0.0,
        }

        for f in os.listdir(self.base_path):
            path = os.path.join(self.base_path, f)
            if os.path.isfile(path):
                info["total_size_mb"] += os.path.getsize(path) / (1024 * 1024)

        return info
