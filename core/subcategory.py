# core/subcategory.py

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


class AnimalSubCategory(Enum):
    """动物子分类"""
    HERBIVORE = auto()
    CARNIVORE = auto()
    OMNIVORE = auto()
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


class MicrobeSubCategory(Enum):
    """微生物子分类"""
    BACTERIA = auto()
    VIRUS = auto()
    FUNGUS = auto()
    PROTIST = auto()


class FoodSubCategory(Enum):
    """食物子分类"""
    RAW = auto()
    COOKED = auto()
    DRINK = auto()
    INGREDIENT = auto()
    SEASONING = auto()
    PERISHABLE = auto()
    PRESERVED = auto()


class ResourceSubCategory(Enum):
    """资源子分类"""
    MINERAL = auto()
    WOOD = auto()
    METAL = auto()
    GEM = auto()
    LIQUID = auto()
    GAS = auto()
    FABRIC = auto()
    FUEL = auto()
    MAGICAL = auto()


class ItemSubCategory(Enum):
    """物品子分类（通用）"""
    TOOL = auto()
    WEAPON = auto()
    ARMOR = auto()
    CONTAINER = auto()
    ACCESSORY = auto()
    BOOK = auto()
    KEY = auto()
    QUEST = auto()


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


class LocationSubCategory(Enum):
    """位置子分类"""
    CITY = auto()
    BUILDING = auto()
    ROOM = auto()
    REGION = auto()
    LANDMARK = auto()
    ROAD = auto()
    DUNGEON = auto()
    PORTAL = auto()


class SystemSubCategory(Enum):
    """系统/模块子分类"""
    MODULE = auto()
    SERVICE = auto()
    PROCESS = auto()
    MANAGER = auto()
    STORAGE = auto()
    NETWORK = auto()


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
