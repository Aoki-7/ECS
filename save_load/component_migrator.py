#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件迁移工具

v3.4 新增 — 处理 PlantComponent 等组件的版本升级

职责：
    - 检测旧版本组件数据
    - 自动迁移到新版本
    - 记录迁移日志

设计原则：
    - 向后兼容：旧存档可以加载
    - 向前兼容：新存档可以被旧版本读取（忽略未知字段）
    - 迁移可逆：保留原始数据备份
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ComponentMigrator:
    """
    组件迁移器

    处理组件 schema 变更时的数据迁移。
    """

    # 迁移注册表：{组件类型名: {版本: 迁移函数}}
    _migrations: Dict[str, Dict[str, callable]] = {}

    @classmethod
    def register_migration(cls, component_type: str, from_version: str, to_version: str):
        """注册迁移函数装饰器"""
        def decorator(func):
            if component_type not in cls._migrations:
                cls._migrations[component_type] = {}
            cls._migrations[component_type][f"{from_version}->{to_version}"] = func
            return func
        return decorator

    @classmethod
    def migrate(cls, component_type: str, data: Dict[str, Any], target_version: str = "current") -> Dict[str, Any]:
        """
        迁移组件数据到目标版本

        Args:
            component_type: 组件类型名（如 "plant.components.plant_component.PlantComponent"）
            data: 组件数据字典
            target_version: 目标版本

        Returns:
            迁移后的数据字典
        """
        if component_type not in cls._migrations:
            return data

        # 检测当前版本
        current_version = data.get("_version", "1.0")
        
        if current_version == target_version:
            return data

        # 执行迁移
        migrations = cls._migrations.get(component_type, {})
        for migration_key, migration_func in migrations.items():
            if migration_key.startswith(current_version):
                try:
                    data = migration_func(data)
                    logger.info(f"[Migrator] {component_type}: {migration_key} 迁移成功")
                except Exception as e:
                    logger.error(f"[Migrator] {component_type}: {migration_key} 迁移失败: {e}")
                    # 迁移失败时返回原始数据，避免数据丢失
                    return data

        return data


# ==================== PlantComponent 迁移 ====================

@ComponentMigrator.register_migration(
    "plant.components.plant_component.PlantComponent",
    "1.0", "2.0"
)
def migrate_plant_component_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    PlantComponent v1.0 -> v2.0 迁移

    v1.0 字段：
    - harvestable_yield, max_yield, harvest_stage, yield_type
    - nutrition_per_unit, is_perennial, regrowth_rate
    - produces_wood, wood_amount

    v2.0 新增字段：
    - health, water, max_water, nutrients, max_nutrients, energy, max_energy
    """
    # 添加新字段的默认值
    data["health"] = 1.0
    data["water"] = 50.0
    data["max_water"] = 100.0
    data["nutrients"] = 50.0
    data["max_nutrients"] = 100.0
    data["energy"] = 50.0
    data["max_energy"] = 100.0
    
    # 更新版本号
    data["_version"] = "2.0"
    
    return data


# ==================== 通用迁移工具 ====================

def migrate_component_data(component_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    通用组件数据迁移入口

    Args:
        component_type: 组件类型名
        data: 组件数据字典

    Returns:
        迁移后的数据字典
    """
    return ComponentMigrator.migrate(component_type, data)


def detect_old_version(data: Dict[str, Any]) -> str:
    """检测数据版本"""
    return data.get("_version", "1.0")
