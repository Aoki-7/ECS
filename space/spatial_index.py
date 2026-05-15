#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:spatial_index.py
@说明:Grid索引，实体ID -> 空间查询加速器
@时间:2026/03/09 13:00:37
@作者:Sherry
@版本:1.0
'''
from collections import defaultdict
from typing import Dict, Set, Tuple


class SpatialIndex:
    """
        实体ID → 空间查询加速器
        (x, y, layer) -> entity_id
    """
    def __init__(self):

        self.cells: Dict[Tuple[int, int, int], Set[int]] = defaultdict(set)

        self.entity_pos: Dict[int, Tuple[int, int, int]] = {}

    # -----------------------------------------------------

    def add(self, entity_id: int, x: int, y: int, layer: int):
        """
        添加实体到索引
        """
        key = (x, y, layer)

        self.cells[key].add(entity_id)

        self.entity_pos[entity_id] = key

    # -----------------------------------------------------

    def remove(self, entity_id: int):
        """
        移除实体到索引
        """
        pos = self.entity_pos.get(entity_id)

        if pos is None:
            return

        self.cells[pos].discard(entity_id)

        if not self.cells[pos]:
            del self.cells[pos]

        del self.entity_pos[entity_id]

    # -----------------------------------------------------

    def move(self, entity_id: int, x: int, y: int, layer: int):
        """
        移动实体到索引
        """
        old = self.entity_pos.get(entity_id)

        new = (x, y, layer)

        if old == new:
            return

        if old is not None:

            self.cells[old].discard(entity_id)

            if not self.cells[old]:
                del self.cells[old]

        self.cells[new].add(entity_id)

        self.entity_pos[entity_id] = new

    # -----------------------------------------------------

    def entities_at(self, x: int, y: int, layer: int = 0) -> Set[int]:
        """返回指定坐标上的实体ID集合"""
        return self.cells.get((x, y, layer), set())
