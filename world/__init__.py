"""
世界实体 — 全局世界实体与配置组件

职责：

依赖：
    - core/

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界实体模块 — 全局单例组件容器

职责：
    - WorldEntity: 轻量级单例实体，专门用于挂载"世界级别"的组件
    - 存储全局共享状态，如 TimeComponent、EnvironmentComponent、PhysicalWeatherComponent 等
    - 通过 World.get_world_component() 提供全局访问接口

与 core.World 的区别：
    - core.World     → ECS 引擎核心，管理所有实体/组件/系统的双向索引与调度
    - world.WorldEntity → 业务层的全局状态容器，仅存储单例组件

典型用法：
    world.set_world_entity(WorldEntity())
    world_entity.add_component(TimeComponent())
    time_comp = world.get_world_component(TimeComponent)
"""

from .world_entity import WorldEntity

__all__ = [
    "WorldEntity",
]
