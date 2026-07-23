"""
equipment 模块

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装备系统模块 — 工具、武器、防具的创建与管理

职责：
    - EquipmentComponent: 描述装备的基础属性（类型、耐久、攻击力、防御力等）
    - EquipmentFactory: 工厂类，按预设模板创建装备实体
    - 支持装备穿戴、耐久消耗、损坏判定

子模块：
    - components/: 装备相关组件定义
    - system/:     装备效果应用系统（如装备对战斗属性的修正）

与 human/ 的关系：
    - 人类通过 InventoryComponent 持有装备
    - 人类系统通过装备属性修正战斗、采集等行为效率
"""

from .equipment_factory import EquipmentFactory

__all__ = [
    "EquipmentFactory",
]
