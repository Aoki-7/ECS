#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界模拟实时运行器 + 仪表盘导出

v3.0.1 — 全生态系统模拟
"""

import sys
import random

sys.path.insert(0, r"D:\个人助手\workspace\ECS")

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
from presentation.visualization.world_simulation_dashboard import WorldSimulationDashboard

import logging
logging.basicConfig(level=logging.CRITICAL)


def create_plant(world, x, y):
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, PlantComponent(yield_type="grass", max_yield=10.0))
    world.add_component(entity, PlantPerceptionComponent())
    world.add_component(entity, LifeCycleComponent(current_age=10))
    return entity.id


def create_animal(world, x, y):
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, AnimalComponent(species="deer", diet="herbivore"))
    world.add_component(entity, AnimalNeedsComponent(hunger=0.5, thirst=0.5))
    world.add_component(entity, AnimalMemoryComponent())
    world.add_component(entity, PhysiologyNeedsComponent())
    world.add_component(entity, ColliderComponent(radius=1.0, layer=0))
    return entity.id


def create_human(world, x, y, gender="male"):
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, HumanComponent())
    world.add_component(entity, IdentityComponent(name=f"Human_{entity.id}"))
    world.add_component(entity, GenderComponent(gender=gender))
    world.add_component(entity, TaskComponent())
    world.add_component(entity, InventoryComponent())
    world.add_component(entity, OutfitComponent())
    world.add_component(entity, PhysiologyNeedsComponent(energy=100.0, hunger=0.0, thirst=0.0))
    world.add_component(entity, ReproductionComponent())
    world.add_component(entity, SocialComponent())
    world.add_component(entity, SkillComponent())
    world.add_component(entity, CraftingKnowledgeComponent())
    world.add_component(entity, FarmingKnowledgeComponent())
    world.add_component(entity, ColliderComponent(radius=0.5, layer=0))
    return entity.id


def create_building(world, x, y, btype="hut"):
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, BuildingComponent(building_type=btype, durability=100.0))
    world.add_component(entity, ColliderComponent(radius=2.0, layer=1))
    world.add_component(entity, ObstacleComponent())
    return entity.id


def create_farm(world, x, y):
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, FarmPlotComponent(
        soil_quality=random.uniform(0.5, 0.9),
        crop_type=random.choice(["wheat", "corn", None]),
        growth_stage=random.uniform(0.0, 0.8),
    ))
    world.add_component(entity, SoilComponent(moisture=random.uniform(0.3, 0.6), ph=random.uniform(6.0, 7.5)))
    return entity.id


def create_soil(world, x, y):
    entity = world.create_entity()
    world.add_component(entity, SpaceComponent(x=x, y=y))
    world.add_component(entity, SoilComponent(moisture=random.uniform(0.2, 0.7), ph=random.uniform(5.5, 8.0)))
    return entity.id


def setup_world():
    world = World()
    world_entity = world.create_entity()
    env = EnvironmentComponent(air_temperature=22.0, air_humidity=0.5, wind_speed=1.0, rainfall=0.0, par=600.0)
    world.add_component(world_entity, env)
    world.set_world_entity(world_entity)

    world.add_system(CollisionSystem())
    world.add_system(PlantPerceptionSystem())
    world.add_system(AnimalNeedsSystem())
    world.add_system(AnimalSocialSystem())
    world.add_system(AnimalMemorySystem())
    world.add_system(ClothingSystem())
    world.add_system(CraftingSystem())
    world.add_system(FarmSystem())
    world.add_system(TechnologyEvolutionSystem())
    world.add_system(DisasterSystem())
    return world


def populate_world(world):
    for i in range(30):
        create_plant(world, random.uniform(0, 200), random.uniform(0, 200))
    for i in range(15):
        create_animal(world, random.uniform(0, 200), random.uniform(0, 200))
    for i in range(5):
        create_human(world, random.uniform(0, 100), random.uniform(0, 100), "male")
        create_human(world, random.uniform(0, 100), random.uniform(0, 100), "female")
    for i in range(3):
        create_building(world, random.uniform(0, 150), random.uniform(0, 150))
    for i in range(8):
        create_farm(world, random.uniform(0, 180), random.uniform(0, 180))
    for i in range(15):
        create_soil(world, random.uniform(0, 200), random.uniform(0, 200))
    tech_pool = world.create_entity()
    world.add_component(tech_pool, CulturalTechPoolComponent())
    print(f"世界创建完成: {len(world.entities)} 个实体")


def run_simulation(world, ticks=500, export_interval=50):
    dashboard = WorldSimulationDashboard(world)
    print(f"\n开始模拟 {ticks} ticks...")
    print("=" * 60)

    for tick in range(ticks):
        if tick % 50 == 0 and tick > 0:
            if random.random() < 0.3:
                create_human(world, random.uniform(0, 200), random.uniform(0, 200))
            if random.random() < 0.4:
                create_farm(world, random.uniform(0, 200), random.uniform(0, 200))
            if random.random() < 0.2:
                create_building(world, random.uniform(0, 200), random.uniform(0, 200))
            if random.random() < 0.3:
                create_plant(world, random.uniform(0, 200), random.uniform(0, 200))

        for entity, ck in list(world.query_components(CraftingKnowledgeComponent)):
            if random.random() < 0.1:
                materials = {"stone": random.uniform(0.5, 1.0), "wood": random.uniform(0.3, 0.8)}
                result = ck.suggest_experiment(materials)
                if result and isinstance(result, dict):
                    ck.record_attempt(inputs=materials, output=result.get("reason", "unknown"),
                                    quality=random.uniform(0.3, 0.9), success=random.random() > 0.3)

        for entity, fk in list(world.query_components(FarmingKnowledgeComponent)):
            if random.random() < 0.1:
                fk.record_planting(crop_type=random.choice(["wheat", "corn", "rice"]),
                                 soil_type=random.choice(["loam", "sand", "clay"]),
                                 season=random.choice(["spring", "summer", "autumn", "winter"]),
                                 yield_amount=random.uniform(0.3, 1.0), success=random.random() > 0.2)

        world.update(dt=1.0)

        if tick % export_interval == 0:
            dashboard.export_html("world_simulation_dashboard.html")
            snapshot = dashboard.history[-1] if dashboard.history else None
            if snapshot:
                print(f"[Tick {tick}] 实体={snapshot.total_entities}, 人类={snapshot.humans}, "
                      f"动物={snapshot.animals}, 植物={snapshot.plants}, 建筑={snapshot.buildings}")

    print("=" * 60)
    if dashboard.history:
        final = dashboard.history[-1]
        print(f"模拟完成! 总实体={final.total_entities}, 人类={final.humans}, 动物={final.animals}, "
              f"植物={final.plants}, 建筑={final.buildings}")
    return dashboard


def main():
    print("=" * 60)
    print("ECS 世界模拟 — 全生态系统")
    print("=" * 60)
    world = setup_world()
    populate_world(world)
    dashboard = run_simulation(world, ticks=500, export_interval=50)
    final_path = dashboard.export_html("world_simulation_dashboard.html")
    print(f"\n仪表盘已导出: {final_path}")
    print("请用浏览器打开查看实时可视化")
    return dashboard


if __name__ == "__main__":
    main()
