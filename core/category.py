#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
全局实体分类枚举

整个 ECS 系统的实体分类唯一来源。
用于快速筛选、统计、查询和权限控制。
"""

from enum import Enum, auto


class EntityCategory(Enum):
    """
    全局实体分类（强约束）

    设计原则：
        - 顶层分类尽量稳定，新增类别需审慎评估
        - 每个实体有且仅有一个主分类
        - 细粒度差异通过 SubCategory 表达
    """

    # ===== 生物 =====
    HUMAN = auto()       # 人类（玩家/NPC）
    ANIMAL = auto()      # 动物（野生/驯化）
    PLANT = auto()       # 植物（草本/木本/水生）
    MICROBE = auto()     # 微生物（细菌/病毒/真菌）

    # ===== 尸体与分解 =====
    CORPSE = auto()      # 尸体（死亡后遗留的实体）

    # ===== 资源 =====
    FOOD = auto()        # 食物（可直接食用）
    WATER = auto()       # 水源（可饮用/污染）
    RESOURCE = auto()    # 通用资源（矿物/木材/金属/石材）

    # ===== 物品与装备 =====
    ITEM = auto()        # 通用物品
    EQUIPMENT = auto()   # 装备（武器/防具/工具）

    # ===== 环境 =====
    WEATHER = auto()     # 天气实体（雨/雪/风暴等）
    TERRAIN = auto()     # 地形实体（平原/森林/山脉等）
    SOIL = auto()        # 土壤网格实体

    # ===== 抽象/组织 =====
    ORG = auto()         # 组织（政府/公会/家族等）
    LOCATION = auto()    # 地点（城市/建筑/地牢等）
    BUILDING = auto()    # 建筑/构筑物

    # ===== 废弃物 =====
    GARBAGE = auto()     # 垃圾/废弃物

    # ===== 系统/虚拟 =====
    SYSTEM = auto()      # 系统模块/管理器
    EVENT = auto()       # 事件实体（任务/灾害/庆典）

    # ===== 未知/未分类 =====
    UNKNOWN = auto()
