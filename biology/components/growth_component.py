


#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:growth.py
@说明:停用
@时间:2026/03/09 13:43:10
@作者:Sherry
@版本:1.0
'''


from core.component import Component

class GrowthComponent(Component):
    def __init__(self, rate: float, max_size: float):
        self.size = 1.0
        self.rate = rate
        self.max_size = max_size