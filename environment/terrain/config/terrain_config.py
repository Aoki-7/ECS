# AI Generated
"""
地形配置
定义地形的默认参数和规则
"""

from typing import Dict, Tuple


# 地形类型参数配置
TERRAIN_CONFIG: Dict[str, Dict] = {
    "plain": {
        "elevation_range": (0, 500),
        "slope_range": (0, 10),
        "vegetation_cover_range": (0.1, 0.5),
        "vegetation_height_range": (0, 3),
        "roughness": 0.1,
        "description": "平原",
    },
    "hill": {
        "elevation_range": (500, 1500),
        "slope_range": (10, 30),
        "vegetation_cover_range": (0.3, 0.7),
        "vegetation_height_range": (2, 10),
        "roughness": 0.3,
        "description": "丘陵",
    },
    "mountain": {
        "elevation_range": (1500, 5000),
        "slope_range": (30, 60),
        "vegetation_cover_range": (0.0, 0.4),
        "vegetation_height_range": (0, 5),
        "roughness": 0.5,
        "description": "山地",
    },
    "valley": {
        "elevation_range": (-100, 200),
        "slope_range": (0, 5),
        "vegetation_cover_range": (0.5, 0.9),
        "vegetation_height_range": (5, 15),
        "roughness": 0.15,
        "description": "山谷",
    },
    "water": {
        "elevation_range": (-10, 1000),
        "slope_range": (0, 5),
        "water_depth_range": (0.5, 100),
        "roughness": 0.05,
        "description": "水域",
    },
    "forest": {
        "elevation_range": (0, 2000),
        "slope_range": (0, 30),
        "vegetation_cover_range": (0.7, 1.0),
        "vegetation_height_range": (10, 30),
        "roughness": 0.25,
        "description": "森林",
    },
    "grassland": {
        "elevation_range": (0, 1500),
        "slope_range": (0, 20),
        "vegetation_cover_range": (0.3, 0.7),
        "vegetation_height_range": (0.5, 2),
        "roughness": 0.2,
        "description": "草地",
    },
    "desert": {
        "elevation_range": (0, 1000),
        "slope_range": (0, 15),
        "vegetation_cover_range": (0.0, 0.1),
        "vegetation_height_range": (0, 1),
        "roughness": 0.4,
        "description": "沙漠",
    },
    "swamp": {
        "elevation_range": (0, 500),
        "slope_range": (0, 5),
        "vegetation_cover_range": (0.6, 0.9),
        "vegetation_height_range": (2, 8),
        "roughness": 0.2,
        "description": "沼泽",
    },
}


# 地形分类规则
TERRAIN_CLASSIFICATION_RULES = {
    "water": {
        "condition": lambda terrain, moisture: terrain.water_depth > 0.5,
        "priority": 1,
    },
    "mountain": {
        "condition": lambda terrain, moisture: terrain.elevation > 1500,
        "priority": 2,
    },
    "hill": {
        "condition": lambda terrain, moisture: terrain.elevation > 500,
        "priority": 3,
    },
    "valley": {
        "condition": lambda terrain, moisture: terrain.elevation < 0,
        "priority": 4,
    },
    "swamp": {
        "condition": lambda terrain, moisture: moisture > 0.8,
        "priority": 5,
    },
    "desert": {
        "condition": lambda terrain, moisture: moisture < 0.1,
        "priority": 6,
    },
    "forest": {
        "condition": lambda terrain, moisture: terrain.vegetation_cover > 0.7,
        "priority": 7,
    },
    "grassland": {
        "condition": lambda terrain, moisture: terrain.vegetation_cover > 0.3,
        "priority": 8,
    },
    "plain": {
        "condition": lambda terrain, moisture: True,
        "priority": 9,
    },
}


def get_terrain_config(terrain_type: str) -> Dict:
    """
    获取地形类型的配置

    Args:
        terrain_type: 地形类型名称

    Returns:
        地形配置字典
    """
    return TERRAIN_CONFIG.get(terrain_type, TERRAIN_CONFIG["plain"])


def get_classification_rules() -> Dict:
    """
    获取地形分类规则

    Returns:
        分类规则字典
    """
    return TERRAIN_CLASSIFICATION_RULES