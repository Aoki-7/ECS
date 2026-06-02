#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人类实体模块 — 人类实体的模板与预设

职责：
    - 定义标准人类实体的组件组合模板
    - 提供不同文化/职业/年龄段的预设配置
    - 被 HumanFactory 调用以快速创建多样化人口

与 human_factory.py 的关系：
    - entities/ 提供模板定义
    - human_factory.py 负责按模板实例化实体并注册到 World
"""
