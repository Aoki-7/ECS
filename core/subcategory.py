#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
全局实体子分类枚举集

每个主分类（EntityCategory）对应一个子分类枚举。
子分类用于表达同一主分类下的细粒度差异。
"""

from enum import Enum, auto


# ───────────────────────────────────────────────
# 生物子分类
# ───────────────────────────────────────────────

class HumanSubCategory(Enum):
    """人类子分类"""
    CIVILIAN = auto()    # 平民
    WORKER = auto()      # 工人
    SOLDIER = auto()     # 士兵
    MERCHANT = auto()    # 商人
    NOBLE = auto()       # 贵族
    SCHOLAR = auto()     # 学者
    ARTISAN = auto()     # 工匠
    SLAVE = auto()       # 奴隶
    HUNTER = auto()      # 猎人
    FARMER = auto()      # 农民
    LEADER = auto()      # 领袖/首领


class AnimalSubCategory(Enum):
    """动物子分类"""
    HERBIVORE = auto()   # 食草动物
    CARNIVORE = auto()   # 食肉动物
    OMNIVORE = auto()    # 杂食动物
    SCAVENGER = auto()   # 食腐动物（清道夫）
    AQUATIC = auto()     # 水生动物
    AVIAN = auto()       # 鸟类
    REPTILE = auto()     # 爬行动物
    INSECT = auto()      # 昆虫
    MOUNT = auto()       # 坐骑


class PlantSubCategory(Enum):
    """植物子分类"""
    TREE = auto()        # 乔木
    FLOWER = auto()      # 花卉
    GRASS = auto()       # 草本植物
    CROP = auto()        # 农作物
    HERB = auto()        # 药用植物
    VINE = auto()        # 藤本植物
    MUSHROOM = auto()    # 菌类
    FERN = auto()        # 蕨类
    SUCCULENT = auto()   # 多肉植物
    AQUATIC = auto()     # 水生植物


class MicrobeSubCategory(Enum):
    """微生物子分类"""
    BACTERIA = auto()    # 细菌
    VIRUS = auto()       # 病毒
    FUNGUS = auto()      # 真菌
    PROTIST = auto()     # 原生生物
    ARCHAEA = auto()     # 古菌


# ───────────────────────────────────────────────
# 尸体子分类
# ───────────────────────────────────────────────

class CorpseSubCategory(Enum):
    """尸体子分类"""
    HUMAN = auto()       # 人类尸体
    ANIMAL = auto()      # 动物尸体
    PLANT = auto()       # 植物残骸
    UNKNOWN = auto()     # 未知来源


# ───────────────────────────────────────────────
# 资源子分类
# ───────────────────────────────────────────────

class FoodSubCategory(Enum):
    """食物子分类"""
    RAW = auto()         # 生食
    COOKED = auto()      # 熟食
    DRINK = auto()       # 饮品
    INGREDIENT = auto()  # 食材
    SEASONING = auto()   # 调味料
    PERISHABLE = auto()  # 易腐食品
    PRESERVED = auto()   # 腌制/保存食品
    BERRY = auto()       # 浆果
    MEAT = auto()        # 肉类
    FISH = auto()        # 鱼类
    GRAIN = auto()       # 谷物


class WaterSubCategory(Enum):
    """水源子分类"""
    CLEAN = auto()       # 净水
    POLLUTED = auto()    # 污水
    SALT = auto()        # 咸水
    HOT = auto()         # 热水/温泉
    COLD = auto()        # 冰水


class ResourceSubCategory(Enum):
    """通用资源子分类"""
    MINERAL = auto()     # 矿物
    WOOD = auto()        # 木材
    METAL = auto()       # 金属
    STONE = auto()       # 石材
    GEM = auto()         # 宝石
    LIQUID = auto()      # 液体
    GAS = auto()         # 气体
    FABRIC = auto()      # 织物
    FUEL = auto()        # 燃料
    MAGICAL = auto()     # 魔法材料


# ───────────────────────────────────────────────
# 物品与装备子分类
# ───────────────────────────────────────────────

class ItemSubCategory(Enum):
    """通用物品子分类"""
    TOOL = auto()        # 工具
    WEAPON = auto()      # 武器
    ARMOR = auto()       # 防具
    CONTAINER = auto()   # 容器
    ACCESSORY = auto()   # 饰品
    BOOK = auto()        # 书籍
    KEY = auto()         # 钥匙
    QUEST = auto()       # 任务物品
    CONSUMABLE = auto()  # 消耗品


class EquipmentSubCategory(Enum):
    """装备子分类"""
    SWORD = auto()       # 剑
    AXE = auto()         # 斧
    BOW = auto()         # 弓
    SHIELD = auto()      # 盾
    HELMET = auto()      # 头盔
    CHESTPLATE = auto()  # 胸甲
    LEGGINGS = auto()    # 护腿
    BOOTS = auto()       # 靴子
    RING = auto()        # 戒指
    AMULET = auto()      # 护身符


# ───────────────────────────────────────────────
# 环境子分类
# ───────────────────────────────────────────────

class WeatherSubCategory(Enum):
    """天气子分类"""
    SUNNY = auto()       # 晴天
    CLOUDY = auto()      # 多云
    RAINY = auto()       # 雨天
    STORMY = auto()      # 暴风雨
    SNOWY = auto()       # 雪天
    FOGGY = auto()       # 雾天
    WINDY = auto()       # 大风
    DROUGHT = auto()     # 干旱


class TerrainSubCategory(Enum):
    """地形子分类"""
    PLAIN = auto()       # 平原
    FOREST = auto()      # 森林
    DESERT = auto()      # 沙漠
    MOUNTAIN = auto()    # 山脉
    SWAMP = auto()       # 沼泽
    WATER_BODY = auto()  # 水体
    CAVE = auto()        # 洞穴
    COAST = auto()       # 海岸


class SoilSubCategory(Enum):
    """土壤子分类"""
    CLAY = auto()        # 黏土
    SAND = auto()        # 沙土
    LOAM = auto()        # 壤土
    SILT = auto()        # 粉土
    PEAT = auto()        # 泥炭
    ROCKY = auto()       # 岩石土


# ───────────────────────────────────────────────
# 抽象/组织子分类
# ───────────────────────────────────────────────

class OrgSubCategory(Enum):
    """组织子分类"""
    GOVERNMENT = auto()  # 政府
    COMPANY = auto()     # 公司
    FACTION = auto()     # 派系
    GUILD = auto()       # 公会
    FAMILY = auto()      # 家族
    RELIGION = auto()    # 宗教
    MILITARY = auto()    # 军队
    SCHOOL = auto()      # 学派/学校
    TRIBE = auto()       # 部落


class LocationSubCategory(Enum):
    """地点子分类"""
    CITY = auto()        # 城市
    BUILDING = auto()    # 建筑
    ROOM = auto()        # 房间
    REGION = auto()      # 区域
    LANDMARK = auto()    # 地标
    ROAD = auto()        # 道路
    DUNGEON = auto()     # 地牢
    PORTAL = auto()      # 传送门
    CAMP = auto()        # 营地
    FARM = auto()        # 农场


class BuildingSubCategory(Enum):
    """建筑子分类"""
    HOUSE = auto()       # 住宅
    FORTRESS = auto()    # 堡垒
    TOWER = auto()       # 塔楼
    BRIDGE = auto()      # 桥梁
    WALL = auto()        # 城墙
    MINE = auto()        # 矿场
    MILL = auto()        # 磨坊
    FORGE = auto()       # 铁匠铺


class GarbageSubCategory(Enum):
    """垃圾子分类"""
    ORGANIC = auto()     # 有机垃圾
    INORGANIC = auto()   # 无机垃圾
    TOXIC = auto()       # 有毒废物
    RECYCLABLE = auto()  # 可回收物


# ───────────────────────────────────────────────
# 系统/虚拟子分类
# ───────────────────────────────────────────────

class SystemSubCategory(Enum):
    """系统/模块子分类"""
    MODULE = auto()      # 模块
    SERVICE = auto()     # 服务
    PROCESS = auto()     # 进程
    MANAGER = auto()     # 管理器
    STORAGE = auto()     # 存储
    NETWORK = auto()     # 网络
    SCHEDULER = auto()   # 调度器


class EventSubCategory(Enum):
    """事件子分类"""
    ATTACK = auto()      # 攻击事件
    TRADE = auto()       # 交易事件
    DISASTER = auto()    # 灾害事件
    FESTIVAL = auto()    # 庆典事件
    MESSAGE = auto()     # 消息事件
    BIRTH = auto()       # 出生事件
    DEATH = auto()       # 死亡事件
    CRAFT = auto()       # 制造事件
    DISCOVERY = auto()   # 发现事件
    MIGRATION = auto()   # 迁移事件
    CONFLICT = auto()    # 冲突事件
