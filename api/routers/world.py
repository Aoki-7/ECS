#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
World API 路由

提供 World 状态查询:
    - GET /world/stats      : World 统计信息
    - GET /world/query      : 组件查询
    - GET /world/archetypes : Archetype 信息
    - GET /world/entities   : 实体列表

版本: v4.0
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from api.dependencies import get_world_manager, WorldManager
from api.schemas.world import WorldStats, QueryResult, ArchetypeInfo

router = APIRouter(prefix="/world", tags=["World"])


@router.get("/stats", response_model=WorldStats)
async def get_world_stats(
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取 World 统计信息
    
    返回:
        - 实体数量 (created/destroyed/active)
        - 组件数量 (archetype_count/entity_count/cache_hit_rate)
        - 系统数量 (registered/executed/skipped)
    """
    return manager.get_cached_stats()


@router.get("/query")
async def query_components(
    component_types: List[str] = Query(..., description="组件类型列表"),
    manager: WorldManager = Depends(get_world_manager)
):
    """
    查询具有指定组件的实体
    
    Args:
        component_types: 组件类型列表 (如 ["HealthComponent", "PositionComponent"])
    
    Returns:
        实体列表及其组件数据
    """
    world = manager.get_world()
    
    # 动态解析组件类型
    # TODO: 实现组件类型映射
    results = []
    
    return {
        "query": component_types,
        "count": len(results),
        "results": results,
    }


@router.get("/archetypes")
async def get_archetypes(
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取所有 Archetype 信息
    
    返回:
        - Archetype 列表
        - 每个 Archetype 的实体数量
        - 组件类型签名
    """
    world = manager.get_world()
    return world.get_archetype_info()


@router.get("/entities")
async def get_entities(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取实体列表
    
    Args:
        limit: 每页数量
        offset: 偏移量
    
    Returns:
        实体列表 (分页)
    """
    world = manager.get_world()
    
    # 兼容不同版本的 World API
    if hasattr(world, 'get_all_entities'):
        entities = world.get_all_entities()
    else:
        # 使用 entities 属性或 query 方法
        entities = list(getattr(world, 'entities', {}).values())
    
    total = len(entities)
    paginated = entities[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "entities": [
            {
                "id": e.id,
                "generation": e.generation,
            }
            for e in paginated
        ],
    }
