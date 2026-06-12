"""
human/systems/physiological 子模块

依赖:
    - human/
    - core/
    - biology/
    - space/
    - environment/
    - memory_layer/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类生理系统包 — 需求更新与健康维护

包含：
    - PhysiologyNeedsSystem : 综合需求更新（饥饿、口渴、精力、社交，含环境耦合）
    - HealthSystem          : 健康状态综合评估与恢复

与 physiology/ 模块的关系：
    - human/systems/physiological/ 关注"人类特有的"需求计算（如文化因素影响口渴阈值）
    - physiology/ 关注"通用的"生理机能（代谢、体液、体温）
"""


