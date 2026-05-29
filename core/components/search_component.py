#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:search_component.py
@说明:搜索组件，用来确定搜索的目标
@时间:2026/03/31 15:17:57
@作者:Sherry
@版本:1.0
'''

# 已从 human/components/abilities/search_component.py 迁移至此
# 向后兼容导入: from human.components.abilities.search_component import SearchComponent
from dataclasses import dataclass
from core.component import Component
from typing import Optional, Type


@dataclass
class SearchComponent(Component):
    """
    通用搜索组件（Search Component）

    为实体提供“搜索目标”的能力，通常由 SearchSystem 处理。

    典型流程：
        1. 实体携带该组件
        2. 系统根据 target_component 查找符合条件的实体
        3. 在 max_distance 范围内筛选最近目标
        4. 将结果写入 result_entity

    适用场景：
        - 寻找食物（FoodComponent）
        - 寻找水源（WaterComponent）
        - 寻找目标对象（任意组件标识）

    注意：
        - 该组件只描述“搜索意图”，不负责执行逻辑
        - 搜索结果由系统写入 result_entity
    """

    target_component: Optional[Type[Component]] = None
    """
    目标组件类型（用于筛选目标实体）

    示例：
        FoodComponent -> 查找所有拥有 FoodComponent 的实体

    说明：
        - 本质是“按组件类型筛选实体”
        - 为 None 时表示未指定目标（系统可忽略或跳过）
    """

    max_distance: float = float("inf")
    """
    最大搜索距离

    说明：
        - 限制搜索范围，避免全图扫描（性能关键）
        - 单位由你的世界坐标系统决定（如米、格子等）
        - 默认值为无限，表示不限制范围
    """

    result_entity: Optional[int] = None
    """
    搜索结果（目标实体ID）

    说明：
        - 由 SearchSystem 写入
        - 表示当前找到的最优目标（通常是最近的）
        - 未找到时为 None
        - 存放的是Entity.id（整数），而不是实体对象

    注意：
        - 不建议手动写入，应由系统统一维护
        - 可被其他系统使用（如移动、交互、攻击等）
    """