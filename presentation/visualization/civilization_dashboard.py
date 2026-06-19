#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文明演化仪表盘

v3.0.1 新增

生成文明繁衍的实时监控仪表盘 HTML。
支持：
- 世界地图（实体分布）
- 人口/建筑/农田趋势图
- 知识积累进度
- 事件日志
- 系统状态
"""

import json
import os
from typing import Dict, List, Optional

from core.world import World


class CivilizationDashboard:
    """文明演化仪表盘"""

    def __init__(self, world: World):
        self.world = world
        self.template_path = os.path.join(
            os.path.dirname(__file__), "civilization_dashboard.html"
        )

    def generate_dashboard_data(self) -> Dict:
        """生成仪表盘数据"""
        from human.components.basic.human_component import HumanComponent
        from civilization.components.building_component import BuildingComponent
        from civilization.components.farm_component import FarmPlotComponent, FarmingKnowledgeComponent
        from civilization.components.crafting_knowledge_component import CraftingKnowledgeComponent, CulturalTechPoolComponent

        humans = list(self.world.get_entities_with(HumanComponent))
        buildings = list(self.world.get_entities_with(BuildingComponent))
        farms = list(self.world.get_entities_with(FarmPlotComponent))

        # 统计知识
        crafting_exp = 0
        farming_exp = 0
        tech_count = 0

        for entity, ck in self.world.query_components(CraftingKnowledgeComponent):
            crafting_exp += len(ck.material_experiments)

        for entity, fk in self.world.query_components(FarmingKnowledgeComponent):
            farming_exp += len(fk.crop_experience)

        for entity, ctp in self.world.query_components(CulturalTechPoolComponent):
            tech_count += len(ctp.shared_recipes)

        return {
            "tick": self.world.tick_count,
            "entities": {
                "humans": len(humans),
                "buildings": len(buildings),
                "farms": len(farms),
            },
            "statistics": {
                "crafting_experience": crafting_exp,
                "farming_experience": farming_exp,
                "technologies": tech_count,
            },
        }

    def export_html(self, filepath: str = "civilization_dashboard.html") -> str:
        """
        导出仪表盘 HTML

        如果模板存在则使用模板，否则生成独立 HTML。
        """
        if os.path.exists(self.template_path):
            with open(self.template_path, 'r', encoding='utf-8') as f:
                html = f.read()
        else:
            html = self._generate_standalone_html()

        # 注入初始数据
        data = self.generate_dashboard_data()
        data_script = f"<script>window.INITIAL_DATA = {json.dumps(data)};</script>"

        # 在 </head> 前注入数据
        html = html.replace("</head>", data_script + "\n</head>")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath

    def _generate_standalone_html(self) -> str:
        """生成独立 HTML（简化版）"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>ECS 文明演化监控</title>
<style>
body { font-family: system-ui, sans-serif; background: #0a0a0f; color: #e8e8f0; margin: 0; padding: 20px; }
.card { background: #1a1a25; border: 1px solid #2a2a3a; border-radius: 12px; padding: 20px; margin: 10px 0; }
h1 { color: #e94560; }
.stat { display: inline-block; background: #0f3460; padding: 15px 25px; margin: 5px; border-radius: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #e94560; }
</style>
</head>
<body>
<h1>ECS 文明演化监控</h1>
<div class="card">
  <div class="stat"><div>人口</div><div class="stat-value" id="humans">-</div></div>
  <div class="stat"><div>建筑</div><div class="stat-value" id="buildings">-</div></div>
  <div class="stat"><div>农田</div><div class="stat-value" id="farms">-</div></div>
</div>
<script>
if (window.INITIAL_DATA) {
  document.getElementById('humans').textContent = window.INITIAL_DATA.entities.humans;
  document.getElementById('buildings').textContent = window.INITIAL_DATA.entities.buildings;
  document.getElementById('farms').textContent = window.INITIAL_DATA.entities.farms;
}
</script>
</body>
</html>"""
