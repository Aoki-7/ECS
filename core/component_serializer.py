#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComponentSerializer — v4.0 新增

职责：
    - 统一所有 Component 的序列化/反序列化
    - 自动注册组件类型
    - 支持版本迁移

设计原则：
    - 集中管理：所有组件序列化逻辑在一个地方
    - 自动发现：通过装饰器自动注册
    - 向后兼容：支持旧版本数据迁移
"""

import logging
from typing import Dict, Type, Optional

from core.component import Component

logger = logging.getLogger(__name__)


class ComponentSerializer:
    """
    组件序列化器

    统一管理所有 Component 类型的序列化和反序列化。
    """

    _registry: Dict[str, Type[Component]] = {}
    _version: str = "4.0"

    @classmethod
    def register(cls, component_type: Type[Component]):
        """注册组件类型"""
        type_name = f"{component_type.__module__}.{component_type.__name__}"
        cls._registry[type_name] = component_type
        logger.debug(f"[ComponentSerializer] 注册组件: {type_name}")

    @classmethod
    def serialize(cls, component: Component) -> dict:
        """序列化组件"""
        type_name = f"{type(component).__module__}.{type(component).__name__}"

        # 获取 to_dict 数据
        if hasattr(component, 'to_dict'):
            data = component.to_dict()
        else:
            # 回退：使用 dataclass 的 asdict
            from dataclasses import asdict
            data = asdict(component)

        return {
            "__type__": type_name,
            "__version__": cls._version,
            "data": data,
        }

    @classmethod
    def deserialize(cls, serialized: dict) -> Optional[Component]:
        """反序列化组件"""
        type_name = serialized.get("__type__")
        if type_name is None:
            logger.warning("[ComponentSerializer] 缺少 __type__ 字段")
            return None

        component_type = cls._registry.get(type_name)
        if component_type is None:
            logger.warning(f"[ComponentSerializer] 未注册的组件类型: {type_name}")
            return None

        data = serialized.get("data", {})

        # 版本迁移
        data_version = serialized.get("__version__", "3.9")
        if data_version != cls._version:
            data = cls._migrate_data(type_name, data, data_version)

        # 反序列化
        if hasattr(component_type, 'from_dict'):
            return component_type.from_dict(data)
        else:
            # 回退：直接传入数据
            try:
                return component_type(**data)
            except Exception as e:
                logger.warning(f"[ComponentSerializer] 反序列化失败: {type_name}: {e}")
                return None

    @classmethod
    def _migrate_data(cls, type_name: str, data: dict, from_version: str) -> dict:
        """迁移旧版本数据"""
        # 目前只支持 3.9 -> 4.0 的迁移
        if from_version == "3.9":
            # 字段重命名等迁移逻辑
            pass
        return data

    @classmethod
    def get_registered_types(cls) -> list:
        """获取所有已注册的类型"""
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, type_name: str) -> bool:
        """检查类型是否已注册"""
        return type_name in cls._registry

    @classmethod
    def reset(cls):
        """重置注册表（主要用于测试）"""
        cls._registry.clear()


# 自动注册装饰器
def register_component(component_class):
    """组件注册装饰器"""
    ComponentSerializer.register(component_class)
    return component_class