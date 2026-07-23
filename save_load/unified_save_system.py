#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
统一存档系统

整合 World 序列化和 MemoryLayer 持久化。
提供统一的存档/读档接口。

存档格式（JSON）:
{
    "version": "2.3",
    "world": { ... WorldSerializer 数据 ... },
    "memory_layer": { ... MemoryLayer.to_dict() ... },
    "meta": { ... 元数据 ... }
}
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from core.system import System
from core.world import World

from save_load.serializers.world_serializer import WorldSerializer
from memory_layer import MemoryLayer

logger = logging.getLogger(__name__)


class UnifiedSaveSystem(System):
    """
    统一存档系统

    整合：
    1. World 状态（Entity + Component）
    2. MemoryLayer 状态（Concept + MemoryInstance）
    3. 存档元数据

    priority = 1（在时间系统之后立即执行）
    tick_interval = 1（每帧检查自动存档）
    """

    priority = 1
    tick_interval = 1
    SAVE_VERSION = "2.3"
    DEFAULT_SAVE_DIR = "saves"
    AUTOSAVE_INTERVAL = 100

    def __init__(self, save_dir: Optional[str] = None):
        super().__init__()
        self._save_dir = Path(save_dir or self.DEFAULT_SAVE_DIR)
        self._save_dir.mkdir(parents=True, exist_ok=True)

    def update(self, world: World, dt: float = 1.0) -> None:
        """检查是否需要自动存档"""
        if world.tick_count > 0 and world.tick_count % self.AUTOSAVE_INTERVAL == 0:
            self.save(world, slot_name="autosave")

    def save(self, world: World, slot_name: str = "manual") -> str:
        """
        统一存档：保存 World + MemoryLayer

        Returns:
            存档文件路径
        """
        from datetime import datetime

        # 1. 序列化 World
        world_data = WorldSerializer.serialize(world)

        # 2. 序列化 MemoryLayer
        memory_layer = world.get_memory_layer()
        memory_data = memory_layer.to_dict() if memory_layer else {}

        # 3. 组装统一存档
        data = {
            "version": self.SAVE_VERSION,
            "world": world_data,
            "memory_layer": memory_data,
            "meta": {
                "slot_name": slot_name,
                "save_time": datetime.now().isoformat(),
                "tick_count": world.tick_count,
                "entity_count": len(world.entities),
                "memory_concepts": len(memory_data.get("concepts", {})) if memory_data else 0,
                "memory_instances": len(memory_data.get("memories", {})) if memory_data else 0,
            }
        }

        # 4. 写入文件
        filepath = self._save_dir / f"{slot_name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(
            f"[UnifiedSave] 存档已保存: {filepath} "
            f"(entities={data['meta']['entity_count']}, "
            f"concepts={data['meta']['memory_concepts']}, "
            f"memories={data['meta']['memory_instances']})"
        )
        return str(filepath)

    def load(self, world: World, slot_name: str = "autosave") -> bool:
        """
        统一读档：恢复 World + MemoryLayer

        Returns:
            是否加载成功
        """
        filepath = self._save_dir / f"{slot_name}.json"
        if not filepath.exists():
            logger.warning(f"[UnifiedSave] 存档不存在: {filepath}")
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"[UnifiedSave] 读取存档失败: {e}")
            return False

        # 版本检查
        version = data.get("version", "unknown")
        if version != self.SAVE_VERSION:
            logger.warning(f"[UnifiedSave] 存档版本不匹配: {version} vs {self.SAVE_VERSION}")
            # 未来可添加版本迁移逻辑

        # 1. 恢复 World
        world_data = data.get("world", {})
        WorldSerializer.deserialize(world, world_data)

        # 2. 恢复 MemoryLayer
        memory_data = data.get("memory_layer", {})
        if memory_data:
            memory_layer = world.get_memory_layer()
            if memory_layer is not None:
                memory_layer.from_dict(memory_data)

        meta = data.get("meta", {})
        logger.info(
            f"[UnifiedSave] 存档已加载: {filepath} "
            f"(entities={meta.get('entity_count', 0)}, "
            f"concepts={meta.get('memory_concepts', 0)}, "
            f"memories={meta.get('memory_instances', 0)})"
        )
        return True

    def list_saves(self) -> list:
        """列出所有存档"""
        saves = []
        for f in self._save_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                meta = data.get("meta", {})
                saves.append({
                    "name": f.stem,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "version": data.get("version", "unknown"),
                    "tick_count": meta.get("tick_count", 0),
                    "entity_count": meta.get("entity_count", 0),
                    "save_time": meta.get("save_time", "unknown"),
                })
            except Exception:
                saves.append({
                    "name": f.stem,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "version": "unknown",
                })
        return sorted(saves, key=lambda x: x.get("save_time", ""), reverse=True)

    def delete_save(self, slot_name: str) -> bool:
        """删除存档"""
        filepath = self._save_dir / f"{slot_name}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False