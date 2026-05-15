

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:__init__.py
@说明:环境模块
@时间:2026/03/04 13:29:22
@作者:Sherry
@版本:1.0
'''

"""

World
 └── Environment
      ├── Terrain      （静态约束）
      ├── Climate      （长期统计）
      ├── Season       （周期驱动）
      ├── Atmosphere   （物理层）
      ├── Weather      （天气状态）
      ├── LightField   （辐射场）
      ├── Hydrology    （水文）
      └── Soil         （地表物质）
 └── Time
 └── Space
"""

"""
每一个环境是一个实体，包含空间组件和其他组件。
是一个空间单元，环境具有连续性，连续性通过空间组件的相邻区域计算得到
并通过多个系统进行管理。

Season
   ↓
Climate
   ↓
Atmosphere
   ↓
Weather
   ↓
LightField
   ↓
Soil
   ↓
Vegetation（未来）

Terrain 应该是 最底层的环境约束。
因为它影响：
      水流
      气候
      光照
      植被
例如：
      海拔
      坡度
      地表类型

Terrain
   ↓
Climate
   ↓
Atmosphere
   ↓
Weather
   ↓
LightField
   ↓
Soil
"""