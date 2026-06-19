#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:human_panel.py
@说明:人类状态可视化面板
@时间:2026/05/23
@版本:1.0

使用 rich 库在终端中渲染人类状态表格。
'''

from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box
from typing import List

if TYPE_CHECKING:
    from core.world import World


class HumanStatePanel:
    """
    人类状态可视化面板
    
    使用 rich 在终端渲染所有人类的关键状态，
    包括生理需求、情绪、意图、动作和部落身份。
    """

    def __init__(self):
        self.console = Console()

    def _bar(self, value: float, max_val: float = 100.0, width: int = 10) -> Text:
        """生成文本进度条"""
        ratio = max(0.0, min(1.0, value / max_val))
        filled = int(ratio * width)
        empty = width - filled
        
        # 颜色：高值=危险(红)，中值=警告(黄)，低值=安全(绿)
        if ratio > 0.7:
            color = "red"
        elif ratio > 0.4:
            color = "yellow"
        else:
            color = "green"
        
        bar_text = "#" * filled + "-" * empty
        return Text(f"{bar_text} {value:.0f}", style=color)

    def _energy_bar(self, value: float, max_val: float = 100.0, width: int = 10) -> Text:
        """精力条：低值=危险"""
        ratio = max(0.0, min(1.0, value / max_val))
        filled = int(ratio * width)
        empty = width - filled
        
        if ratio < 0.3:
            color = "red"
        elif ratio < 0.5:
            color = "yellow"
        else:
            color = "green"
        
        bar_text = "#" * filled + "-" * empty
        return Text(f"{bar_text} {value:.0f}", style=color)

    def _emotion_badge(self, emotion_label: str, mood_score: float) -> Text:
        """情绪标签"""
        if mood_score > 0.3:
            style = "green"
        elif mood_score < -0.3:
            style = "red"
        else:
            style = "white"
        return Text(emotion_label, style=style)

    def _hp_bar(self, value: float, max_val: float = 100.0, width: int = 10) -> Text:
        """生命值条：低值=危险"""
        ratio = max(0.0, min(1.0, value / max_val)) if max_val > 0 else 0.0
        filled = int(ratio * width)
        empty = width - filled

        if ratio < 0.3:
            color = "red"
        elif ratio < 0.6:
            color = "yellow"
        else:
            color = "green"

        bar_text = "#" * filled + "-" * empty
        return Text(f"{bar_text} {value:.0f}", style=color)

    def _temp_badge(self, temp: float) -> Text:
        """体温标签：异常标色"""
        if temp >= 39.0 or temp <= 35.0:
            style = "bold red"
        elif temp >= 38.0 or temp <= 36.0:
            style = "yellow"
        else:
            style = "green"
        return Text(f"{temp:.1f}°C", style=style)

    def _disease_badge(self, diseases: List[dict]) -> Text:
        """疾病标签"""
        if not diseases:
            return Text("-", style="dim")
        # 取最严重的一条
        worst = max(diseases, key=lambda d: d.get("severity", 0))
        name = worst.get("name", "未知")[:6]
        severity = worst.get("severity", 0)
        if severity >= 70:
            style = "bold red"
        elif severity >= 40:
            style = "red"
        else:
            style = "yellow"
        return Text(f"{name}({severity:.0f})", style=style)

    def _loyalty_badge(self, loyalty: float) -> Text:
        """忠诚度标签"""
        if loyalty >= 80:
            style = "bold green"
        elif loyalty >= 50:
            style = "green"
        elif loyalty >= 20:
            style = "yellow"
        else:
            style = "red"
        return Text(f"{loyalty:.0f}", style=style)

    def render(self, world: "World", step_count: int = 0) -> Panel:
        """渲染人类状态面板"""
        
        # 导入所有需要的组件
        from human.components.basic.human_component import HumanComponent
        from human.components.basic.identity_component import IdentityComponent
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
        from biology.components.gender_component import GenderComponent, Gender
        from biology.components.physiology_needs_component import PhysiologyNeedsComponent
        from human.components.cognitive.emotion_component import EmotionComponent
        from human.components.cognitive.intent_component import IntentComponent
        from human.components.action.action_component import ActionComponent
        from human.components.social.tribe_membership_component import TribeMembershipComponent
        from space.space_component import SpaceComponent
        from human.components.social.tribe_component import TribeComponent
        from identity.event_log_system import EventLog
        
        # 统计总体信息
        total_humans = 0
        tribe_count = 0
        for _, _ in world.get_components(HumanComponent):
            total_humans += 1
        for _, _ in world.get_components(TribeComponent):
            tribe_count += 1
        
        # 创建表格
        table = Table(
            box=box.SIMPLE_HEAD,
            title=f"[Human] 人类状态面板 (Step {step_count})",
            title_style="bold cyan",
            header_style="bold bright_white",
            row_styles=["", "dim"],
            padding=(0, 1),
        )
        
        table.add_column("名称", width=12, no_wrap=True)
        table.add_column("年龄", width=5, justify="center")
        table.add_column("位置", width=8, justify="center")
        table.add_column("HP", width=14)
        table.add_column("饥饿", width=12)
        table.add_column("口渴", width=12)
        table.add_column("精力", width=12)
        table.add_column("疲劳", width=12)
        table.add_column("体温", width=8, justify="center")
        table.add_column("情绪", width=6, justify="center")
        table.add_column("疾病", width=12, no_wrap=True)
        table.add_column("意图", width=8, no_wrap=True)
        table.add_column("动作", width=8, no_wrap=True)
        table.add_column("部落", width=10, justify="center")
        
        # 收集所有人类数据
        humans_data = []
        for entity, _ in world.get_components(HumanComponent):
            identity = world.get_component(entity, IdentityComponent)
            age = world.get_component(entity, LifeCycleComponent)
            gender = world.get_component(entity, GenderComponent)
            needs = world.get_component(entity, PhysiologyNeedsComponent)
            health = world.get_component(entity, HealthStatusComponent)
            disease = world.get_component(entity, DiseaseComponent)
            emotion = world.get_component(entity, EmotionComponent)
            intent = world.get_component(entity, IntentComponent)
            action = world.get_component(entity, ActionComponent)
            space = world.get_component(entity, SpaceComponent)
            membership = world.get_component(entity, TribeMembershipComponent)

            name = identity.name if identity else f"E{entity.id}"
            gender_symbol = "M" if (gender and gender.gender == Gender.MALE) else "F" if (gender and gender.gender == Gender.FEMALE) else "?"
            age_str = f"{age.age:.0f}{gender_symbol}" if age else "?"
            pos_str = f"({space.x:.0f},{space.y:.0f})" if space else "(?,?)"

            hp_bar = self._hp_bar(health.hp if health else 0, health.max_hp if health else 100, 8)
            hunger_bar = self._bar(needs.hunger if needs else 0, 100, 6)
            thirst_bar = self._bar(needs.thirst if needs else 0, 100, 6)
            energy_bar = self._energy_bar(needs.energy if needs else 0, 100, 6)
            fatigue_bar = self._bar(needs.fatigue if needs else 0, 100, 6)
            temp_badge = self._temp_badge(needs.body_temperature if needs else 37.0)

            emotion_label = emotion.get_mood_label() if emotion else "-"
            mood_score = emotion.get_mood_score() if emotion else 0.0
            emotion_badge = self._emotion_badge(emotion_label, mood_score)

            diseases = []
            if disease and disease.diseases:
                for d in disease.diseases:
                    if d.severity > 0:
                        diseases.append({"name": d.name, "severity": d.severity})
            disease_badge = self._disease_badge(diseases)

            intent_str = intent.intent.name if intent and intent.intent else "-"
            action_str = action.current_action.name if action and action.current_action else "-"

            if membership and membership.is_member():
                role_icon = "[L]" if membership.is_leader() else "[E]" if membership.role == "elder" else "[M]"
                tribe_str = f"{role_icon} {self._loyalty_badge(membership.loyalty)}"
            else:
                tribe_str = "-"

            humans_data.append({
                "name": name,
                "age": age_str,
                "pos": pos_str,
                "hp": hp_bar,
                "hunger": hunger_bar,
                "thirst": thirst_bar,
                "energy": energy_bar,
                "fatigue": fatigue_bar,
                "temp": temp_badge,
                "emotion": emotion_badge,
                "disease": disease_badge,
                "intent": intent_str,
                "action": action_str,
                "tribe": tribe_str,
                "sort_key": needs.hunger + needs.thirst if needs else 0,
            })
        
        # 按危机程度排序（最危险的在前）
        humans_data.sort(key=lambda x: x["sort_key"], reverse=True)
        
        for data in humans_data:
            table.add_row(
                data["name"],
                data["age"],
                data["pos"],
                data["hp"],
                data["hunger"],
                data["thirst"],
                data["energy"],
                data["fatigue"],
                data["temp"],
                data["emotion"],
                data["disease"],
                data["intent"],
                data["action"],
                data["tribe"],
            )
        
        # 总体统计文本
        stats_text = Text()
        stats_text.append(f"人口: {total_humans}  ", style="bold")
        stats_text.append(f"部落: {tribe_count}  ", style="bold")
        current_time = world.get_time()
        if current_time:
            day = int(current_time.total_hours // 24)
            hour = int(current_time.total_hours % 24)
            stats_text.append(f"时间: 第{day}天 {hour:02d}:00", style="bold cyan")
        
        # 最近事件列表
        recent_events = EventLog.get_recent(world, n=5)
        event_lines = []
        for evt in recent_events:
            severity_style = {
                "critical": "bold red",
                "milestone": "bold green",
                "warning": "yellow",
                "info": "dim",
            }.get(evt.severity, "dim")
            event_lines.append(Text(f"  [{evt.type}] {evt.description}", style=severity_style))
        
        if event_lines:
            from rich.console import Group
            content = Group(stats_text, table, Text("\n最近事件:", style="bold underline"), *event_lines)
        else:
            from rich.console import Group
            content = Group(stats_text, table)
        
        return Panel(
            content,
            border_style="bright_blue",
            padding=(1, 2),
        )

    def print_panel(self, world: "World", step_count: int = 0):
        """直接打印面板到终端"""
        panel = self.render(world, step_count)
        self.console.print(panel)
