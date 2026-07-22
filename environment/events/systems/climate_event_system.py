#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
气候事件系统 v4.16.0
生成和管理极端气候事件，应用事件效果到生态系统
"""

import random
import math
from typing import Dict, List, Tuple

from core.system import System
from core.world import World

from environment.events.components.climate_event_component import (
    ClimateEventComponent, ClimateEventType, EventSeverity
)
from environment.soil.components.soil_component import SoilComponent
from environment.physics_weather.components.temperature_component import TemperatureComponent
from environment.physics_weather.components.precipitation_component import PrecipitationComponent
from plant.components.plant_component import PlantComponent
from animal.components.animal_component import AnimalComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent, LifeStage
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.systems.death_system import DeathSystem
from space.space_component import SpaceComponent

import logging

logger = logging.getLogger(__name__)


class ClimateEventSystem(System):
    """气候事件系统"""
    tick_interval = 24  # 每天运行一次，检查是否生成新事件

    def __init__(self, seed: int | None = None):
        super().__init__()
        self._rng = random.Random(seed)
        self._world_time: float = 0.0
        # 基础事件生成概率（每天）
        self._base_event_probability: float = 0.05  # 5%概率每天发生一次极端事件

    def update(self, world: World, dt: float = 1.0) -> None:
        """更新气候事件系统"""
        self._world_time += dt
        
        # 1. 处理已有的激活事件
        self._update_active_events(world, dt)
        
        # 2. 尝试生成新事件
        if self._tick_counter % self.tick_interval == 0:
            if self._rng.random() < self._base_event_probability:
                self._generate_new_event(world)
    
    def _update_active_events(self, world: World, dt: float) -> None:
        """更新激活的气候事件，应用效果"""
        events = world.get_components(ClimateEventComponent)
        for event_entity, event in list(events):
            # 更新事件剩余时间
            still_active = event.update(dt)
            
            if still_active:
                # 应用事件效果
                self._apply_event_effects(world, event)
            else:
                # 事件结束，应用结束效果并移除实体
                self._apply_event_end_effects(world, event)
                world.remove_entity(event_entity)
                logger.info(f"[Climate] {event.get_effect_description()} 已结束")
    
    def _generate_new_event(self, world: World) -> None:
        """根据当前环境条件生成合适的气候事件"""
        # 获取全局环境参数
        temp_comp = world.get_world_component(TemperatureComponent)
        precip_comp = world.get_world_component(PrecipitationComponent)
        
        if not temp_comp or not precip_comp:
            return
        
        # 计算各事件的生成概率，基于当前环境
        event_prob: Dict[ClimateEventType, float] = {
            ClimateEventType.DROUGHT: max(0.0, 0.1 - precip_comp.average_rainfall / 100.0),
            ClimateEventType.FLOOD: max(0.0, precip_comp.average_rainfall / 200.0),
            ClimateEventType.COLD_WAVE: max(0.0, 0.05 - (temp_comp.average_temperature - 0) / 50.0 if temp_comp.average_temperature < 10 else 0.0),
            ClimateEventType.HEAT_WAVE: max(0.0, (temp_comp.average_temperature - 25) / 50.0 if temp_comp.average_temperature > 25 else 0.0),
            ClimateEventType.WILDFIRE: max(0.0, (precip_comp.average_rainfall < 10) * (temp_comp.average_temperature > 30) * 0.2),
            ClimateEventType.HAILSTORM: max(0.0, (temp_comp.average_temperature < 20) * (precip_comp.average_rainfall > 50) * 0.05),
            ClimateEventType.TORNADO: 0.01,
            ClimateEventType.HURRICANE: 0.005,
        }
        
        # 随机选择一个事件生成
        total_prob = sum(event_prob.values())
        if total_prob <= 0:
            return
        
        rand_val = self._rng.random() * total_prob
        cumulative = 0.0
        selected_event = ClimateEventType.DROUGHT
        
        for event_type, prob in event_prob.items():
            cumulative += prob
            if rand_val <= cumulative:
                selected_event = event_type
                break
        
        # 随机生成事件参数
        severity = self._rng.choices(
            population=[EventSeverity.LIGHT, EventSeverity.MODERATE, EventSeverity.SEVERE, EventSeverity.EXTREME],
            weights=[0.5, 0.3, 0.15, 0.05]
        )[0]
        
        # 随机事件中心（在世界范围内）
        world_width = 50  # 默认50x50世界，TODO: 从世界配置获取
        world_height = 50
        center_x = self._rng.uniform(0, world_width)
        center_y = self._rng.uniform(0, world_height)
        
        # 事件持续时间
        duration_map = {
            ClimateEventType.DROUGHT: self._rng.uniform(7*24, 30*24),  # 7-30天
            ClimateEventType.FLOOD: self._rng.uniform(1*24, 7*24),    # 1-7天
            ClimateEventType.COLD_WAVE: self._rng.uniform(1*24, 3*24),# 1-3天
            ClimateEventType.HEAT_WAVE: self._rng.uniform(1*24, 5*24),# 1-5天
            ClimateEventType.WILDFIRE: self._rng.uniform(6, 72),      # 6小时到3天
            ClimateEventType.HAILSTORM: self._rng.uniform(1, 6),      # 1-6小时
            ClimateEventType.TORNADO: self._rng.uniform(0.5, 2),      # 30分钟到2小时
            ClimateEventType.HURRICANE: self._rng.uniform(24, 72),    # 1-3天
        }
        duration = duration_map[selected_event]
        
        # 影响半径
        radius_map = {
            ClimateEventType.DROUGHT: self._rng.uniform(20, 100),
            ClimateEventType.FLOOD: self._rng.uniform(10, 50),
            ClimateEventType.COLD_WAVE: self._rng.uniform(50, 200),
            ClimateEventType.HEAT_WAVE: self._rng.uniform(50, 200),
            ClimateEventType.WILDFIRE: self._rng.uniform(5, 30),
            ClimateEventType.HAILSTORM: self._rng.uniform(5, 20),
            ClimateEventType.TORNADO: self._rng.uniform(1, 10),
            ClimateEventType.HURRICANE: self._rng.uniform(50, 300),
        }
        radius = radius_map[selected_event]
        
        # 创建事件实体
        event_entity = world.create_entity()
        event = ClimateEventComponent(
            event_type=selected_event,
            severity=severity,
            start_time=self._world_time,
            duration=duration,
            center=(center_x, center_y),
            radius=radius
        )
        world.add_component(event_entity, event)
        
        logger.warning(f"[Climate] 生成极端天气事件：{event.get_effect_description()} at ({center_x:.0f}, {center_y:.0f})")
    
    def _apply_event_effects(self, world: World, event: ClimateEventComponent) -> None:
        """应用气候事件的实时效果"""
        event_type = event.event_type
        
        # 根据事件类型应用不同效果
        effect_handlers = {
            ClimateEventType.DROUGHT: self._apply_drought_effect,
            ClimateEventType.FLOOD: self._apply_flood_effect,
            ClimateEventType.COLD_WAVE: self._apply_cold_wave_effect,
            ClimateEventType.HEAT_WAVE: self._apply_heat_wave_effect,
            ClimateEventType.WILDFIRE: self._apply_wildfire_effect,
            ClimateEventType.HAILSTORM: self._apply_hailstorm_effect,
            ClimateEventType.TORNADO: self._apply_tornado_effect,
            ClimateEventType.HURRICANE: self._apply_hurricane_effect,
        }
        
        handler = effect_handlers.get(event_type)
        if handler:
            handler(world, event)
    
    def _apply_drought_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用干旱效果"""
        # 降低土壤湿度
        for soil_entity, (soil, space) in world.get_components([SoilComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0:
                soil.moisture = max(0.0, soil.moisture - intensity * 0.05)
        
        # 减慢植物生长，严重时植物死亡
        for plant_entity, (plant, lifecycle, space) in world.get_components([PlantComponent, LifeCycleComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0:
                plant.growth_rate *= (1.0 - intensity * 0.8)
                if intensity > 0.7 and self._rng.random() < intensity * 0.1:
                    # 重度干旱下植物有概率死亡
                    DeathSystem.kill(world, plant_entity, cause="drought")
    
    def _apply_flood_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用洪水效果"""
        # 升高水位，土壤湿度拉满
        for soil_entity, (soil, space) in world.get_components([SoilComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0:
                soil.moisture = min(1.0, soil.moisture + intensity * 0.3)
        
        # 低地植物和动物淹死
        for entity, (lifecycle, space) in world.get_components([LifeCycleComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0.5 and self._rng.random() < intensity * 0.2:
                # 低洼处生物淹死
                DeathSystem.kill(world, entity, cause="flood")
    
    def _apply_cold_wave_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用寒潮效果"""
        # 降低全局温度
        temp_comp = world.get_world_component(TemperatureComponent)
        if temp_comp:
            temp_comp.current_temperature -= event.intensity * 15
        
        # 生物冻伤死亡
        for entity, (lifecycle, energy, space) in world.get_components([LifeCycleComponent, EnergyComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0:
                energy.value -= intensity * 10  # 寒冷消耗更多能量
                if intensity > 0.6 and self._rng.random() < intensity * 0.15:
                    DeathSystem.kill(world, entity, cause="cold")
    
    def _apply_heat_wave_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用热浪效果"""
        # 升高全局温度
        temp_comp = world.get_world_component(TemperatureComponent)
        if temp_comp:
            temp_comp.current_temperature += event.intensity * 15
        
        # 生物中暑死亡
        for entity, (lifecycle, energy, space) in world.get_components([LifeCycleComponent, EnergyComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0:
                energy.value -= intensity * 8  # 炎热消耗更多能量
                if intensity > 0.6 and self._rng.random() < intensity * 0.15:
                    DeathSystem.kill(world, entity, cause="heat")
    
    def _apply_wildfire_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用野火效果"""
        # 烧毁植物和动物
        for entity, (lifecycle, space) in world.get_components([LifeCycleComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0.3 and self._rng.random() < intensity * 0.4:
                DeathSystem.kill(world, entity, cause="wildfire")
        
        # 烧毁的植被增加土壤肥力
        for soil_entity, (soil, space) in world.get_components([SoilComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0:
                soil.nitrogen += intensity * 50  # 火灾释放大量氮素
                soil.organic_matter += intensity * 20
    
    def _apply_hailstorm_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用冰雹效果"""
        # 破坏植物，伤害动物
        for entity, (lifecycle, space) in world.get_components([LifeCycleComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0.2 and self._rng.random() < intensity * 0.3:
                if world.has_component(entity, PlantComponent):
                    DeathSystem.kill(world, entity, cause="hail")
                else:
                    # 动物受伤，损失能量
                    energy = world.get_component(entity, EnergyComponent)
                    if energy:
                        energy.value -= intensity * 30
    
    def _apply_tornado_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用龙卷风效果"""
        # 直接杀死路径上的所有生物
        for entity, (lifecycle, space) in world.get_components([LifeCycleComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0.5:
                DeathSystem.kill(world, entity, cause="tornado")
    
    def _apply_hurricane_effect(self, world: World, event: ClimateEventComponent) -> None:
        """应用飓风效果"""
        # 强风摧毁植被，洪水，杀死生物
        for entity, (lifecycle, space) in world.get_components([LifeCycleComponent, SpaceComponent]):
            intensity = event.get_intensity_at_position(space.x, space.y)
            if intensity > 0.4 and self._rng.random() < intensity * 0.5:
                DeathSystem.kill(world, entity, cause="hurricane")
    
    def _apply_event_end_effects(self, world: World, event: ClimateEventComponent) -> None:
        """应用事件结束后的后续效果"""
        if event.event_type == ClimateEventType.WILDFIRE:
            # 野火后一段时间植物生长更快，因为土壤肥力高
            logger.info("[Climate] 野火结束，土壤肥力大幅提升，未来植物生长速度加快")
