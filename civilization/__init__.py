#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文明系统 — 技术、文化、知识、建筑、农业、制作

目录结构:
    civilization/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── systems/                 # 文明系统包
    │   ├── civilization_system.py     # CivilizationSystem: 文明阶段检测 (采集→农业→工业)
    │   ├── resource_gathering_system.py # ResourceGatheringSystem: 群体资源采集策略
    │   ├── construction_system.py     # ConstructionSystem: 建筑项目管理 (需求/资源/进度)
    │   ├── trade_system.py            # TradeSystem: 宏观贸易 (市场/路线/价格)
    │   └── technology_system.py       # TechnologySystem: 科技树管理 (研发/解锁/传播)
    └── tests/                 # 文明测试包

核心职责:
    1. 文明阶段检测:
       - CivilizationSystem: 基于科技与人口检测文明阶段
       - 阶段: 采集社会 → 农业社会 → 工业社会 → 信息社会
       - 阶段转换条件: 科技水平 + 人口密度 + 资源储备

    2. 群体资源采集:
       - ResourceGatheringSystem: 群体层面的资源采集策略
       - 效率计算: 工具水平 + 组织程度 + 环境适宜性
       - 资源分配: 采集 → 储备 → 消费 → 贸易

    3. 建筑项目:
       - ConstructionSystem: 建筑项目管理
       - 流程: 需求评估 → 资源分配 → 建造进度 → 质量检查
       - 建筑类型: 住宅/仓库/工坊/防御/宗教

    4. 宏观贸易:
       - TradeSystem: 群体间贸易
       - 市场供需: 价格浮动由供需关系决定
       - 贸易路线: 距离/风险/收益权衡

    5. 科技树:
       - TechnologySystem: 科技研发与管理
       - 研发进度: 知识积累 + 实验 + 传承
       - 技术解锁: 前置条件 + 概率
       - 知识传播: 交流/教育/文献

与其他模块的关系:
    - core/: 依赖 ECS 框架
    - human/: 文明关注"群体"，人类关注"个体"
      - 个体行为汇聚成群体趋势
      - 群体趋势反过来约束个体行为 (法律/道德/习俗)
    - resource/: 文明系统管理宏观资源配置
      - rules/ 处理微观资源转换 (食物腐败/技能提升)
      - civilization/ 处理宏观资源配置 (建筑/科技/贸易)
    - environment/: 气候影响农业产量，进而影响文明发展
    - society/: 文明阶段决定社会结构 (部落→村庄→城市→国家)
    - memory_layer/: 知识积累存储于记忆层，技术失传风险

设计原则:
    - 群体涌现: 个体简单行为 → 复杂文明现象
    - 技术可失传: 知识 tied to 实体，实体死亡 → 知识可能消失
    - 文明差异化: 不同文明可发展出完全不同的技术路线
    - 信息损失: 知识传播 = 重新生成，不是完美复制

版本: v4.0
"""

from .systems.civilization_system import CivilizationSystem
from .systems.resource_gathering_system import ResourceGatheringSystem
from .systems.construction_system import ConstructionSystem
from .systems.trade_system import TradeSystem
from .systems.technology_system import TechnologySystem

__all__ = [
    'CivilizationSystem',
    'ResourceGatheringSystem',
    'ConstructionSystem',
    'TradeSystem',
    'TechnologySystem'
]