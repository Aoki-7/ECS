#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具类型枚举定义
"""
from enum import Enum

class ToolType(Enum):
    """工具类型"""
    # 采集工具
    AXE = "axe"                  # 斧头：砍树效率+50%
    PICKAXE = "pickaxe"          # 镐子：挖矿效率+50%
    SICKLE = "sickle"            # 镰刀：收获作物效率+30%
    FISHING_ROD = "fishing_rod"  # 鱼竿：捕鱼效率+40%

    # 战斗工具
    WEAPON = "weapon"            # 武器：战斗伤害+50%
    BOW = "bow"                  # 弓：远程攻击

    # 建造工具
    HAMMER = "hammer"            # 锤子：建造速度+30%

    # 农业工具
    PLOW = "plow"                # 犁：耕作效率+60%

    # 生活工具
    TORCH = "torch"              # 火把：夜间视野+50%

class ToolMaterial(Enum):
    """工具材质"""
    STONE = "stone"      # 石制：基础耐久100
    BRONZE = "bronze"    # 青铜：耐久200，效率+20%
    IRON = "iron"        # 铁制：耐久300，效率+40%
    STEEL = "steel"      # 钢制：耐久500，效率+60%

class ToolQuality(Enum):
    """工具品质"""
    ROUGH = "rough"      # 粗糙：耐久系数0.8
    NORMAL = "normal"    # 普通：耐久系数1.0
    FINE = "fine"        # 精良：耐久系数1.5
    MASTER = "master"    # 大师：耐久系数2.0