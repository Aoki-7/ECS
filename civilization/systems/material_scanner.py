#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
材料扫描器

职责：
    - 扫描库存中的可用材料
    - 检查材料是否充足
    - 消耗材料
"""

from typing import Dict, List

from human.components.economic.inventory.inventory_component import InventoryComponent


class MaterialScanner:
    """材料扫描器"""

    # 材料基础属性（物理属性，非配方）
    MATERIAL_PROPERTIES = {
        "wood": {
            "hardness": 0.3,
            "flexibility": 0.7,
            "durability": 0.4,
            "workability": 0.8,
        },
        "stone": {
            "hardness": 0.9,
            "flexibility": 0.1,
            "durability": 0.8,
            "workability": 0.3,
        },
        "metal": {
            "hardness": 0.8,
            "flexibility": 0.5,
            "durability": 0.9,
            "workability": 0.4,
        },
        "bone": {
            "hardness": 0.5,
            "flexibility": 0.3,
            "durability": 0.5,
            "workability": 0.6,
        },
        "fiber": {
            "hardness": 0.1,
            "flexibility": 0.9,
            "durability": 0.2,
            "workability": 0.7,
        },
        "clay": {
            "hardness": 0.2,
            "flexibility": 0.4,
            "durability": 0.1,
            "workability": 0.9,
        },
    }

    def scan_inventory(self, inventory: InventoryComponent) -> List[str]:
        """扫描库存中的可用材料"""
        available = []
        for item_name in inventory.items:
            if item_name in self.MATERIAL_PROPERTIES:
                available.append(item_name)
        return available

    def has_materials(self, inventory: InventoryComponent, recipe: Dict[str, int]) -> bool:
        """检查材料是否充足"""
        for mat_name, amount in recipe.items():
            if inventory.items.get(mat_name, 0) < amount:
                return False
        return True

    def consume_materials(self, inventory: InventoryComponent, recipe: Dict[str, int]) -> None:
        """消耗材料"""
        to_delete = []
        for mat_name, amount in list(recipe.items()):
            inventory.items[mat_name] = inventory.items.get(mat_name, 0) - amount
            if inventory.items[mat_name] <= 0:
                to_delete.append(mat_name)
        for mat_name in to_delete:
            del inventory.items[mat_name]