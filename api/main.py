#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 服务层 — FastAPI 后端入口

提供:
    - RESTful API (World/Entity/System/Snapshot/History)
    - WebSocket 实时事件流
    - 依赖注入 (WorldManager)

依赖:
    - fastapi
    - uvicorn
    - pydantic

启动:
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

版本: v4.0
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from api.routers import world, entity, system, snapshot, history
from api.websocket import event_stream
from db.config import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时清理资源
    pass


app = FastAPI(
    title="ECS World Simulation API",
    description="Entity-Component-System 世界模拟系统后端 API",
    version="4.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip 压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 注册路由
app.include_router(world.router, tags=["World"])
app.include_router(entity.router, tags=["Entity"])
app.include_router(system.router, tags=["System"])
app.include_router(snapshot.router, tags=["Snapshot"])
app.include_router(history.router, tags=["History"])

# WebSocket 端点
@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await event_stream.handle(websocket)

@app.get("/")
async def root():
    return {
        "message": "ECS World Simulation API",
        "version": "4.0.0",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}