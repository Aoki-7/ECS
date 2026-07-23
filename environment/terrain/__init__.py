"""
地形子模块 — 海拔、坡度、地表类型、通行性

依赖:
    - environment/
    - core/
    - space/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地形模块 — 地表类型与空间约束

职责：
    - TerrainComponent: 地形属性（类型、海拔、坡度、通行性）
    - TerrainType: 地形类型枚举（水域、平原、森林、山地、沙漠等）
    - TerrainClassifier: 根据海拔/湿度/温度自动分类地形
    - TerrainGenerator:  procedurally 生成地形分布

地形影响链：
    Terrain → Climate（海拔修正温度）
    Terrain → Soil（坡度影响水分保持）
    Terrain → LightField（山地阴影）
    Terrain → Human/Animal（通行性影响移动速度）
    Terrain → Plant（适宜物种分布）
"""

from .config.terrain_types import TerrainType, TERRAIN_GROUPS, is_water_terrain, is_land_terrain, is_vegetation_terrain
from .components.terrain_component import TerrainComponent
from .config.terrain_classifier import TerrainClassifier
from .config.terrain_generator import TerrainGenerator
from .config.terrain_config import get_terrain_config, get_classification_rules

__all__ = [
    # 类型
    'TerrainType',
    'TERRAIN_GROUPS',
    'is_water_terrain',
    'is_land_terrain',
    'is_vegetation_terrain',
    # 组件
    'TerrainComponent',
    # 分类器
    'TerrainClassifier',
    # 生成器
    'TerrainGenerator',
    # 配置
    'get_terrain_config',
    'get_classification_rules',
]

