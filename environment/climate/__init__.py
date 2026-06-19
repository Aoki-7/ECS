"""
气候子模块 — 长期气候趋势、随机过程

依赖:
    - environment/
    - core/
    - time_module/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
气候模块 — 长期气候趋势与统计

职责：
    - ClimateComponent: 存储某区域的气候基线（年均温、年降水、湿度基线等）
    - ClimateSystem: 使用 Ornstein-Uhlenbeck 过程生成气候趋势
    - 为 PhysicalWeatherSystem 提供长期偏移量，使天气具有"记忆性"

设计原理：
    - OU 过程：均值回归 + 随机扰动，模拟真实气候的年际波动
    - 气候基线由地形和纬度决定，短期天气在基线附近波动
    - 不同区域可配置不同气候基线（热带雨林 vs 极地冰原）
"""


