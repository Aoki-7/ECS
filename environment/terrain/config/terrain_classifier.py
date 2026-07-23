# AI Generated
"""
地形类型推导器
根据物理量推导地形类型
"""

from environment.terrain.config.terrain_types import TerrainType
from environment.terrain.components.terrain_component import TerrainComponent


class TerrainClassifier:
    """
    地形类型推导器

    根据地形的物理属性（海拔、坡度、水深等）推导地形类型
    """

    @staticmethod
    def classify(terrain: TerrainComponent, soil_moisture: float = 0.5) -> TerrainType:
        """
        根据地形属性推导地形类型

        Args:
            terrain: 地形组件
            soil_moisture: 土壤湿度 (0-1)

        Returns:
            TerrainType: 推导出的地形类型
        """
        # 1. 优先判断水域
        if terrain.water_depth > 0.5:
            return TerrainType.WATER

        # 2. 根据海拔和坡度判断地形
        if terrain.elevation > 1500:
            return TerrainType.MOUNTAIN
        elif terrain.elevation > 500:
            return TerrainType.HILL
        elif terrain.elevation < 0:
            return TerrainType.VALLEY

        # 3. 根据湿度判断特殊地形
        if soil_moisture > 0.8:
            return TerrainType.SWAMP
        elif soil_moisture < 0.1:
            return TerrainType.DESERT

        # 4. 根据植被覆盖判断
        if terrain.vegetation_cover > 0.7:
            return TerrainType.FOREST
        elif terrain.vegetation_cover > 0.3:
            return TerrainType.GRASSLAND

        # 5. 默认为平原
        return TerrainType.PLAIN

    @staticmethod
    def get_terrain_properties(terrain_type: TerrainType) -> dict:
        """
        获取地形类型的典型属性范围

        Args:
            terrain_type: 地形类型

        Returns:
            dict: 包含典型属性范围的字典
        """
        properties = {
            TerrainType.PLAIN: {
                "elevation": (0, 500),
                "slope": (0, 10),
                "vegetation_cover": (0.1, 0.5),
                "description": "平坦的陆地，适合农业和建筑"
            },
            TerrainType.HILL: {
                "elevation": (500, 1500),
                "slope": (10, 30),
                "vegetation_cover": (0.3, 0.7),
                "description": "起伏的丘陵，适合林业"
            },
            TerrainType.MOUNTAIN: {
                "elevation": (1500, 5000),
                "slope": (30, 60),
                "vegetation_cover": (0.0, 0.4),
                "description": "高海拔山地，岩石裸露"
            },
            TerrainType.VALLEY: {
                "elevation": (-100, 200),
                "slope": (0, 5),
                "vegetation_cover": (0.5, 0.9),
                "description": "低洼山谷，水源丰富"
            },
            TerrainType.WATER: {
                "elevation": (-10, 1000),
                "slope": (0, 5),
                "water_depth": (0.5, 100),
                "description": "水域，包括湖泊、河流等"
            },
            TerrainType.FOREST: {
                "elevation": (0, 2000),
                "slope": (0, 30),
                "vegetation_cover": (0.7, 1.0),
                "description": "茂密的森林，生物多样性高"
            },
            TerrainType.GRASSLAND: {
                "elevation": (0, 1500),
                "slope": (0, 20),
                "vegetation_cover": (0.3, 0.7),
                "description": "开阔的草地，适合放牧"
            },
            TerrainType.DESERT: {
                "elevation": (0, 1000),
                "slope": (0, 15),
                "vegetation_cover": (0.0, 0.1),
                "description": "干旱地区，植被稀少"
            },
            TerrainType.SWAMP: {
                "elevation": (0, 500),
                "slope": (0, 5),
                "vegetation_cover": (0.6, 0.9),
                "description": "湿地沼泽，水位较高"
            },
        }

        return properties.get(terrain_type, {})