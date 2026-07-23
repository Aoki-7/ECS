# AI Generated
"""
地形类型定义
使用基础类型定义，后续可根据物理量推导
"""

from enum import Enum


class TerrainType(Enum):
    """
    地形类型枚举

    所有地形类型的基础定义
    地形类型可以通过物理量（海拔、坡度、湿度等）推导得出
    """

    # 基础地形
    PLAIN = "plain"           # 平原
    HILL = "hill"             # 丘陵
    MOUNTAIN = "mountain"     # 山地
    VALLEY = "valley"         # 山谷

    # 水域地形
    WATER = "water"           # 水域（通用）
    LAKE = "lake"             # 湖泊
    RIVER = "river"           # 河流
    OCEAN = "ocean"           # 海洋

    # 植被地形
    FOREST = "forest"         # 森林
    GRASSLAND = "grassland"   # 草地
    JUNGLE = "jungle"         # 丛林

    # 特殊地形
    DESERT = "desert"         # 沙漠
    SWAMP = "swamp"           # 沼泽
    TUNDRA = "tundra"         # 苔原

    def __str__(self):
        """返回地形的中文描述"""
        return self._get_chinese_name()

    def _get_chinese_name(self) -> str:
        """获取地形的中文名称"""
        names = {
            TerrainType.PLAIN: "平原",
            TerrainType.HILL: "丘陵",
            TerrainType.MOUNTAIN: "山地",
            TerrainType.VALLEY: "山谷",
            TerrainType.WATER: "水域",
            TerrainType.LAKE: "湖泊",
            TerrainType.RIVER: "河流",
            TerrainType.OCEAN: "海洋",
            TerrainType.FOREST: "森林",
            TerrainType.GRASSLAND: "草地",
            TerrainType.JUNGLE: "丛林",
            TerrainType.DESERT: "沙漠",
            TerrainType.SWAMP: "沼泽",
            TerrainType.TUNDRA: "苔原",
        }
        return names.get(self, self.value)


# 地形类型分组
TERRAIN_GROUPS = {
    "land": [TerrainType.PLAIN, TerrainType.HILL, TerrainType.MOUNTAIN, TerrainType.VALLEY],
    "water": [TerrainType.WATER, TerrainType.LAKE, TerrainType.RIVER, TerrainType.OCEAN],
    "vegetation": [TerrainType.FOREST, TerrainType.GRASSLAND, TerrainType.JUNGLE],
    "special": [TerrainType.DESERT, TerrainType.SWAMP, TerrainType.TUNDRA],
}


def is_water_terrain(terrain_type: TerrainType) -> bool:
    """判断是否为水域地形"""
    return terrain_type in TERRAIN_GROUPS["water"]


def is_land_terrain(terrain_type: TerrainType) -> bool:
    """判断是否为陆地地形"""
    return terrain_type in TERRAIN_GROUPS["land"]


def is_vegetation_terrain(terrain_type: TerrainType) -> bool:
    """判断是否为植被地形"""
    return terrain_type in TERRAIN_GROUPS["vegetation"]