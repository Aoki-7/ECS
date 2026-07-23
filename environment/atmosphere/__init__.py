"""
大气子模块 — 气压、风场、对流、热力学

依赖:
    - environment/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大气模块 — 底层大气物理量计算

职责：
    - 提供气压、风场、气体组成、热交换等底层物理量
    - 为天气系统（physics_weather/）提供大气状态输入
    - 为光场系统（light_field/）提供散射参数

子模块：
    - components/    : AtmosphereComponent（大气成分、气压、气溶胶）
    - system/        : 大气物理系统群（对流、热力学、风场）

与 physics_weather/ 的区别：
    - atmosphere/    → 更底层的物理（大气结构、气体动力学）
    - physics_weather/ → 直接可观测的天气状态（温度、云量、降水）
"""

