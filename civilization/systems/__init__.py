"""
文明系统包 — 阶段检测、资源采集、建筑、贸易、科技

依赖:
    - civilization/
    - core/
    - human/
    - resource/
    - environment/

版本: v4.0
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文明系统包 — 群体社会演进的逻辑实现

包含：
    - CivilizationSystem      : 文明阶段检测与晋升
    - ResourceGatheringSystem : 群体资源采集效率与策略
    - ConstructionSystem      : 建筑项目进度管理
    - TradeSystem            : 宏观贸易与市场
    - TechnologySystem       : 科技树研发与解锁

执行优先级：
    - 通常在 SimulationLoop 中以 priority 70 执行
    - 位于所有个体系统之后，基于聚合数据做群体级判定
"""


