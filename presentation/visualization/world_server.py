#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界模拟 WebSocket 服务器

v3.0.1 — 后端实时计算，前端实时推送

架构：
    Python (FastAPI + WebSocket) ←→ 浏览器 (WebSocket + Canvas/Chart.js)
    
    1. 后端运行 ECS 世界模拟
    2. 每 tick 将世界状态序列化为 JSON
    3. 通过 WebSocket 推送到前端
    4. 前端实时更新可视化
"""

import asyncio
import json
import sys
import time
import random
from typing import Dict, List, Set
from dataclasses import asdict

sys.path.insert(0, r"D:\个人助手\workspace\ECS")

# 尝试导入 FastAPI，如果没有则使用标准库 websocket
# 先创建一个简化版使用 asyncio

from core.world import World
from space.space_component import SpaceComponent
from space.collision_system import CollisionSystem, ColliderComponent, ObstacleComponent
from environment.environment_component import EnvironmentComponent
from environment.soil.components.soil_component import SoilComponent
from environment.systems.disaster_system import DisasterSystem
from plant.components.plant_component import PlantComponent
from plant.components.plant_perception_component import PlantPerceptionComponent
from plant.systems.plant_perception_system import PlantPerceptionSystem
from animal.components.animal_component import AnimalComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_memory_component import AnimalMemoryComponent
from animal.systems.animal_needs_system import AnimalNeedsSystem
from animal.systems.animal_social_system import AnimalSocialSystem
from animal.systems.animal_memory_system import AnimalMemorySystem
from human.components.basic.human_component import HumanComponent
from human.components.basic.identity_component import IdentityComponent
from human.components.basic.gender_component import GenderComponent
from human.components.cognitive.task_component import TaskComponent
from human.components.economic.inventory.inventory_component import InventoryComponent
from human.components.clothing_component import ClothingComponent, OutfitComponent
from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.social.reproduction_component import ReproductionComponent
from human.components.social.social_component import SocialComponent
from human.components.abilities.skill_component import SkillComponent
from human.systems.clothing_system import ClothingSystem
from civilization.components.building_component import BuildingComponent
from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent, CulturalTechPoolComponent
from civilization.components.farm_component import FarmPlotComponent, FarmingKnowledgeComponent
from civilization.systems.crafting_system import CraftingSystem
from civilization.systems.farm_system import FarmSystem
from civilization.systems.technology_evolution_system import TechnologyEvolutionSystem
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorldSimulationServer:
    """
    世界模拟服务器
    
    职责：
        1. 管理 ECS 世界
        2. 运行模拟循环
        3. 收集世界状态
        4. 通过 WebSocket 推送数据
    """
    
    def __init__(self):
        self.world = None
        self.clients: Set = set()
        self.tick_interval = 0.1  # 每 0.1 秒一个 tick (10 ticks/秒)
        self.is_running = False
        self.history: List[Dict] = []
        self.max_history = 200
        
    def setup_world(self):
        """设置完整世界"""
        self.world = World()
        
        # 环境
        world_entity = self.world.create_entity()
        env = EnvironmentComponent(
            air_temperature=22.0,
            air_humidity=0.5,
            wind_speed=1.0,
            rainfall=0.0,
            par=600.0,
        )
        self.world.add_component(world_entity, env)
        self.world.set_world_entity(world_entity)
        
        # 系统
        self.world.add_system(CollisionSystem())
        self.world.add_system(PlantPerceptionSystem())
        self.world.add_system(AnimalNeedsSystem())
        self.world.add_system(AnimalSocialSystem())
        self.world.add_system(AnimalMemorySystem())
        self.world.add_system(ClothingSystem())
        self.world.add_system(CraftingSystem())
        self.world.add_system(FarmSystem())
        self.world.add_system(TechnologyEvolutionSystem())
        self.world.add_system(DisasterSystem())
        
        # 填充世界
        self._populate_world()
        
        logger.info(f"世界创建完成: {len(self.world.entities)} 个实体")
        
    def _populate_world(self):
        """填充世界实体"""
        # 植物 (30)
        for i in range(30):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(
                x=random.uniform(0, 250), y=random.uniform(0, 250)
            ))
            self.world.add_component(entity, PlantComponent(
                yield_type="grass", max_yield=10.0
            ))
            self.world.add_component(entity, PlantPerceptionComponent())
            self.world.add_component(entity, LifeCycleComponent(current_age=10))
        
        # 动物 (15)
        for i in range(15):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(
                x=random.uniform(0, 250), y=random.uniform(0, 250)
            ))
            self.world.add_component(entity, AnimalComponent(
                species="deer", diet="herbivore"
            ))
            self.world.add_component(entity, AnimalNeedsComponent(
                hunger=0.5, thirst=0.5
            ))
            self.world.add_component(entity, AnimalMemoryComponent())
            self.world.add_component(entity, PhysiologyNeedsComponent())
            self.world.add_component(entity, ColliderComponent(radius=1.0, layer=0))
        
        # 人类 (10)
        for i in range(5):
            for gender in ["male", "female"]:
                entity = self.world.create_entity()
                self.world.add_component(entity, SpaceComponent(
                    x=random.uniform(0, 100), y=random.uniform(0, 100)
                ))
                self.world.add_component(entity, HumanComponent())
                self.world.add_component(entity, IdentityComponent(
                    name=f"Human_{entity.id}"
                ))
                self.world.add_component(entity, GenderComponent(gender=gender))
                self.world.add_component(entity, TaskComponent())
                self.world.add_component(entity, InventoryComponent())
                self.world.add_component(entity, OutfitComponent())
                self.world.add_component(entity, PhysiologyNeedsComponent())
                self.world.add_component(entity, ReproductionComponent())
                self.world.add_component(entity, SocialComponent())
                self.world.add_component(entity, SkillComponent())
                self.world.add_component(entity, CraftingKnowledgeComponent())
                self.world.add_component(entity, FarmingKnowledgeComponent())
                self.world.add_component(entity, ColliderComponent(radius=0.5, layer=0))
        
        # 建筑 (3)
        for i in range(3):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(
                x=random.uniform(0, 150), y=random.uniform(0, 150)
            ))
            self.world.add_component(entity, BuildingComponent(
                building_type="hut", durability=100.0
            ))
            self.world.add_component(entity, ColliderComponent(radius=2.0, layer=1))
            self.world.add_component(entity, ObstacleComponent())
        
        # 农田 (8)
        for i in range(8):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(
                x=random.uniform(0, 200), y=random.uniform(0, 200)
            ))
            self.world.add_component(entity, FarmPlotComponent(
                soil_quality=random.uniform(0.5, 0.9),
                crop_type=random.choice(["wheat", "corn", None]),
                growth_stage=random.uniform(0.0, 0.8),
            ))
            self.world.add_component(entity, SoilComponent(
                moisture=random.uniform(0.3, 0.6),
                ph=random.uniform(6.0, 7.5)
            ))
        
        # 土壤 (15)
        for i in range(15):
            entity = self.world.create_entity()
            self.world.add_component(entity, SpaceComponent(
                x=random.uniform(0, 250), y=random.uniform(0, 250)
            ))
            self.world.add_component(entity, SoilComponent(
                moisture=random.uniform(0.2, 0.7),
                ph=random.uniform(5.5, 8.0)
            ))
        
        # 文化技术池
        tech_pool = self.world.create_entity()
        self.world.add_component(tech_pool, CulturalTechPoolComponent())
    
    def get_world_state(self) -> Dict:
        """获取当前世界状态（用于推送到前端）"""
        state = {
            "tick": self.world.tick_count,
            "timestamp": time.time(),
        }
        
        # 实体统计
        humans = list(self.world.get_entities_with(HumanComponent))
        animals = list(self.world.get_entities_with(AnimalComponent))
        plants = list(self.world.get_entities_with(PlantComponent))
        buildings = list(self.world.get_entities_with(BuildingComponent))
        farms = list(self.world.get_entities_with(FarmPlotComponent))
        soils = list(self.world.get_entities_with(SoilComponent))
        
        state["statistics"] = {
            "total_entities": len(self.world.entities),
            "humans": len(humans),
            "animals": len(animals),
            "plants": len(plants),
            "buildings": len(buildings),
            "farms": len(farms),
            "soil_patches": len(soils),
        }
        
        # 实体位置（用于地图）
        state["entities"] = []
        
        # 人类
        for entity, (space, _) in self.world.get_components(SpaceComponent, HumanComponent):
            state["entities"].append({
                "id": entity.id, "type": "human",
                "x": space.x, "y": space.y
            })
        
        # 动物
        for entity, (space, _) in self.world.get_components(SpaceComponent, AnimalComponent):
            state["entities"].append({
                "id": entity.id, "type": "animal",
                "x": space.x, "y": space.y
            })
        
        # 植物
        for entity, (space, _) in self.world.get_components(SpaceComponent, PlantComponent):
            state["entities"].append({
                "id": entity.id, "type": "plant",
                "x": space.x, "y": space.y
            })
        
        # 建筑
        for entity, (space, _) in self.world.get_components(SpaceComponent, BuildingComponent):
            state["entities"].append({
                "id": entity.id, "type": "building",
                "x": space.x, "y": space.y
            })
        
        # 农田
        for entity, (space, _) in self.world.get_components(SpaceComponent, FarmPlotComponent):
            state["entities"].append({
                "id": entity.id, "type": "farm",
                "x": space.x, "y": space.y
            })
        
        # 土壤
        for entity, (space, _) in self.world.get_components(SpaceComponent, SoilComponent):
            state["entities"].append({
                "id": entity.id, "type": "soil",
                "x": space.x, "y": space.y
            })
        
        # 环境
        try:
            env = self.world.get_environment()
            if env:
                state["environment"] = {
                    "temperature": getattr(env, 'air_temperature', 20.0),
                    "humidity": getattr(env, 'air_humidity', 0.5),
                    "rainfall": getattr(env, 'rainfall', 0.0),
                    "wind_speed": getattr(env, 'wind_speed', 0.0),
                }
        except Exception:
            state["environment"] = {"temperature": 20.0, "humidity": 0.5, "rainfall": 0.0, "wind_speed": 0.0}
        
        # 知识统计
        crafting_exp = 0
        for entity, ck in self.world.query_components(CraftingKnowledgeComponent):
            crafting_exp += len(ck.material_experiments)
        
        farming_exp = 0
        for entity, fk in self.world.query_components(FarmingKnowledgeComponent):
            farming_exp += len(fk.crop_experience)
        
        tech_count = 0
        for entity, ctp in self.world.query_components(CulturalTechPoolComponent):
            tech_count += len(ctp.shared_recipes)
        
        state["knowledge"] = {
            "crafting": crafting_exp,
            "farming": farming_exp,
            "technologies": tech_count,
        }
        
        # 系统状态
        state["systems"] = [
            {"name": s.__class__.__name__, "enabled": getattr(s, 'enabled', True)}
            for s in self.world.systems
        ]
        
        return state
    
    async def run_simulation(self):
        """运行模拟循环"""
        self.is_running = True
        logger.info("模拟开始运行")
        
        while self.is_running:
            tick_start = time.time()
            
            # 随机事件
            if self.world.tick_count % 50 == 0 and self.world.tick_count > 0:
                if random.random() < 0.3:
                    self._create_human()
                if random.random() < 0.4:
                    self._create_farm()
                if random.random() < 0.2:
                    self._create_building()
            
            # 模拟制作活动
            for entity, ck in list(self.world.query_components(CraftingKnowledgeComponent)):
                if random.random() < 0.1:
                    materials = {"stone": random.uniform(0.5, 1.0), "wood": random.uniform(0.3, 0.8)}
                    result = ck.suggest_experiment(materials)
                    if result and isinstance(result, dict):
                        ck.record_attempt(
                            inputs=materials,
                            output=result.get("reason", "unknown"),
                            quality=random.uniform(0.3, 0.9),
                            success=random.random() > 0.3,
                        )
            
            # 模拟农业活动
            for entity, fk in list(self.world.query_components(FarmingKnowledgeComponent)):
                if random.random() < 0.1:
                    fk.record_planting(
                        crop_type=random.choice(["wheat", "corn", "rice"]),
                        soil_type=random.choice(["loam", "sand", "clay"]),
                        season=random.choice(["spring", "summer", "autumn", "winter"]),
                        yield_amount=random.uniform(0.3, 1.0),
                        success=random.random() > 0.2,
                    )
            
            # 更新世界
            self.world.update(dt=1.0)
            
            # 获取状态并广播
            state = self.get_world_state()
            
            # 保存历史
            if self.world.tick_count % 10 == 0:
                self.history.append({
                    "tick": state["tick"],
                    "humans": state["statistics"]["humans"],
                    "animals": state["statistics"]["animals"],
                    "plants": state["statistics"]["plants"],
                    "buildings": state["statistics"]["buildings"],
                    "farms": state["statistics"]["farms"],
                })
                if len(self.history) > self.max_history:
                    self.history.pop(0)
            
            state["history"] = self.history
            
            # 广播到所有客户端
            await self.broadcast(state)
            
            # 控制 tick 速率
            elapsed = time.time() - tick_start
            sleep_time = max(0, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)
    
    def _create_human(self):
        """创建新人类"""
        entity = self.world.create_entity()
        gender = random.choice(["male", "female"])
        self.world.add_component(entity, SpaceComponent(
            x=random.uniform(0, 250), y=random.uniform(0, 250)
        ))
        self.world.add_component(entity, HumanComponent())
        self.world.add_component(entity, IdentityComponent(name=f"Human_{entity.id}"))
        self.world.add_component(entity, GenderComponent(gender=gender))
        self.world.add_component(entity, TaskComponent())
        self.world.add_component(entity, InventoryComponent())
        self.world.add_component(entity, OutfitComponent())
        self.world.add_component(entity, PhysiologyNeedsComponent())
        self.world.add_component(entity, ReproductionComponent())
        self.world.add_component(entity, SocialComponent())
        self.world.add_component(entity, SkillComponent())
        self.world.add_component(entity, CraftingKnowledgeComponent())
        self.world.add_component(entity, FarmingKnowledgeComponent())
        self.world.add_component(entity, ColliderComponent(radius=0.5, layer=0))
    
    def _create_farm(self):
        """创建新农田"""
        entity = self.world.create_entity()
        self.world.add_component(entity, SpaceComponent(
            x=random.uniform(0, 250), y=random.uniform(0, 250)
        ))
        self.world.add_component(entity, FarmPlotComponent(
            soil_quality=random.uniform(0.5, 0.9),
            crop_type=random.choice(["wheat", "corn", None]),
            growth_stage=random.uniform(0.0, 0.8),
        ))
        self.world.add_component(entity, SoilComponent(
            moisture=random.uniform(0.3, 0.6),
            ph=random.uniform(6.0, 7.5)
        ))
    
    def _create_building(self):
        """创建新建筑"""
        entity = self.world.create_entity()
        self.world.add_component(entity, SpaceComponent(
            x=random.uniform(0, 250), y=random.uniform(0, 250)
        ))
        self.world.add_component(entity, BuildingComponent(
            building_type="hut", durability=100.0
        ))
        self.world.add_component(entity, ColliderComponent(radius=2.0, layer=1))
        self.world.add_component(entity, ObstacleComponent())
    
    async def broadcast(self, message: Dict):
        """广播消息到所有客户端"""
        if not self.clients:
            return
        
        data = json.dumps(message)
        disconnected = set()
        
        for client in self.clients:
            try:
                await client.send(data)
            except Exception:
                disconnected.add(client)
        
        # 清理断开连接的客户端
        self.clients -= disconnected
    
    def stop(self):
        """停止模拟"""
        self.is_running = False
        logger.info("模拟已停止")


# 简单的 WebSocket 服务器实现（使用 asyncio）
async def handle_client(websocket, path, server: WorldSimulationServer):
    """处理客户端连接"""
    logger.info(f"客户端连接: {websocket.remote_address}")
    server.clients.add(websocket)
    
    try:
        # 发送初始状态
        initial_state = server.get_world_state()
        initial_state["history"] = server.history
        await websocket.send(json.dumps(initial_state))
        
        # 保持连接，接收命令
        async for message in websocket:
            data = json.loads(message)
            command = data.get("command")
            
            if command == "pause":
                server.is_running = False
            elif command == "resume":
                if not server.is_running:
                    server.is_running = True
                    asyncio.create_task(server.run_simulation())
            elif command == "speed":
                server.tick_interval = data.get("interval", 0.1)
            
    except Exception as e:
        logger.error(f"客户端错误: {e}")
    finally:
        server.clients.discard(websocket)
        logger.info(f"客户端断开: {websocket.remote_address}")


# 尝试使用 websockets 库，如果没有则使用简化版
try:
    import websockets
    
    async def main():
        server = WorldSimulationServer()
        server.setup_world()
        
        # 启动 WebSocket 服务器
        ws_server = await websockets.serve(
            lambda ws, path: handle_client(ws, path, server),
            "localhost", 8765
        )
        
        logger.info("WebSocket 服务器启动: ws://localhost:8765")
        
        # 启动模拟
        asyncio.create_task(server.run_simulation())
        
        # 保持运行
        await asyncio.Future()
    
    if __name__ == "__main__":
        asyncio.run(main())

except ImportError:
    logger.warning("websockets 库未安装，使用简化版")
    logger.info("安装: pip install websockets")
    
    # 简化版：导出静态数据供前端读取
    def export_static_data():
        server = WorldSimulationServer()
        server.setup_world()
        
        # 运行 100 ticks
        for _ in range(100):
            server.world.update(dt=1.0)
        
        # 导出数据
        state = server.get_world_state()
        state["history"] = server.history
        
        with open("world_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        logger.info("静态数据已导出: world_state.json")
    
    if __name__ == "__main__":
        export_static_data()
