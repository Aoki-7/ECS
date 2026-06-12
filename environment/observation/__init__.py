"""
观测子模块 — 天气状态推导、异常检测

依赖:
    - environment/
    - core/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境观测模块 — 天气状态推导与异常检测

职责：
    - WeatherEventSystem  : 滑动窗口统计异常检测（|当前值-μ| > 2.5σ）
    - WeatherLifetimeSystem: 异常事件超时清理
    - WeatherClassifier   : 从连续物理量推导离散天气标签（晴/多云/小雨等）

设计原则：
    - 离散天气状态是连续物理量的"实时视图"，不存储、不直接驱动逻辑
    - 异常检测用于生成事件日志，供 presentation/ 和 human/ 的感知系统使用
"""


