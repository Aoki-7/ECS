#!/usr/bin/env python3
"""
ECS 世界模拟 Demo 服务器 (FastAPI + WebSocket)

版本: v4.16.0
定位: 实时演化、像素风、轻前端重后端、长时间运行低缓存压力

运行:
    cd D:\\个人助手\\workspace\\ECS
    python presentation/visualization/demo_server.py

后端端口: 8000
前端开发服务器: http://localhost:3000
"""

from __future__ import annotations

import os
import sys
import json
import time
import random
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 将项目根目录加入路径
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.world import World
from core.entity import Entity
from core.components.world_config_component import WorldConfigComponent
from application.simulation_loop import SimulationLoop

from space.space_component import SpaceComponent
from human.components.basic.human_component import HumanComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.components.gender_component import GenderComponent
from human.components.social.reproduction_component import ReproductionComponent
from biology.components.health_status_component import HealthStatusComponent
from plant.components.plant_component import PlantComponent
from animal.components.animal_component import AnimalComponent
from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent

import os
from logging.handlers import RotatingFileHandler

# 日志目录创建
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)
LOG_FILE = LOG_DIR / "demo_server.log"

# 日志格式
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 根logger配置
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.handlers.clear()

# 1. 文件Handler：全量日志（DEBUG+），10MB轮转，保留5个备份
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)

# 2. 控制台Handler：仅保留关键信息（WARNING+，以及demo相关INFO）
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.WARNING)
root_logger.addHandler(console_handler)

# 自定义Demo日志：控制台输出INFO级别
logger = logging.getLogger("ecs_demo")
logger.setLevel(logging.INFO)
logger.propagate = True  # 还是要进文件

# 过滤其他系统的INFO日志，仅保留到文件，控制台不输出
QUIET_MODULES = [
    "civilization",
    "environment",
    "biology",
    "human",
    "resource",
    "core",
    "application",
    "space",
    "uvicorn",
    "fastapi",
    "starlette",
]
for mod in QUIET_MODULES:
    mod_logger = logging.getLogger(mod)
    mod_logger.setLevel(logging.INFO)  # 还是进文件
    # 给这些模块的控制台输出降级到WARNING
    for handler in mod_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

@dataclass
class DemoConfig:
    """Demo 运行配置（可运行时调整）"""
    map_width: int = 50
    map_height: int = 50
    initial_humans: int = 25
    initial_plants: int = 50
    initial_food: int = 50
    initial_water: int = 50
    time_scale: float = 1.0          # 每个 tick 模拟多少小时
    target_tps: float = 10.0         # 目标 tick 频率（tick/s）
    speed: float = 1.0               # 速度倍率（影响 sleep 间隔和 time_scale）
    snapshot_interval: int = 1       # 每 N 个 tick 推送一次快照
    paused: bool = False
    max_history_ticks: int = 0       # 0 表示不保留历史，降低缓存压力

    @property
    def effective_time_scale(self) -> float:
        return self.time_scale * self.speed

    @property
    def sleep_interval(self) -> float:
        if self.speed <= 0 or self.paused:
            return 0.1
        return 1.0 / (self.target_tps * self.speed)


# ---------------------------------------------------------------------------
# 世界封装
# ---------------------------------------------------------------------------

class DemoWorld:
    """轻量封装 ECS 世界，供 Demo 服务器使用"""

    def __init__(self, config: DemoConfig):
        self.config = config
        self.world = World()
        self.loop = SimulationLoop(self.world)
        self.tick_count: int = 0
        self._births: int = 0
        self._deaths: int = 0

        self._init_world()
        self._spawn_entities()

    def _init_world(self) -> None:
        world_entity = self.world.create_entity()
        wc = WorldConfigComponent(
            map_width=self.config.map_width,
            map_height=self.config.map_height,
            time_scale=self.config.effective_time_scale,
        )
        self.world.add_component(world_entity, wc)
        self.world.set_world_entity(world_entity)

        self.loop.init()  # 注册系统、环境网格（小网格很快）

    def _spawn_entities(self) -> None:
        self.loop.create_initial_resources(
            self.config.initial_food,
            self.config.initial_water,
        )
        self.loop.create_initial_population(self.config.initial_humans)
        self.loop.create_initial_plants(self.config.initial_plants)

        # 让初始人类年轻些，避免一上来就老死，优化繁衍参数适合Demo观测
        from human.components.social.reproduction_component import ReproductionComponent
        for entity, _ in self.world.query_components(HumanComponent):
            lc = self.world.get_component(entity, LifeCycleComponent)
            repro = self.world.get_component(entity, ReproductionComponent)
            if lc is not None:
                lc.current_age = random.uniform(16.0, 30.0)  # 全是育龄人口
                lc.max_age = 80.0
                lc.min_reproductive_age = 16.0
                lc.max_reproductive_age = 45.0
            if repro is not None:
                repro.pregnancy_duration = 300.0  # 300小时=12.5天，Demo优化，快速看到生育
                repro.birth_cooldown = 600.0  # 生育冷却600小时=25天
                repro.last_birth_time = 0.0  # 重置冷却，初始即可怀孕

        # 预统计当前实体数
        self._recompute_stats()

    def step(self) -> None:
        """推进一个 tick"""
        self.loop.update(delta_hours=self.config.effective_time_scale)
        self.tick_count += 1

        # 自然资源生成逻辑（符合现实逻辑，允许匮乏但不破坏闭环）
        if self.tick_count % 30 == 0:
            # 每30tick（30小时游戏时间）按自然规则生成资源
            wc = self.world.get_world_component(WorldConfigComponent)
            world_env = self.world.get_component(self.world.get_world_entity(), EnvironmentComponent)
            human_count = len(list(self.world.query_components(HumanComponent)))
            
            # 统计当前资源量
            food_count = len(list(self.world.query_components(FoodComponent)))
            water_count = len(list(self.world.query_components(WaterComponent)))
            
            # 降雨时才生成水源，模拟降雨积水，30%概率
            if world_env and world_env.rainfall > 2.0 and random.random() < 0.3 and water_count < 8:
                from resource.water.water_factory import WaterFactory
                wf = WaterFactory()
                # 少量生成，每次2-3个小水坑
                for _ in range(random.randint(2, 3)):
                    x = random.uniform(0, wc.map_width - 1)
                    y = random.uniform(0, wc.map_height - 1)
                    wf.create_water(self.world, x=x, y=y, amount=random.uniform(2, 5))
                logger.debug(f"降雨生成 {random.randint(2,3)} 个水坑，当前水源={water_count}")
            
            # 白天时生成少量浆果，模拟植物自然结果，25%概率
            if world_env and hasattr(world_env, 'is_day') and world_env.is_day and random.random() < 0.25 and food_count < 6:
                from resource.food.food_factory import FoodFactory
                ff = FoodFactory()
                # 每次2-3个浆果
                for _ in range(random.randint(2, 3)):
                    x = random.uniform(0, wc.map_width - 1)
                    y = random.uniform(0, wc.map_height - 1)
                    ff.create_food(self.world, x=x, y=y, food_type="berry", amount=random.uniform(1, 2))
                logger.debug(f"植物结果生成 {random.randint(2,3)} 个浆果，当前食物={food_count}")
            
            # 人口灭绝后无自动补给，文明灭亡，等待用户手动重置纪元
            if human_count == 0:
                logger.info("人口已灭绝，文明灭亡，请手动重置")

        # 轻量死亡/出生探测：仅用于面板统计，不缓存历史
        self._recompute_stats()

    def _recompute_stats(self) -> Dict[str, Any]:
        stats = {
            "total": 0,
            "humans": 0,
            "plants": 0,
            "animals": 0,
            "food": 0,
            "water": 0,
            "buildings": 0,
            "corpses": 0,
        }
        for entity, _ in self.world.query(SpaceComponent):
            stats["total"] += 1
            if self.world.get_component(entity, HumanComponent) is not None:
                stats["humans"] += 1
            elif self.world.get_component(entity, PlantComponent) is not None:
                stats["plants"] += 1
            elif self.world.get_component(entity, AnimalComponent) is not None:
                stats["animals"] += 1
            elif self.world.get_component(entity, FoodComponent) is not None:
                stats["food"] += 1
            elif self.world.get_component(entity, WaterComponent) is not None:
                stats["water"] += 1
        return stats

    def get_snapshot(self) -> Dict[str, Any]:
        """生成精简快照，供前端 Canvas 渲染"""
        entities: List[Dict[str, Any]] = []
        for entity, space in self.world.query(SpaceComponent):
            x = int(round(space.x))
            y = int(round(space.y))
            if not (0 <= x < self.config.map_width and 0 <= y < self.config.map_height):
                continue

            kind = "unknown"
            state: Dict[str, Any] = {}

            if self.world.get_component(entity, HumanComponent) is not None:
                kind = "human"
                lc = self.world.get_component(entity, LifeCycleComponent)
                gender = self.world.get_component(entity, GenderComponent)
                health = self.world.get_component(entity, HealthStatusComponent)
                repro = self.world.get_component(entity, ReproductionComponent)
                state = {
                    "age": round(lc.current_age, 1) if lc else 0,
                    "max_age": round(lc.max_age, 1) if lc else 0,
                    "gender": gender.gender.value if gender and hasattr(gender.gender, "value") else str(gender.gender) if gender else None,
                    "pregnant": repro.is_pregnant if repro else False,
                    "hp": round(health.hp, 2) if health else 1.0,
                }
            elif self.world.get_component(entity, PlantComponent) is not None:
                kind = "plant"
                lc = self.world.get_component(entity, LifeCycleComponent)
                state = {"age": round(lc.current_age, 1) if lc else 0}
            elif self.world.get_component(entity, AnimalComponent) is not None:
                kind = "animal"
            elif self.world.get_component(entity, FoodComponent) is not None:
                kind = "food"
                fc = self.world.get_component(entity, FoodComponent)
                state = {"nutrition": round(fc.nutrition, 1) if fc else 0}
            elif self.world.get_component(entity, WaterComponent) is not None:
                kind = "water"
                wc = self.world.get_component(entity, WaterComponent)
                state = {"amount": round(wc.amount, 1) if wc else 0}

            entities.append({
                "id": entity.id,
                "x": x,
                "y": y,
                "type": kind,
                "state": state,
            })

        stats = self._recompute_stats()
        stats["tick"] = self.tick_count
        stats["births"] = self._births
        stats["deaths"] = self._deaths

        return {
            "type": "snapshot",
            "tick": self.tick_count,
            "config": {
                "width": self.config.map_width,
                "height": self.config.map_height,
                "time_scale": self.config.effective_time_scale,
                "speed": self.config.speed,
                "paused": self.config.paused,
            },
            "entities": entities,
            "stats": stats,
        }

    def get_entity_detail(self, entity_id: int) -> Optional[Dict[str, Any]]:
        """获取单个实体详情（供 Inspector）"""
        entity = self.world.get_entity(entity_id)
        if entity is None:
            return None
        components: Dict[str, Any] = {}
        for comp in self.world.get_components(entity):
            comp_name = type(comp).__name__
            try:
                if hasattr(comp, "to_dict"):
                    components[comp_name] = comp.to_dict()
                else:
                    components[comp_name] = str(comp)
            except Exception:
                components[comp_name] = "<serialize error>"
        return {"id": entity_id, "components": components}


# ---------------------------------------------------------------------------
# FastAPI 应用
# ---------------------------------------------------------------------------

app = FastAPI(title="ECS World Simulation Demo", version="4.16.0")
demo_config = DemoConfig()
demo_world: Optional[DemoWorld] = None
clients: Set[WebSocket] = set()
simulation_task: Optional[asyncio.Task] = None


async def broadcast(message: Dict[str, Any]) -> None:
    """向所有 WebSocket 客户端广播"""
    dead = set()
    for ws in clients:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    for ws in dead:
        clients.discard(ws)


async def simulation_loop() -> None:
    """后台模拟循环"""
    global demo_world
    if demo_world is None:
        logger.error("模拟世界未初始化")
        return

    logger.info("后台模拟循环启动")
    while True:
        try:
            if not demo_config.paused and demo_world is not None:
                # CPU 密集型模拟放在线程池执行，避免阻塞事件循环
                await asyncio.to_thread(demo_world.step)

                if demo_world.tick_count % max(1, demo_config.snapshot_interval) == 0:
                    snapshot = await asyncio.to_thread(demo_world.get_snapshot)
                    await broadcast(snapshot)
            else:
                # 暂停时仍周期性推送当前状态，保持前端时钟/连接活跃
                if demo_world is not None:
                    snapshot = await asyncio.to_thread(demo_world.get_snapshot)
                    await broadcast(snapshot)
            await asyncio.sleep(demo_config.sleep_interval)
        except asyncio.CancelledError:
            logger.info("模拟循环已取消")
            break
        except Exception as exc:
            logger.exception("模拟循环异常: %s", exc)
            await asyncio.sleep(1.0)


@app.on_event("startup")
async def startup() -> None:
    global demo_world, simulation_task
    logger.info("正在初始化 Demo 世界...")
    demo_world = DemoWorld(demo_config)
    logger.info("Demo 世界初始化完成，实体数: %d", len(demo_world.world.entities))
    simulation_task = asyncio.create_task(simulation_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    if simulation_task is not None:
        simulation_task.cancel()


@app.get("/api/world/config")
async def get_config() -> Dict[str, Any]:
    return {
        "map_width": demo_config.map_width,
        "map_height": demo_config.map_height,
        "initial_humans": demo_config.initial_humans,
        "initial_plants": demo_config.initial_plants,
        "time_scale": demo_config.time_scale,
        "speed": demo_config.speed,
        "paused": demo_config.paused,
    }


@app.get("/api/world/stats")
async def get_stats() -> Dict[str, Any]:
    if demo_world is None:
        return {"error": "world not ready"}
    return demo_world.get_snapshot()


@app.get("/api/entity/{entity_id}")
async def get_entity(entity_id: int) -> Dict[str, Any]:
    if demo_world is None:
        return {"error": "world not ready"}
    detail = demo_world.get_entity_detail(entity_id)
    if detail is None:
        return {"error": "entity not found"}
    return detail


@app.websocket("/ws/world")
async def websocket_endpoint(ws: WebSocket) -> None:
    global demo_world
    await ws.accept()
    clients.add(ws)
    logger.info("WebSocket 客户端连接，当前 %d 个", len(clients))

    # 发送初始快照
    if demo_world is not None:
        try:
            await ws.send_json(demo_world.get_snapshot())
        except Exception as exc:
            logger.warning("发送初始快照失败: %s", exc)

    try:
        while True:
            data = await ws.receive_json()
            if not isinstance(data, dict):
                continue

            msg_type = data.get("type")
            if msg_type == "control":
                action = data.get("action")
                if action == "pause":
                    demo_config.paused = True
                elif action == "resume":
                    demo_config.paused = False
                elif action == "toggle":
                    demo_config.paused = not demo_config.paused
                elif action == "set_speed":
                    speed = float(data.get("value", 1.0))
                    demo_config.speed = max(0.0, min(speed, 10.0))
                elif action == "step":
                    # 单步前进（暂停模式下）
                    demo_config.paused = True
                    await asyncio.to_thread(demo_world.step)
                elif action == "reset":
                    demo_world = DemoWorld(demo_config)

                # 确认状态
                await ws.send_json({
                    "type": "config",
                    "config": {
                        "speed": demo_config.speed,
                        "paused": demo_config.paused,
                    },
                })
            elif msg_type == "query_entity":
                eid = int(data.get("entity_id", -1))
                detail = demo_world.get_entity_detail(eid) if demo_world else None
                await ws.send_json({
                    "type": "entity_detail",
                    "entity": detail or {"error": "not found"},
                })
    except WebSocketDisconnect:
        logger.info("WebSocket 客户端断开")
    except Exception as exc:
        logger.warning("WebSocket 异常: %s", exc)
    finally:
        clients.discard(ws)


# 静态文件服务（生产构建）
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True))
else:
    @app.get("/")
    async def root() -> Dict[str, Any]:
        return {
            "message": "ECS Demo API 正在运行",
            "docs": "/docs",
            "ws": "ws://localhost:8000/ws/world",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "presentation.visualization.demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",
        access_log=False,
    )
