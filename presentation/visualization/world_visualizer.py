#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界可视化器

生成世界状态的多种可视化图表：
1. 实体分布热力图
2. 系统性能监控
3. 实体关系网络图
4. 记忆网络图
5. 事件时间轴

输出格式：HTML（基于 D3.js）或 JSON 数据
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from core.world import World

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """可视化配置"""
    width: int = 800
    height: int = 600
    theme: str = "dark"
    show_labels: bool = True


class WorldVisualizer:
    """世界可视化器"""

    def __init__(self, world: World, config: Optional[VisualizationConfig] = None):
        self.world = world
        self.config = config or VisualizationConfig()

    def generate_entity_heatmap(self) -> dict:
        """生成实体分布热力图数据"""
        try:
            from space.space_component import SpaceComponent
        except ImportError:
            return {"type": "heatmap", "data": []}

        positions = []
        for entity, comps in self.world.get_components(SpaceComponent):
            space = comps[0] if isinstance(comps, list) else comps
            positions.append({"x": space.x, "y": space.y, "id": entity.id})

        return {
            "type": "heatmap",
            "data": positions,
            "count": len(positions),
        }

    def generate_system_performance(self) -> dict:
        """生成系统性能监控数据"""
        systems_data = []
        for system in self.world.systems:
            systems_data.append({
                "name": system.__class__.__name__,
                "priority": getattr(system, "priority", 0),
                "tick_interval": getattr(system, "tick_interval", 1),
                "enabled": getattr(system, "enabled", True),
            })

        return {
            "type": "performance",
            "tick_count": self.world.tick_count,
            "entity_count": len(self.world.entities),
            "systems": sorted(systems_data, key=lambda s: s["priority"]),
        }

    def generate_entity_network(self) -> dict:
        """生成实体关系网络图数据"""
        nodes = []
        edges = []

        for entity in self.world.entities.values():
            nodes.append({"id": entity.id, "type": "unknown"})

        # 尝试获取社交关系
        try:
            from animal.components.animal_social_component import AnimalSocialComponent
            for entity, social in self.world.get_components(AnimalSocialComponent):
                for other_id, score in social.relationship_scores.items():
                    if abs(score) > 0.3:
                        edges.append({
                            "source": entity.id,
                            "target": other_id,
                            "weight": abs(score),
                        })
        except ImportError:
            pass

        return {
            "type": "network",
            "nodes": nodes,
            "edges": edges,
        }

    def generate_memory_network(self) -> dict:
        """生成记忆网络图数据"""
        memory_layer = self.world.get_memory_layer()
        if memory_layer is None:
            return {"type": "memory_network", "concepts": [], "memories": []}

        concepts = []
        for concept in memory_layer.get_all_concepts():
            concepts.append({
                "id": concept.concept_id,
                "name": concept.name,
                "active": concept.is_active,
            })

        memories = []
        for memory in memory_layer.get_all_memories():
            memories.append({
                "subject": memory.subject_id,
                "concept": memory.concept_id,
                "confidence": memory.confidence,
            })

        return {
            "type": "memory_network",
            "concepts": concepts,
            "memories": memories,
        }

    def generate_event_timeline(self, limit: int = 100) -> dict:
        """生成事件时间轴数据"""
        try:
            from core.event_bus import EventBus
            events = EventBus.get_instance().get_history(limit=limit)
            timeline_data = [
                {
                    "time": e.timestamp,
                    "type": e.event_type,
                    "source": e.source,
                }
                for e in events
            ]
        except Exception:
            timeline_data = []

        return {
            "type": "timeline",
            "events": timeline_data,
        }

    def generate_full_report(self) -> dict:
        """生成完整可视化报告"""
        return {
            "version": "3.0-beta",
            "timestamp": self.world.tick_count,
            "visualizations": [
                self.generate_entity_heatmap(),
                self.generate_system_performance(),
                self.generate_entity_network(),
                self.generate_memory_network(),
                self.generate_event_timeline(),
            ],
        }

    def export_html(self, filepath: str = "world_visualization.html") -> str:
        """导出为交互式 HTML 文件"""
        report = self.generate_full_report()

        # 简化的 HTML 模板
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ECS World Visualization</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }}
.panel {{ background: #16213e; padding: 15px; margin: 10px 0; border-radius: 8px; }}
h2 {{ color: #e94560; }}
.stat {{ display: inline-block; background: #0f3460; padding: 10px 20px; margin: 5px; border-radius: 5px; }}
.stat-value {{ font-size: 24px; font-weight: bold; color: #e94560; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #333; }}
th {{ color: #e94560; }}
</style>
</head>
<body>
<h1>ECS World Visualization v3.0-beta</h1>

<div class="panel">
    <div class="stat"><div>Entities</div><div class="stat-value">{len(self.world.entities)}</div></div>
    <div class="stat"><div>Tick</div><div class="stat-value">{self.world.tick_count}</div></div>
    <div class="stat"><div>Systems</div><div class="stat-value">{len(self.world.systems)}</div></div>
</div>

<div class="panel">
    <h2>System Performance</h2>
    <table>
        <tr><th>System</th><th>Priority</th><th>Interval</th><th>Status</th></tr>
"""
        # 添加系统行
        perf = report["visualizations"][1]
        for sys in perf.get("systems", []):
            status = "✓" if sys["enabled"] else "✗"
            color = "#4ecca3" if sys["enabled"] else "#e94560"
            html += f'<tr><td>{sys["name"]}</td><td>{sys["priority"]}</td><td>{sys["tick_interval"]}</td><td style="color:{color}">{status}</td></tr>\n'

        html += """    </table>
</div>

<div class="panel">
    <h2>Memory Network</h2>
"""
        # 记忆网络
        mem = report["visualizations"][3]
        html += f'<p>Concepts: {len(mem.get("concepts", []))}</p>\n'
        html += f'<p>Memories: {len(mem.get("memories", []))}</p>\n'

        html += """
</div>

<div class="panel">
    <h2>Event Timeline (Recent)</h2>
"""
        # 时间轴
        timeline = report["visualizations"][4]
        for event in timeline.get("events", [])[-10:]:
            html += f'<p>[{event["time"]:.0f}] {event["type"]} from {event["source"]}</p>\n'

        html += """
</div>

<script>
const report = """ + json.dumps(report, ensure_ascii=False) + """;
console.log("Visualization report:", report);
</script>
</body>
</html>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"[Visualizer] HTML 已导出: {filepath}")
        return filepath
