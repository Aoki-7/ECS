# AI Generated
"""
地形模块

提供地形相关的组件、系统和工具
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
