#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件迁移工具测试

v3.4 新增
"""

import pytest

from save_load.component_migrator import (
    ComponentMigrator,
    migrate_plant_component_v1_to_v2,
    migrate_component_data,
    detect_old_version,
)


class TestComponentMigrator:
    """测试组件迁移器"""

    def test_detect_old_version(self):
        """测试版本检测"""
        assert detect_old_version({}) == "1.0"
        assert detect_old_version({"_version": "2.0"}) == "2.0"

    def test_plant_migration(self):
        """测试 PlantComponent 迁移"""
        old_data = {
            "harvestable_yield": 10.0,
            "max_yield": 20.0,
            "harvest_stage": 3,
            "yield_type": "berry",
        }
        
        migrated = migrate_plant_component_v1_to_v2(old_data)
        
        # 旧字段保留
        assert migrated["harvestable_yield"] == 10.0
        assert migrated["yield_type"] == "berry"
        
        # 新字段添加
        assert migrated["health"] == 1.0
        assert migrated["water"] == 50.0
        assert migrated["max_water"] == 100.0
        assert migrated["nutrients"] == 50.0
        assert migrated["energy"] == 50.0
        
        # 版本更新
        assert migrated["_version"] == "2.0"

    def test_migrate_component_data(self):
        """测试通用迁移入口"""
        old_data = {
            "harvestable_yield": 5.0,
            "yield_type": "wheat",
        }
        
        migrated = migrate_component_data(
            "plant.components.plant_component.PlantComponent",
            old_data
        )
        
        assert "health" in migrated
        assert "water" in migrated
        assert migrated["_version"] == "2.0"

    def test_no_migration_needed(self):
        """测试无需迁移的情况"""
        current_data = {
            "_version": "2.0",
            "health": 0.8,
            "water": 60.0,
        }
        
        migrated = migrate_component_data(
            "plant.components.plant_component.PlantComponent",
            current_data
        )
        
        # 数据应该不变
        assert migrated["health"] == 0.8
        assert migrated["water"] == 60.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
