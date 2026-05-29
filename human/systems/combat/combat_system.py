#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:combat_system.py
@说明:战斗系统（简化版）
@时间:2026/05/29
@版本:1.0

处理 ATTACK / DEFEND / FLEE / CHASE 四种战斗行为
'''

import math
import random

from core.system import System
from core.world import World

from core.components.action_component import (
    ActionComponent, ActionType, ActionStatus
)
from biology.components.health_component import HealthComponent
from human.components.combat.combat_stats_component import CombatStatsComponent
from biology.components.injury.injury_component import InjuryComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem


class CombatSystem(System):
    """
    战斗系统
    处理攻击、防御、逃跑、追击的逻辑
    """

    FLEE_DISTANCE = 20.0     # 逃跑成功距离
    FLEE_SPEED_BONUS = 2.0   # 逃跑速度倍率

    def update(self, world: World, dt: float):
        space_system = world.get_system(SpaceSystem)

        for entity, (action, space, combat_stats, health) in list(world.get_components(
            ActionComponent, SpaceComponent, CombatStatsComponent, HealthComponent
        )):
            action: ActionComponent
            space: SpaceComponent
            combat_stats: CombatStatsComponent
            health: HealthComponent

            if action.current_action == ActionType.ATTACK:
                self._process_attack(world, space_system, entity, action, space, combat_stats, health, dt)
            elif action.current_action == ActionType.DEFEND:
                self._process_defend(action, dt)
            elif action.current_action == ActionType.FLEE:
                self._process_flee(world, space_system, entity, action, space, dt)
            elif action.current_action == ActionType.CHASE:
                self._process_chase(world, space_system, entity, action, space, combat_stats, dt)

    def _process_attack(self, world, space_system, entity, action, space, combat_stats, health, dt):
        """处理攻击逻辑"""
        target_id = action.target_entity
        if target_id is None:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        target = world.query_entity(target_id)
        if target is None or not target.is_alive():
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        target_space = world.get_component(target, SpaceComponent)
        if target_space is None:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        dist = math.hypot(target_space.x - space.x, target_space.y - space.y)

        if dist > combat_stats.attack_range:
            # 距离太远，转为追击
            action.current_action = ActionType.CHASE
            action.status = ActionStatus.RUNNING
            return

        # 计算伤害
        target_combat = world.get_component(target, CombatStatsComponent)
        target_defense = target_combat.defense_power if target_combat else 0.0

        base_damage = max(0.0, combat_stats.attack_power - target_defense)
        random_factor = random.uniform(0.8, 1.2)
        damage = base_damage * random_factor

        # 应用伤害
        target_health = world.get_component(target, HealthComponent)
        if target_health:
            target_health.hp -= damage
            target_health.hp = max(0.0, target_health.hp)

        # 给目标添加伤害组件（如果没有）
        target_injury = world.get_component(target, InjuryComponent)
        if target_injury is None:
            from biology.components.injury.injury_component import InjuryComponent
            world.add_component(target, InjuryComponent(damage_per_sec=0.5))

        action.status = ActionStatus.SUCCESS

        # 如果目标未死，保持攻击状态（下一 tick 继续）
        if target_health and target_health.hp <= 0:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.SUCCESS

    def _process_defend(self, action, dt):
        """处理防御逻辑：防御状态持续中"""
        action.progress += dt * 0.5
        if action.progress >= 1.0:
            action.progress = 1.0
            action.status = ActionStatus.SUCCESS
            # 防御结束后自动 IDLE
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.IDLE

    def _process_flee(self, world, space_system, entity, action, space, dt):
        """处理逃跑逻辑：向远离敌人的反方向移动"""
        target_id = action.target_entity
        if target_id is None:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        target = world.query_entity(target_id)
        if target is None or not target.is_alive():
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.SUCCESS
            return

        target_space = world.get_component(target, SpaceComponent)
        if target_space is None:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        dx = space.x - target_space.x
        dy = space.y - target_space.y
        dist = math.hypot(dx, dy)

        if dist >= self.FLEE_DISTANCE:
            # 逃跑成功
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.SUCCESS
            action.target_entity = None
            return

        # 向反方向移动
        if dist > 0:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x, dir_y = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        # 使用速度组件，临时提升
        velocity = world.get_component(entity, VelocityComponent)
        speed = velocity.speed * self.FLEE_SPEED_BONUS if velocity else 5.0

        space.x = round(space.x + dir_x * speed * dt)
        space.y = round(space.y + dir_y * speed * dt)
        space.dirty = True

        action.status = ActionStatus.RUNNING

    def _process_chase(self, world, space_system, entity, action, space, combat_stats, dt):
        """处理追击逻辑：直线追击目标"""
        target_id = action.target_entity
        if target_id is None:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        target = world.query_entity(target_id)
        if target is None or not target.is_alive():
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        target_space = world.get_component(target, SpaceComponent)
        if target_space is None:
            action.current_action = ActionType.IDLE
            action.status = ActionStatus.FAILED
            return

        dist = math.hypot(target_space.x - space.x, target_space.y - space.y)

        if dist <= combat_stats.attack_range:
            # 进入攻击范围，转为攻击
            action.current_action = ActionType.ATTACK
            action.status = ActionStatus.RUNNING
            return

        # 直线追击
        if dist > 0:
            dir_x = (target_space.x - space.x) / dist
            dir_y = (target_space.y - space.y) / dist
        else:
            action.current_action = ActionType.ATTACK
            return

        velocity = world.get_component(entity, VelocityComponent)
        speed = velocity.speed if velocity else 2.5

        space.x = round(space.x + dir_x * speed * dt)
        space.y = round(space.y + dir_y * speed * dt)
        space.dirty = True

        action.status = ActionStatus.RUNNING


from core.components.velocity_component import VelocityComponent
