

# core/category.py

from enum import Enum, auto


class EntityCategory(Enum):
    """
    全局实体分类（强约束）
    整个系统唯一来源
    """

    # ===== 生物 =====
    HUMAN = auto()
    ANIMAL = auto()
    PLANT = auto()
    MICROBE = auto()

    # ===== 物体 =====
    ITEM = auto()
    FOOD = auto()
    RESOURCE = auto()

    # ===== 抽象/组织 =====
    ORG = auto()
    LOCATION = auto()

    # ===== 系统/虚拟 =====
    SYSTEM = auto()
    EVENT = auto()

    UNKNOWN = auto()