"""
装备系统 — 装备穿戴、属性加成、耐久

依赖:
    - equipment/
    - core/
    - human/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装备系统包 — 装备效果的应用与更新

包含：
    - EquipmentEffectSystem : 根据当前装备修正实体的战斗/采集/移动属性
    - DurabilitySystem      : 装备使用后的耐久消耗与损坏判定

与 human/ 的交互：
    - 读取人类的 InventoryComponent 获取已装备物品
    - 将装备属性加成写回人类的对应组件（如修正攻击力、防御力）
"""


