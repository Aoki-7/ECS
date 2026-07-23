#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
全局实体子分类枚举集

v3.9 迁移：从 core/ 移回 identity/，保持 core 层纯粹性。

每个主分类（EntityCategory）对应一个子分类枚举。
子分类用于表达同一主分类下的细粒度差异。
"""

from enum import Enum, auto


class HumanSubCategory(Enum):
    """人类子分类"""
    CIVILIAN = auto()
    WORKER = auto()
    SOLDIER = auto()
    MERCHANT = auto()
    NOBLE = auto()
    SCHOLAR = auto()
    ARTISAN = auto()
    SLAVE = auto()
    HUNTER = auto()
    FARMER = auto()
    LEADER = auto()


class AnimalSubCategory(Enum):
    """动物子分类"""
    HERBIVORE = auto()
    CARNIVORE = auto()
    OMNIVORE = auto()
    SCAVENGER = auto()
    AQUATIC = auto()
    AVIAN = auto()
    REPTILE = auto()
    INSECT = auto()
    MOUNT = auto()


class PlantSubCategory(Enum):
    """植物子分类"""
    TREE = auto()
    FLOWER = auto()
    GRASS = auto()
    CROP = auto()
    HERB = auto()
    VINE = auto()
    MUSHROOM = auto()
    FERN = auto()
    SUCCULENT = auto()
    AQUATIC = auto()


class MicrobeSubCategory(Enum):
    """微生物子分类"""
    BACTERIA = auto()
    VIRUS = auto()
    FUNGUS = auto()
    PROTIST = auto()
    ARCHAEA = auto()


class CorpseSubCategory(Enum):
    """尸体子分类"""
    HUMAN = auto()
    ANIMAL = auto()
    PLANT = auto()
    UNKNOWN = auto()


class FoodSubCategory(Enum):
    """食物子分类"""
    RAW = auto()
    COOKED = auto()
    DRINK = auto()
    INGREDIENT = auto()
    SEASONING = auto()
    PERISHABLE = auto()
    PRESERVED = auto()
    BERRY = auto()
    MEAT = auto()
    FISH = auto()
    GRAIN = auto()


class WaterSubCategory(Enum):
    """水源子分类"""
    CLEAN = auto()
    POLLUTED = auto()
    SALT = auto()
    HOT = auto()
    COLD = auto()


class ResourceSubCategory(Enum):
    """通用资源子分类"""
    MINERAL = auto()
    WOOD = auto()
    METAL = auto()
    STONE = auto()
    GEM = auto()
    LIQUID = auto()
    GAS = auto()
    FABRIC = auto()
    FUEL = auto()
    MAGICAL = auto()


class ItemSubCategory(Enum):
    """通用物品子分类"""
    TOOL = auto()
    WEAPON = auto()
    ARMOR = auto()
    CONTAINER = auto()
    ACCESSORY = auto()
    BOOK = auto()
    KEY = auto()
    QUEST = auto()
    CONSUMABLE = auto()


class EquipmentSubCategory(Enum):
    """装备子分类"""
    SWORD = auto()
    AXE = auto()
    BOW = auto()
    SHIELD = auto()
    HELMET = auto()
    CHESTPLATE = auto()
    LEGGINGS = auto()
    BOOTS = auto()
    RING = auto()
    AMULET = auto()


class WeatherSubCategory(Enum):
    """天气子分类"""
    SUNNY = auto()
    CLOUDY = auto()
    RAINY = auto()
    STORMY = auto()
    SNOWY = auto()
    FOGGY = auto()
    WINDY = auto()
    DROUGHT = auto()


class TerrainSubCategory(Enum):
    """地形子分类"""
    PLAIN = auto()
    FOREST = auto()
    DESERT = auto()
    MOUNTAIN = auto()
    SWAMP = auto()
    WATER_BODY = auto()
    CAVE = auto()
    COAST = auto()


class SoilSubCategory(Enum):
    """土壤子分类"""
    CLAY = auto()
    SAND = auto()
    LOAM = auto()
    SILT = auto()
    PEAT = auto()
    ROCKY = auto()


class OrgSubCategory(Enum):
    """组织子分类"""
    GOVERNMENT = auto()
    COMPANY = auto()
    FACTION = auto()
    GUILD = auto()
    FAMILY = auto()
    RELIGION = auto()
    MILITARY = auto()
    SCHOOL = auto()
    TRIBE = auto()


class LocationSubCategory(Enum):
    """地点子分类"""
    CITY = auto()
    BUILDING = auto()
    ROOM = auto()
    REGION = auto()
    LANDMARK = auto()
    ROAD = auto()
    DUNGEON = auto()
    PORTAL = auto()
    CAMP = auto()
    FARM = auto()


class BuildingSubCategory(Enum):
    """建筑子分类"""
    HOUSE = auto()
    FORTRESS = auto()
    TOWER = auto()
    BRIDGE = auto()
    WALL = auto()
    MINE = auto()
    MILL = auto()
    FORGE = auto()


class GarbageSubCategory(Enum):
    """垃圾子分类"""
    ORGANIC = auto()
    INORGANIC = auto()
    TOXIC = auto()
    RECYCLABLE = auto()


class SystemSubCategory(Enum):
    """系统/模块子分类"""
    MODULE = auto()
    SERVICE = auto()
    PROCESS = auto()
    MANAGER = auto()
    STORAGE = auto()
    NETWORK = auto()
    SCHEDULER = auto()


class EventSubCategory(Enum):
    """事件子分类"""
    ATTACK = auto()
    TRADE = auto()
    DISASTER = auto()
    FESTIVAL = auto()
    MESSAGE = auto()
    BIRTH = auto()
    DEATH = auto()
    CRAFT = auto()
    DISCOVERY = auto()
    MIGRATION = auto()
    CONFLICT = auto()