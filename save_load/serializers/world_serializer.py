#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
WorldSerializer — 世界状态序列化器

将 World 的 entities 和 components 序列化为可 JSON 化的字典。
不序列化 System（系统为纯逻辑，状态由组件重建后自动恢复）。
"""

import json
import logging
from typing import Dict, Any, List

from core.world import World
from core.entity import Entity
from core.component import Component
from core.component_serializer import ComponentSerializer

logger = logging.getLogger(__name__)


class WorldSerializer:
    """世界状态序列化器"""

    @staticmethod
    def serialize(world: World) -> Dict[str, Any]:
        """
        将 World 序列化为字典

        序列化内容：
        - entities: 所有实体列表（id + generation）
        - components: 按组件类型分组的组件数据
        - world_entity: 世界实体及其组件
        - tick_count: 当前 tick 计数
        """
        data = {
            "tick_count": world.tick_count,
            "entities": [],
            "components": {},
            "world_entity": None,
        }

        # 序列化普通实体
        for entity in world.entities.values():
            data["entities"].append(entity.to_dict())

        # 序列化组件（按类型分组）
        # v4.0: 优先使用 ComponentSerializer
        for comp_type, comp_dict in world.components.items():
            type_name = f"{comp_type.__module__}.{comp_type.__name__}"
            data["components"][type_name] = {}
            for entity_id, comp in comp_dict.items():
                try:
                    # 尝试使用 ComponentSerializer
                    if ComponentSerializer.is_registered(type_name):
                        data["components"][type_name][str(entity_id)] = ComponentSerializer.serialize(comp)
                    else:
                        # 回退到旧方式
                        data["components"][type_name][str(entity_id)] = comp.to_dict()
                except Exception as e:
                    logger.warning(f"[Save] 序列化组件 {type_name} 失败 (entity={entity_id}): {e}")

        # 序列化 world_entity
        if world._world_entity is not None:
            we = world._world_entity
            data["world_entity"] = {
                "entity": we.to_dict(),
                "components": {}
            }
            # WorldEntity 的组件存储在 _components 中
            for comp_type, comp in we._components.items():
                type_name = f"{comp_type.__module__}.{comp_type.__name__}"
                try:
                    # v4.0: 优先使用 ComponentSerializer
                    if ComponentSerializer.is_registered(type_name):
                        data["world_entity"]["components"][type_name] = ComponentSerializer.serialize(comp)
                    else:
                        data["world_entity"]["components"][type_name] = comp.to_dict()
                except Exception as e:
                    logger.warning(f"[Save] 序列化 world_entity 组件 {type_name} 失败: {e}")

        return data

    @staticmethod
    def deserialize(world: World, data: Dict[str, Any]) -> None:
        """
        将字典反序列化恢复到 World

        警告：这会清空当前 World 的所有状态！
        """
        # 清空当前状态（兼容 v3.9 和 v4.0）
        world.components.clear()
        world._query_cache.clear()
        if hasattr(world, '_system_cache'):
            world._system_cache.clear()

        world.tick_count = data.get("tick_count", 0)

        # 重建实体
        entity_map = {}  # old_id -> new Entity
        for entity_data in data.get("entities", []):
            entity = Entity(entity_data["id"], entity_data["generation"])
            # v4.0: 使用 EntityManager
            if hasattr(world, '_entity_manager'):
                world._entity_manager._entities[entity.id] = entity
            else:
                world.entities[entity.id] = entity
            entity_map[entity_data["id"]] = entity

        # 重建组件
        for type_name, comp_dict in data.get("components", {}).items():
            try:
                comp_type = WorldSerializer._resolve_type(type_name)
            except Exception as e:
                logger.warning(f"[Load] 无法解析组件类型 {type_name}: {e}")
                continue

            # v4.0: 使用 ArchetypeStore (通过 World.add_component)
            if hasattr(world, '_archetype_store'):
                for entity_id_str, comp_data in comp_dict.items():
                    entity_id = int(entity_id_str)
                    entity = entity_map.get(entity_id)
                    if entity is None:
                        logger.warning(f"[Load] 组件 {type_name} 引用了不存在的实体 {entity_id}")
                        continue
                    try:
                        # v4.0: 优先使用 ComponentSerializer
                        if isinstance(comp_data, dict) and "__type__" in comp_data:
                            comp = ComponentSerializer.deserialize(comp_data)
                        else:
                            # 迁移旧版本数据
                            from save_load.component_migrator import migrate_component_data
                            comp_data = migrate_component_data(type_name, comp_data)
                            comp = comp_type.from_dict(comp_data)
                        
                        if comp is not None:
                            world.add_component(entity, comp)
                    except Exception as e:
                        logger.warning(f"[Load] 反序列化组件 {type_name} 失败 (entity={entity_id}): {e}")
            elif hasattr(world, '_component_store'):
                for entity_id_str, comp_data in comp_dict.items():
                    entity_id = int(entity_id_str)
                    entity = entity_map.get(entity_id)
                    if entity is None:
                        logger.warning(f"[Load] 组件 {type_name} 引用了不存在的实体 {entity_id}")
                        continue
                    try:
                        if isinstance(comp_data, dict) and "__type__" in comp_data:
                            comp = ComponentSerializer.deserialize(comp_data)
                        else:
                            from save_load.component_migrator import migrate_component_data
                            comp_data = migrate_component_data(type_name, comp_data)
                            comp = comp_type.from_dict(comp_data)
                        
                        if comp is not None:
                            world._component_store.add_component(entity, comp)
                    except Exception as e:
                        logger.warning(f"[Load] 反序列化组件 {type_name} 失败 (entity={entity_id}): {e}")
            else:
                # v3.9 兼容路径
                world.components[comp_type] = {}
                world._component_entities[comp_type] = set()

                for entity_id_str, comp_data in comp_dict.items():
                    entity_id = int(entity_id_str)
                    entity = entity_map.get(entity_id)
                    if entity is None:
                        logger.warning(f"[Load] 组件 {type_name} 引用了不存在的实体 {entity_id}")
                        continue
                    try:
                        if isinstance(comp_data, dict) and "__type__" in comp_data:
                            comp = ComponentSerializer.deserialize(comp_data)
                        else:
                            from save_load.component_migrator import migrate_component_data
                            comp_data = migrate_component_data(type_name, comp_data)
                            comp = comp_type.from_dict(comp_data)
                        
                        if comp is not None:
                            world.components[comp_type][entity_id] = comp
                            world._component_entities[comp_type].add(entity_id)
                    except Exception as e:
                        logger.warning(f"[Load] 反序列化组件 {type_name} 失败 (entity={entity_id}): {e}")

        # 重建 world_entity
        world_entity_data = data.get("world_entity")
        if world_entity_data:
            from world.world_entity import WorldEntity
            we = WorldEntity()
            for type_name, comp_data in world_entity_data.get("components", {}).items():
                try:
                    comp_type = WorldSerializer._resolve_type(type_name)
                    comp = comp_type.from_dict(comp_data)
                    we.add_component(comp)
                except Exception as e:
                    logger.warning(f"[Load] 反序列化 world_entity 组件 {type_name} 失败: {e}")
            world.set_world_entity(we)

    @staticmethod
    def _resolve_type(type_name: str):
        """根据模块路径.类名字符串解析类型"""
        module_path, class_name = type_name.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)
