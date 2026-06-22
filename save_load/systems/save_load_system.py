#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
SaveLoadSystem — 存档/读档系统

职责：
1. 将当前世界状态保存到 JSON 文件
2. 从 JSON 文件加载世界状态
3. 管理存档槽（自动/手动）

设计原则：
    - 仅序列化数据（Entity + Component），不序列化 System（纯逻辑）
    - 加载后 System 自动基于新组件数据恢复运行
    - 存档文件格式为 JSON（人类可读）
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from core.system import System
from core.world import World

from save_load.components.save_slot_component import SaveSlotComponent
from save_load.serializers.world_serializer import WorldSerializer

logger = logging.getLogger(__name__)


class SaveLoadSystem(System):
    """
    存档/读档系统

    priority = 1（在时间系统之后立即执行，确保存档发生在 tick 开始时）
    tick_interval = 1（每帧检查是否需要自动存档）
    """

    priority = 1
    tick_interval = 1

    # 默认存档目录
    DEFAULT_SAVE_DIR = "saves"
    # 自动存档间隔（tick 数）
    AUTOSAVE_INTERVAL = 100

    def __init__(self, save_dir: Optional[str] = None):
        super().__init__()
        self._save_dir = Path(save_dir or self.DEFAULT_SAVE_DIR)
        self._save_dir.mkdir(parents=True, exist_ok=True)

    def on_add(self, world: World):
        """自动挂载 SaveSlotComponent"""
        if world.get_world_component(SaveSlotComponent) is None:
            slot = SaveSlotComponent()
            world_entity = world.get_world_entity()
            if world_entity is not None:
                world.add_component(world_entity, slot)
            else:
                world_entity = world.create_entity()
                world.add_component(world_entity, slot)
                world.set_world_entity(world_entity)

    def on_remove(self, world: World):
        """系统移除时清理 SaveSlotComponent"""
        we = world.get_world_entity()
        if we:
            comp = world.get_component(we, SaveSlotComponent)
            if comp:
                we.remove_component(SaveSlotComponent)

    def update(self, world: World, dt: float = 1.0) -> None:
        """检查是否需要自动存档"""
        try:
            super().update(world, dt)
        except Exception:
            pass
        # 每 AUTOSAVE_INTERVAL tick 自动存档一次
        if world.tick_count > 0 and world.tick_count % self.AUTOSAVE_INTERVAL == 0:
            try:
                self.save(world, slot_name="autosave")
            except Exception as e:
                logger.warning(f"[SaveLoad] 自动存档失败: {e}")

    # ── 存档 API ──

    def save(self, world: World, slot_name: str = "manual") -> str:
        """
        保存世界状态到指定存档槽

        Returns:
            存档文件的完整路径
        """
        from datetime import datetime

        data = WorldSerializer.serialize(world)

        slot = world.get_world_component(SaveSlotComponent)
        if slot is None:
            slot = SaveSlotComponent()
            world_entity = world.get_world_entity()
            if world_entity is not None:
                world.add_component(world_entity, slot)
            else:
                world_entity = world.create_entity()
                world.add_component(world_entity, slot)
                world.set_world_entity(world_entity)

        slot.slot_name = slot_name
        slot.save_time = datetime.now().isoformat()
        slot.tick_count = world.tick_count
        slot.entity_count = len(world.entities)

        # 将元数据也写入存档
        data["_meta"] = {
            "slot_name": slot_name,
            "save_time": slot.save_time,
            "tick_count": slot.tick_count,
            "entity_count": slot.entity_count,
        }

        filepath = self._save_dir / f"{slot_name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"[SaveLoad] 存档已保存: {filepath} (entities={slot.entity_count}, ticks={slot.tick_count})")
        return str(filepath)

    def load(self, world: World, slot_name: str = "autosave") -> bool:
        """
        从指定存档槽加载世界状态

        Returns:
            是否加载成功
        """
        filepath = self._save_dir / f"{slot_name}.json"
        if not filepath.exists():
            logger.warning(f"[SaveLoad] 存档不存在: {filepath}")
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"[SaveLoad] 读取存档失败: {e}")
            return False

        WorldSerializer.deserialize(world, data)

        # 恢复存档元数据
        meta = data.get("_meta", {})
        slot = world.get_world_component(SaveSlotComponent)
        if slot is None:
            slot = SaveSlotComponent()
            world.get_world_entity().add_component(slot)
        slot.slot_name = meta.get("slot_name", slot_name)
        slot.save_time = meta.get("save_time")
        slot.tick_count = meta.get("tick_count", 0)
        slot.entity_count = meta.get("entity_count", 0)

        logger.info(f"[SaveLoad] 存档已加载: {filepath} (entities={slot.entity_count}, ticks={slot.tick_count})")
        return True

    def list_saves(self) -> list:
        """列出所有存档文件"""
        saves = []
        for f in self._save_dir.glob("*.json"):
            saves.append({
                "name": f.stem,
                "path": str(f),
                "size": f.stat().st_size,
            })
        return saves
