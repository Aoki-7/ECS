#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System API 路由

提供系统控制:
    - POST /system/run       : 运行模拟
    - POST /system/pause     : 暂停模拟
    - POST /system/step      : 单步执行
    - GET  /system/status    : 获取状态
    - GET  /system/list      : 系统列表

版本: v4.0
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from api.dependencies import get_world_manager, WorldManager
from api.schemas.system import SystemStatus, SystemInfo, RunConfig

router = APIRouter(prefix="/system", tags=["System"])


@router.post("/run")
async def run_simulation(
    config: Optional[RunConfig] = None,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    运行模拟
    
    Args:
        config: 运行配置 (步数/步长)
    
    Returns:
        运行状态
    """
    if manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    manager.set_running(True)
    manager.set_paused(False)
    
    return {
        "status": "running",
        "config": config.dict() if config else {},
    }


@router.post("/pause")
async def pause_simulation(
    manager: WorldManager = Depends(get_world_manager)
):
    """
    暂停模拟
    
    Returns:
        暂停状态
    """
    if not manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation not running")
    
    manager.set_paused(True)
    
    return {
        "status": "paused",
    }


@router.post("/resume")
async def resume_simulation(
    manager: WorldManager = Depends(get_world_manager)
):
    """
    恢复模拟
    
    Returns:
        恢复状态
    """
    if not manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation not running")
    
    manager.set_paused(False)
    
    return {
        "status": "running",
    }


@router.post("/step")
async def step_simulation(
    dt: float = 1.0,
    manager: WorldManager = Depends(get_world_manager)
):
    """
    单步执行
    
    Args:
        dt: 时间步长
    
    Returns:
        执行结果
    """
    await manager.run_step(dt)
    
    return {
        "status": "step_completed",
        "dt": dt,
        "stats": manager.get_stats(),
    }


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取系统状态
    
    Returns:
        运行状态 (running/paused/stopped)
    """
    return {
        "running": manager.is_running(),
        "paused": manager.is_paused(),
        "stats": manager.get_stats(),
    }


@router.get("/list", response_model=List[SystemInfo])
async def list_systems(
    manager: WorldManager = Depends(get_world_manager)
):
    """
    获取系统列表
    
    Returns:
        所有注册的系统信息
    """
    world = manager.get_world()

    systems = []
    for system in world.systems:
        systems.append({
            "name": type(system).__name__,
            "enabled": True,
            "tick_interval": getattr(system, "tick_interval", 1),
            "priority": getattr(system, "priority", 0),
        })

    return systems
