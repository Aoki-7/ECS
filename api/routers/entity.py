#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity API 路由

提供实体 CRUD 操作:
    - GET  /entity/{entity_id}      : 获取实体详情
    - GET  /entity/{entity_id}/components : 获取实体组件
    - POST /entity                  : 创建实体
    - PUT  /entity/{entity_id}      : 更新实体
    - DELETE /entity/{entity_id}    : 删除实体

版本: v4.0
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import dataclasses

from api.dependencies import get_world_manager, WorldManager
from api.schemas.entity import EntityCreate, EntityUpdate, EntityDetail

router = APIRouter(prefix="/entity", tags=["Entity"])


def _component_to_dict(component: Any) -> Dict[str, Any]:
    """将组件实例序列化为字典"""
    if hasattr(component, "to_dict"):
        return component.to_dict()
    if dataclasses.is_dataclass(component):
        return dataclasses.asdict(component)
    return vars(component)


def _serialize_entity_components(world, entity) -> Dict[str, Any]:
    """序列化实体的所有组件"""
    components = world.get_entity_components(entity)
    return {
        comp_type.__name__: _component_to_dict(comp)
        for comp_type, comp in components.items()
    }


@router.get("/{entity_id}", response_model=EntityDetail)
async def get_entity(
    entity_id: int,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取实体详情
    
    Args:
        entity_id: 实体 ID
    
    Returns:
        实体详情 (ID, 生成号, 组件列表)
    """
    world = manager.get_world()
    
    if not world.has_entity_id(entity_id):
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    entity = world.get_entity(entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    components = _serialize_entity_components(world, entity)

    return {
        "id": entity.id,
        "generation": entity.generation,
        "components": components,
    }


@router.get("/{entity_id}/components")
async def get_entity_components(
    entity_id: int,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取实体所有组件
    
    Args:
        entity_id: 实体 ID
    
    Returns:
        组件列表及其数据
    """
    world = manager.get_world()

    if not world.has_entity_id(entity_id):
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    entity = world.get_entity(entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    components = _serialize_entity_components(world, entity)

    return {
        "entity_id": entity_id,
        "components": components,
    }


@router.post("/")
async def create_entity(
    data: EntityCreate,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    创建实体
    
    Args:
        data: 创建参数 (组件列表)
    
    Returns:
        新实体 ID
    """
    world = manager.get_world()
    entity = world.create_entity()

    if data.components:
        raise HTTPException(
            status_code=501,
            detail="Component creation by name is not yet supported. Create an empty entity instead."
        )

    return {
        "id": entity.id,
        "generation": entity.generation,
    }


@router.put("/{entity_id}")
async def update_entity(
    entity_id: int,
    data: EntityUpdate,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    更新实体
    
    Args:
        entity_id: 实体 ID
        data: 更新参数
    
    Returns:
        更新结果
    """
    world = manager.get_world()

    if not world.has_entity_id(entity_id):
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")

    if data.components:
        raise HTTPException(
            status_code=501,
            detail="Component update by name is not yet supported."
        )

    return {
        "id": entity_id,
        "updated": True,
    }


@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: int,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    删除实体
    
    ⚠️ 注意：此操作仅删除实体本身，不会清理其他组件中的引用。
    各系统应在收到 EntityDestroyed 事件后自行清理引用。
    
    Args:
        entity_id: 实体 ID
    
    Returns:
        删除结果
    """
    world = manager.get_world()
    
    if not world.has_entity_id(entity_id):
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    # 触发 EntityDestroyed 事件，通知各系统清理引用
    try:
        world.event_bus.publish("EntityDestroyed", {"entity_id": entity_id})
    except Exception as e:
        logger.warning(f"[API Entity] 发布 EntityDestroyed 事件失败: {e}")  # 事件系统可能未初始化
    
    world.remove_entity_by_id(entity_id)
    
    return {
        "id": entity_id,
        "deleted": True,
        "note": "各系统应在收到 EntityDestroyed 事件后清理引用"
    }