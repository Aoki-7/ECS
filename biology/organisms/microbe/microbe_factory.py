#!/usr/bin/env python3
"""
微生物工厂 v4.16.0
创建各种类型的微生物实体
"""

from core.world import World
from biology.organisms.microbe.components.microbe_component import MicrobeComponent, MicrobeType, MicrobeFunction
from space.space_component import SpaceComponent


class MicrobeFactory:
    """微生物工厂类，用于创建各种微生物实体"""
    
    @staticmethod
    def create_decomposer_bacteria(world: World, x: float, y: float, population: float = 1e6) -> int:
        """创建腐生分解细菌"""
        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=x, y=y))
        world.add_component(entity, MicrobeComponent(
            microbe_type=MicrobeType.BACTERIA,
            functions=[MicrobeFunction.DECOMPOSER],
            species="Pseudomonas putida",
            growth_rate=0.15,
            optimal_temperature=28.0,
            optimal_moisture=0.65,
            optimal_ph=7.0,
            population_size=population,
            decomposition_efficiency=0.25
        ))
        return entity
    
    @staticmethod
    def create_nitrogen_fixing_bacteria(world: World, x: float, y: float, population: float = 5e5) -> int:
        """创建根瘤菌/固氮菌"""
        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=x, y=y))
        world.add_component(entity, MicrobeComponent(
            microbe_type=MicrobeType.BACTERIA,
            functions=[MicrobeFunction.NITROGEN_FIXER, MicrobeFunction.SYMBIONT],
            species="Rhizobium",
            growth_rate=0.08,
            optimal_temperature=25.0,
            optimal_moisture=0.6,
            optimal_ph=6.8,
            population_size=population,
            nitrogen_fixation_rate=0.02,
            symbiosis_efficiency=0.4
        ))
        return entity
    
    @staticmethod
    def create_mycorrhizal_fungi(world: World, x: float, y: float, population: float = 3e5) -> int:
        """创建菌根真菌"""
        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=x, y=y))
        world.add_component(entity, MicrobeComponent(
            microbe_type=MicrobeType.FUNGI,
            functions=[MicrobeFunction.MYCORRHIZA, MicrobeFunction.DECOMPOSER],
            species="Glomus intraradices",
            growth_rate=0.05,
            optimal_temperature=22.0,
            optimal_moisture=0.55,
            optimal_ph=6.0,
            population_size=population,
            decomposition_efficiency=0.15,
            symbiosis_efficiency=0.5
        ))
        return entity
    
    @staticmethod
    def create_pathogenic_bacteria(world: World, x: float, y: float, population: float = 1e4) -> int:
        """创建致病细菌"""
        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=x, y=y))
        world.add_component(entity, MicrobeComponent(
            microbe_type=MicrobeType.BACTERIA,
            functions=[MicrobeFunction.PATHOGEN],
            species="Salmonella enterica",
            growth_rate=0.2,
            optimal_temperature=37.0,
            optimal_moisture=0.7,
            optimal_ph=7.2,
            population_size=population,
            pathogenicity=0.6
        ))
        return entity
    
    @staticmethod
    def create_pathogenic_fungi(world: World, x: float, y: float, population: float = 1e4) -> int:
        """创建致病真菌"""
        entity = world.create_entity()
        world.add_component(entity, SpaceComponent(x=x, y=y))
        world.add_component(entity, MicrobeComponent(
            microbe_type=MicrobeType.FUNGI,
            functions=[MicrobeFunction.PATHOGEN],
            species="Botrytis cinerea",
            growth_rate=0.12,
            optimal_temperature=20.0,
            optimal_moisture=0.8,
            optimal_ph=5.5,
            population_size=population,
            pathogenicity=0.5
        ))
        return entity
    
    @staticmethod
    def add_default_soil_microbes(world: World, x: float, y: float) -> None:
        """为指定位置的土壤添加默认微生物群落"""
        # 添加分解菌
        MicrobeFactory.create_decomposer_bacteria(world, x, y)
        # 50%概率添加固氮菌
        import random
        if random.random() < 0.5:
            MicrobeFactory.create_nitrogen_fixing_bacteria(world, x, y)
        # 70%概率添加菌根真菌
        if random.random() < 0.7:
            MicrobeFactory.create_mycorrhizal_fungi(world, x, y)
        # 10%概率添加低浓度致病菌
        if random.random() < 0.1:
            MicrobeFactory.create_pathogenic_bacteria(world, x, y, population=1e3)