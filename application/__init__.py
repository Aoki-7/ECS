#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用层 — 模拟循环、世界构建、入口程序

目录结构:
    application/
    ├── __init__.py              # 本文件：包导出与公共接口
    ├── simulation_loop.py       # SimulationLoop: 模拟主循环 (初始化 → 运行 → 清理)
    ├── world_builder.py         # WorldBuilder: 世界构建器 (创建世界/注册系统/生成实体)
    ├── config_loader.py         # ConfigLoader: 配置加载 (从文件/命令行/默认值)
    └── tests/                   # 应用测试包

核心职责:
    1. 模拟主循环:
       - SimulationLoop: 模拟入口与主循环
       - 生命周期: 初始化 → 运行 → 暂停 → 恢复 → 清理
       - 支持固定步长 (fixed timestep) 和可变步长
       - 支持实时模式 (实时渲染) 和批处理模式 (后台运行)

    2. 世界构建:
       - WorldBuilder: 创建世界、注册系统、生成初始实体
       - 系统注册顺序: 按 SystemScheduler 依赖图自动排序
       - 实体生成: 按配置生成初始人口/植物/动物/环境
       - 地图生成: 创建地形/气候/土壤初始状态

    3. 配置加载:
       - ConfigLoader: 从配置文件/命令行参数/环境变量加载配置
       - 配置内容: 世界大小/初始人口/系统参数/渲染设置
       - 配置验证: 检查配置合法性，提供默认值

    4. 模块整合:
       - 整合所有子系统形成完整模拟
       - 框架与领域之间的胶水层
       - 允许导入任何下层模块 (core, space, time_module, environment, human, biology, ...)
       - 不允许被 domain/ 内的业务系统反向导入

与其他模块的关系:
    - core/: 依赖 ECS 框架 (World/System/Entity)
    - space/: 创建空间索引和地图
    - time_module/: 创建时间系统和调度器
    - environment/: 创建环境实体和管线
    - biology/: 创建生物系统
    - animal/: 创建动物工厂和初始种群
    - plant/: 创建植物工厂和初始植被
    - human/: 创建人类工厂和初始人口
    - civilization/: 创建文明系统
    - memory_layer/: 创建记忆层实例
    - save_load/: 创建存档系统
    - presentation/: 创建可视化仪表盘
    - 所有模块: application/ 是最高层，整合所有下层模块

设计原则:
    - 胶水层: 框架与领域之间的桥梁，不实现业务逻辑
    - 单向依赖: 允许导入下层，不允许被下层导入
    - 可配置: 所有参数可通过配置调整，无硬编码
    - 可扩展: 支持添加新模块，无需修改现有代码

版本: v4.0
"""

from .simulation_loop import SimulationLoop

__all__ = ["SimulationLoop"]