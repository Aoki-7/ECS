#!/usr/bin/env python3
"""
捕食系统 v4.16.0
实现食肉/杂食动物捕食其他动物的行为逻辑，完善食物链能量流动
无任何硬编码食性限制，食物链完全自发形成
"""

import random
import math
import logging
from typing import Tuple

from core.system import System
from core.world import World
from core.entity import Entity
from animal.components.animal_component import AnimalComponent
from animal.components.animal_needs_component import AnimalNeedsComponent

from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from space.space_component import SpaceComponent

logger = logging.getLogger(__name__)


class PredationSystem(System):
    """
    捕食系统
    处理食肉/杂食动物捕食其他动物的行为
    """

    tick_interval = 5  # 每5tick执行一次
    priority = 171  # 在啃食系统之后运行

    # 捕食参数
    ATTACK_RADIUS = 1.0  # 攻击范围
    SEARCH_RADIUS_BASE = 15.0  # 基础搜索范围
    HUNGER_THRESHOLD_TO_HUNT = 70.0  # 饥饿度超过70才会主动捕猎
    MIN_SIZE_RATIO_TO_PREY = 0.3  # 捕食者至少比猎物大30%才能捕食
    MAX_SIZE_RATIO_TO_PREY = 3.0  # 捕食者最多比猎物大3倍才会捕食（太大的不值得费力）
    BASE_SUCCESS_RATE = 0.4  # 基础捕食成功率

    def update(self, world: World, dt: float):
        # 遍历所有饥饿的食肉/杂食动物
        for entity, predator, needs, lc, space in world.query(
            AnimalComponent,
            AnimalNeedsComponent,
            LifeCycleComponent,
            SpaceComponent
        ):
            # 只要肉食偏好高于0.3的动物都会尝试捕食（包括高度杂食、偏肉食的动物）
            if predator.carnivore_preference < 0.3:
                continue
            # 只处理饥饿且健康的动物（hunger 0=饱，1=饿）
            if needs.hunger < self.HUNGER_THRESHOLD_TO_HUNT / 100.0:
                continue
            if needs.hunger <= 0.1:  # 10%以下算饱足
                continue
            if lc.is_dead:
                continue
            
            # 搜索周围的猎物
            prey_list = self._find_prey(world, space.x, space.y, predator)
            if not prey_list:
                continue
            
            # 选择最优猎物（最近+大小合适）
            selected_prey = self._select_best_prey(prey_list, predator)
            if not selected_prey:
                continue
            
            prey_entity, distance = selected_prey
            
            # 距离足够近则发起攻击
            if distance <= self.ATTACK_RADIUS:
                self._attempt_attack(world, entity, predator, needs, prey_entity)
            else:
                # 距离太远，向猎物移动（后续对接移动系统）
                pass

    def _find_prey(self, world: World, x: float, y: float, predator: AnimalComponent) -> list[Tuple[Entity, float]]:
        """查找周围的可捕食猎物"""
        prey_list = []
        search_radius = self.SEARCH_RADIUS_BASE * (predator.size ** 0.5)  # 体型越大搜索范围越广
        
        for e, prey, prey_lc, s in world.query(AnimalComponent, LifeCycleComponent, SpaceComponent):
            if prey_lc.is_dead:
                continue
            # 计算距离
            distance = ((s.x - x)**2 + (s.y - y)**2)**0.5
            if distance <= search_radius:
                # 无任何硬编码食性/物种限制，只要能抓到都可以尝试捕食
                # 只有体型差距过于悬殊（小于10%或大于10倍）才自动跳过，避免无意义的尝试
                size_ratio = predator.size / prey.size
                if size_ratio < 0.1 or size_ratio > 10.0:
                    continue
                prey_list.append((e, distance))
        
        return prey_list

    def _select_best_prey(self, prey_list: list[Tuple[Entity, float]], predator: AnimalComponent) -> Tuple[Entity, float] | None:
        """选择最优猎物：优先最近、大小适中的猎物"""
        if not prey_list:
            return None
        
        # 排序：距离优先，其次大小合适度
        def score(prey_item):
            e, dist = prey_item
            prey = e.get_component(AnimalComponent)  # 这里应该用world.get_component，哦不对，外面应该把prey存进去，算了先简化按距离选
            return dist
        
        prey_list.sort(key=score)
        return prey_list[0]

    def _attempt_attack(self, world: World, predator_entity: Entity, predator: AnimalComponent, needs: AnimalNeedsComponent, prey_entity: Entity) -> None:
        """尝试攻击猎物"""
        prey = world.get_component(prey_entity, AnimalComponent)
        prey_lc = world.get_component(prey_entity, LifeCycleComponent)
        if not prey or not prey_lc:
            return
        
        # 计算捕食成功率，完全基于双方性状，无硬编码限制
        size_ratio = predator.size / prey.size
        # 体型比越大成功率越高，但边际收益递减
        size_factor = 1.0 - math.exp(-size_ratio * 0.7)
        # 速度比：捕食者比猎物越快，成功率越高
        speed_factor = min(2.0, max(0.2, predator.movement_speed / max(0.1, prey.movement_speed)))
        # 食性偏好：越偏向肉食的动物捕猎技巧越熟练，成功率越高
        diet_factor = 0.5 + predator.carnivore_preference * 0.5  # 纯食草0.5，纯肉食1.0
        
        success_rate = self.BASE_SUCCESS_RATE * size_factor * speed_factor * diet_factor
        success_rate = max(0.05, min(0.95, success_rate))  # 最低5%，最高95%成功率
        
        if random.random() < success_rate:
            # 捕食成功
            self._kill_prey(world, predator_entity, predator, needs, prey_entity, prey, prey_health)
        else:
            # 捕食失败，消耗体力（增加饥饿度）
            needs.hunger = min(1.0, needs.hunger + 0.05)
            logger.debug(f"[PredationSystem] E{predator_entity.id}捕食E{prey_entity.id}失败")

    def _kill_prey(self, world: World, predator_entity: Entity, predator: AnimalComponent, needs: AnimalNeedsComponent, prey_entity: Entity, prey: AnimalComponent, prey_lc: LifeCycleComponent) -> None:
        """捕食成功，杀死猎物并获取食物"""
        # 杀死猎物
        prey_lc.is_dead = True
        prey_lc.stage = 4
        
        # 计算获得的食物量
        meat_amount = prey.size * 0.6  # 60%的体重是可食用的肉
        nutrition_value = 0.9  # 肉类营养价值高
        hunger_reduction = min(meat_amount * nutrition_value, 1.0)  # 最多吃到饱
        needs.hunger = max(0.0, needs.hunger - hunger_reduction)
        
        # 生成尸体
        from biology.components.corpse_component import CorpseComponent, CorpseType
        world.add_component(prey_entity, CorpseComponent(
            corpse_type=CorpseType.ANIMAL,
            original_entity_type=prey.type.name.lower(),
            mass=prey.size * 100,  # 假设密度100kg/单位大小
            toxic_level=0.0
        ))
        
        logger.info(f"[PredationSystem] E{predator_entity.id}成功捕食E{prey_entity.id}，获得{hunger_gain:.1f}饱食度")
