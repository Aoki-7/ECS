#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界模拟实时仪表盘

v3.0.1 新增 — 全生态系统可视化

职责：
    - 收集世界所有系统数据
    - 生成实时监控 HTML
    - 支持实体分布、系统性能、生态指标
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from core.world import World


@dataclass
class WorldSnapshot:
    """世界快照"""
    tick: int
    timestamp: float
    
    # 实体统计
    total_entities: int = 0
    humans: int = 0
    animals: int = 0
    plants: int = 0
    buildings: int = 0
    farms: int = 0
    soil_patches: int = 0
    
    # 生态指标
    avg_plant_health: float = 0.0
    avg_animal_energy: float = 0.0
    total_biomass: float = 0.0
    biodiversity_index: float = 0.0
    
    # 文明指标
    total_population: int = 0
    building_count: int = 0
    farm_count: int = 0
    crafting_knowledge: int = 0
    farming_knowledge: int = 0
    tech_count: int = 0
    
    # 环境指标
    temperature: float = 20.0
    humidity: float = 0.5
    rainfall: float = 0.0
    wind_speed: float = 0.0
    
    # 灾害状态
    active_disasters: int = 0
    disaster_types: List[str] = None
    
    # 系统性能
    system_count: int = 0
    avg_tick_time_ms: float = 0.0
    
    def __post_init__(self):
        if self.disaster_types is None:
            self.disaster_types = []


class WorldSimulationDashboard:
    """
    世界模拟仪表盘
    
    收集完整世界数据并生成可视化。
    """
    
    def __init__(self, world: World):
        self.world = world
        self.history: List[WorldSnapshot] = []
        self.max_history = 500
        
    def capture_snapshot(self) -> WorldSnapshot:
        """捕获世界快照"""
        snapshot = WorldSnapshot(
            tick=self.world.tick_count,
            timestamp=time.time(),
        )
        
        # 统计实体
        snapshot.total_entities = len(self.world.entities)
        
        # 人类
        try:
            from human.components.basic.human_component import HumanComponent
            snapshot.humans = len(list(self.world.get_entities_with(HumanComponent)))
            snapshot.total_population = snapshot.humans
        except ImportError:
            pass
        
        # 动物
        try:
            from animal.components.animal_component import AnimalComponent
            snapshot.animals = len(list(self.world.get_entities_with(AnimalComponent)))
        except ImportError:
            pass
        
        # 植物
        try:
            from plant.components.plant_component import PlantComponent
            plants = list(self.world.get_entities_with(PlantComponent))
            snapshot.plants = len(plants)
        except ImportError:
            pass
        
        # 建筑
        try:
            from civilization.components.building_component import BuildingComponent
            snapshot.buildings = len(list(self.world.get_entities_with(BuildingComponent)))
            snapshot.building_count = snapshot.buildings
        except ImportError:
            pass
        
        # 农田
        try:
            from civilization.components.farm_component import FarmPlotComponent
            snapshot.farms = len(list(self.world.get_entities_with(FarmPlotComponent)))
            snapshot.farm_count = snapshot.farms
        except ImportError:
            pass
        
        # 土壤
        try:
            from environment.soil.components.soil_component import SoilComponent
            snapshot.soil_patches = len(list(self.world.get_entities_with(SoilComponent)))
        except ImportError:
            pass
        
        # 环境
        try:
            env = self.world.get_environment()
            if env:
                snapshot.temperature = getattr(env, 'air_temperature', 20.0)
                snapshot.humidity = getattr(env, 'air_humidity', 0.5)
                snapshot.rainfall = getattr(env, 'rainfall', 0.0)
                snapshot.wind_speed = getattr(env, 'wind_speed', 0.0)
        except Exception:
            pass
        
        # 系统
        snapshot.system_count = len(self.world.systems)
        
        # 知识统计
        try:
            from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent, CulturalTechPoolComponent
            crafting_exp = 0
            for entity, ck in self.world.query_components(CraftingKnowledgeComponent):
                crafting_exp += len(ck.material_experiments)
            snapshot.crafting_knowledge = crafting_exp
            
            tech_count = 0
            for entity, ctp in self.world.query_components(CulturalTechPoolComponent):
                tech_count += len(ctp.shared_recipes)
            snapshot.tech_count = tech_count
        except ImportError:
            pass
        
        try:
            from civilization.components.farm_component import FarmingKnowledgeComponent
            farming_exp = 0
            for entity, fk in self.world.query_components(FarmingKnowledgeComponent):
                farming_exp += len(fk.crop_experience)
            snapshot.farming_knowledge = farming_exp
        except ImportError:
            pass
        
        # 保存历史
        self.history.append(snapshot)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return snapshot
    
    def get_entity_positions(self) -> List[Dict[str, Any]]:
        """获取实体位置用于地图显示"""
        positions = []
        
        try:
            from space.space_component import SpaceComponent
            from human.components.basic.human_component import HumanComponent
            from animal.components.animal_component import AnimalComponent
            from plant.components.plant_component import PlantComponent
            from civilization.components.building_component import BuildingComponent
            from civilization.components.farm_component import FarmPlotComponent
            
            # 人类
            for entity, (space, _) in self.world.get_components(SpaceComponent, HumanComponent):
                positions.append({
                    'id': entity.id,
                    'type': 'human',
                    'x': space.x,
                    'y': space.y,
                })
            
            # 动物
            for entity, (space, _) in self.world.get_components(SpaceComponent, AnimalComponent):
                positions.append({
                    'id': entity.id,
                    'type': 'animal',
                    'x': space.x,
                    'y': space.y,
                })
            
            # 植物
            for entity, (space, _) in self.world.get_components(SpaceComponent, PlantComponent):
                positions.append({
                    'id': entity.id,
                    'type': 'plant',
                    'x': space.x,
                    'y': space.y,
                })
            
            # 建筑
            for entity, (space, _) in self.world.get_components(SpaceComponent, BuildingComponent):
                positions.append({
                    'id': entity.id,
                    'type': 'building',
                    'x': space.x,
                    'y': space.y,
                })
            
            # 农田
            for entity, (space, _) in self.world.get_components(SpaceComponent, FarmPlotComponent):
                positions.append({
                    'id': entity.id,
                    'type': 'farm',
                    'x': space.x,
                    'y': space.y,
                })
        except ImportError:
            pass
        
        return positions
    
    def export_json_data(self) -> Dict:
        """导出 JSON 数据供前端使用"""
        snapshot = self.capture_snapshot()
        
        return {
            'snapshot': asdict(snapshot),
            'history': [asdict(h) for h in self.history],
            'entities': self.get_entity_positions(),
        }
    
    def export_html(self, filepath: str = "world_simulation_dashboard.html") -> str:
        """导出完整仪表盘 HTML"""
        template_path = os.path.join(
            os.path.dirname(__file__), "world_simulation_dashboard.html"
        )
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()
        else:
            # 使用简化模板
            html = self._generate_full_dashboard_html()
        
        # 注入初始数据
        data = self.export_json_data()
        data_script = f"<script>window.WORLD_DATA = {json.dumps(data)};</script>"
        html = html.replace("</head>", data_script + "\n</head>")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath
    
    def _generate_full_dashboard_html(self) -> str:
        """生成完整仪表盘 HTML"""
        # 这里会返回一个简化版，实际使用外部模板文件
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>ECS World Simulation</title>
<style>
body { font-family: system-ui; background: #0a0a0f; color: #e8e8f0; margin: 0; padding: 20px; }
.stat { display: inline-block; background: #1a1a25; padding: 15px; margin: 5px; border-radius: 8px; }
.stat-value { font-size: 24px; font-weight: bold; color: #e94560; }
</style>
</head>
<body>
<h1>ECS World Simulation Dashboard</h1>
<div id="stats"></div>
<script>
if (window.WORLD_DATA) {
  const s = window.WORLD_DATA.snapshot;
  document.getElementById('stats').innerHTML = `
    <div class="stat"><div>Entities</div><div class="stat-value">${s.total_entities}</div></div>
    <div class="stat"><div>Humans</div><div class="stat-value">${s.humans}</div></div>
    <div class="stat"><div>Animals</div><div class="stat-value">${s.animals}</div></div>
    <div class="stat"><div>Plants</div><div class="stat-value">${s.plants}</div></div>
  `;
}
</script>
</body>
</html>"""
