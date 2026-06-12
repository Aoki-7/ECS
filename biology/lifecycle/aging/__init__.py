"""
衰老包 — 衰老机制与老年期处理

依赖：
    - biology.lifecycle/
    - core/
    - identity/

版本：v4.0

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
衰老子模块 — 生物体随时间退化

职责：
    - 管理生物体从成熟到衰老的渐进式退化过程
    - 降低生理功能上限（代谢率、恢复速度、免疫力）
    - 增加死亡概率（与 biology/lifecycle/death/ 协作）

子模块：
    - systems/ : SenescenceSystem（衰老系统）

与 death/ 的关系：
    - aging/ 负责"渐进退化"
    - death/ 负责"死亡判定与执行"
    - aging 过程中产生的健康恶化会被 death 系统检测到并触发死亡
"""

