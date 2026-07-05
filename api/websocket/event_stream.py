#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket 事件流

提供实时事件推送:
    - 模拟状态更新
    - 实体变化通知
    - 系统执行日志

版本: v4.0
"""

import asyncio
import json
from typing import Set, Dict

from fastapi import WebSocket
from starlette.websockets import WebSocketState


class EventStreamManager:
    """
    WebSocket 事件流管理器

    职责:
        1. 管理所有 WebSocket 连接
        2. 广播事件到所有客户端
        3. 处理客户端订阅/取消订阅
    """

    def __init__(self):
        self.connections: Set[WebSocket] = set()
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """建立连接"""
        await websocket.accept()
        async with self._lock:
            self.connections.add(websocket)
            self.subscriptions[websocket] = set()

    async def disconnect(self, websocket: WebSocket):
        """断开连接"""
        async with self._lock:
            self.connections.discard(websocket)
            self.subscriptions.pop(websocket, None)

    async def broadcast(self, event_type: str, data: dict):
        """广播事件到所有客户端（已订阅该类型的才发送）"""
        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time(),
        })

        disconnected = set()
        for conn in self.connections:
            topics = self.subscriptions.get(conn, set())
            # 未订阅任何主题时，默认接收全部事件；已订阅则过滤
            if topics and event_type not in topics:
                continue
            try:
                await conn.send_text(message)
            except Exception:
                disconnected.add(conn)

        # 清理断开的连接
        async with self._lock:
            self.connections -= disconnected
            for conn in disconnected:
                self.subscriptions.pop(conn, None)

    async def _send_ack(self, websocket: WebSocket, action: str, topic: str):
        await websocket.send_text(json.dumps({
            "type": "ack",
            "action": action,
            "topic": topic,
        }))

    async def handle(self, websocket: WebSocket):
        """处理 WebSocket 连接"""
        await self.connect(websocket)
        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                # 接收客户端消息 (订阅/取消订阅)
                data = await websocket.receive_text()
                message = json.loads(data)
                topic = message.get("topic", "")

                # 处理客户端命令
                if message.get("action") == "subscribe":
                    self.subscriptions.setdefault(websocket, set()).add(topic)
                    await self._send_ack(websocket, "subscribe", topic)
                elif message.get("action") == "unsubscribe":
                    self.subscriptions.get(websocket, set()).discard(topic)
                    await self._send_ack(websocket, "unsubscribe", topic)
                elif message.get("action") == "disconnect":
                    break
        except Exception:
            pass
        finally:
            await self.disconnect(websocket)


# 全局实例
event_stream_manager = EventStreamManager()


async def handle(websocket: WebSocket):
    """WebSocket 处理入口"""
    await event_stream_manager.handle(websocket)
