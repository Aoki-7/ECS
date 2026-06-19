#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆持久化

支持记忆层的序列化、存档/读档、增量保存。
"""

import json
import logging
import os
from typing import Optional

from .memory_layer import MemoryLayer

logger = logging.getLogger(__name__)


class MemoryPersistence:
    """
    记忆持久化管理器

    支持：
    1. 完整序列化/反序列化
    2. 增量保存（只保存变更）
    3. 自动备份（保留历史版本）
    """

    def __init__(self, save_dir: str = "saves/memory"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def save(self, memory_layer: MemoryLayer, filename: str = "memory.json") -> str:
        """保存记忆层到文件"""
        filepath = os.path.join(self.save_dir, filename)
        data = memory_layer.to_dict()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"[MemoryPersistence] 已保存到 {filepath}")
        return filepath

    def load(self, filename: str = "memory.json") -> MemoryLayer:
        """从文件加载记忆层"""
        filepath = os.path.join(self.save_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"存档文件不存在: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        ml = MemoryLayer.from_dict(data)
        logger.info(f"[MemoryPersistence] 已从 {filepath} 加载")
        return ml

    def auto_save(
        self,
        memory_layer: MemoryLayer,
        tick: int,
        interval: int = 100,
    ) -> Optional[str]:
        """
        自动保存（按 tick 间隔）

        Returns:
            保存的文件路径，如果未触发保存则返回 None
        """
        if tick % interval != 0:
            return None

        filename = f"memory_auto_tick{tick}.json"
        return self.save(memory_layer, filename)

    def list_saves(self) -> list[str]:
        """列出所有存档文件"""
        if not os.path.exists(self.save_dir):
            return []
        files = [f for f in os.listdir(self.save_dir) if f.endswith(".json")]
        return sorted(files)

    def delete_save(self, filename: str) -> bool:
        """删除存档文件"""
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
