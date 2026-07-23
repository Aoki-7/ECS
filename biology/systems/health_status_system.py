#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
健康状态系统

将 HealthStatusComponent 中的业务逻辑迁移到 System
"""

from core.system import System
from core.world import World

from biology.components.health_status_component import HealthStatusComponent, WoundRecord


class HealthStatusSystem(System):
    """健康状态管理系统"""

    tick_interval = 5  # 每5帧执行一次

    def update(self, world: World, dt: float):
        for entity, (health,) in world.get_components(HealthStatusComponent):
            self._update_wounds(health, dt)
            self._remove_healed_wounds(health)

    def _update_wounds(self, health: HealthStatusComponent, dt: float):
        """更新伤口年龄并计算持续伤害"""
        total_dot = 0.0
        for wound in health.wounds:
            wound.age += dt
            if wound.duration > 0 and wound.age >= wound.duration:
                wound.severity = 0.0
            elif wound.damage_per_sec > 0:
                total_dot += wound.damage_per_sec * dt
        
        if total_dot > 0:
            health.hp = max(0, health.hp - total_dot)

    def _remove_healed_wounds(self, health: HealthStatusComponent, heal_threshold: float = 0.1):
        """移除已愈合的伤口"""
        health.wounds = [w for w in health.wounds if w.severity > heal_threshold]
        health.total_damage = sum(w.severity for w in health.wounds)

    @staticmethod
    def add_wound(entity, health: HealthStatusComponent, wound_type: str, severity: float,
                  damage_per_sec: float = 0.0, duration: float = -1.0):
        """添加新伤口（静态方法，供其他 System 调用）"""
        health.wounds.append(WoundRecord(
            type=wound_type,
            severity=severity,
            age=0.0,
            damage_per_sec=damage_per_sec,
            duration=duration,
        ))
        health.total_damage = min(health.max_damage, health.total_damage + severity)

    @staticmethod
    def get_total_severity(health: HealthStatusComponent) -> float:
        """获取所有伤口的总严重程度"""
        return sum(w.severity for w in health.wounds)