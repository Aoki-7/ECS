from dataclasses import dataclass, asdict, fields
from enum import Enum
from typing import Any, Dict

from core.entity import Entity
from core.component_pool import component_pool


ENTITY_KEY_PREFIX = "__entity_key__"


@dataclass(slots=True)
class Component:
    """
    ECS 基础组件类

    to_dict / from_dict 提供 JSON 安全与可还原的序列化：
    - Enum 转 name 字符串
    - Entity 键转为带前缀的字符串，Entity 值转为 {"__entity__": True, ...}
    """
    def __new__(cls, *args, **kwargs):
        """从组件池获取实例，复用已回收的组件对象"""
        return component_pool.get(cls, *args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """导出为字典，Enum / Entity 自动转为可 JSON 序列化的形式"""
        return self._prepare_for_json(asdict(self))

    def _prepare_for_json(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.name
        if isinstance(obj, Entity):
            return {"__entity__": True, "id": obj.id, "generation": obj.generation}
        if isinstance(obj, set):
            return [self._prepare_for_json(v) for v in obj]
        if isinstance(obj, dict):
            return {
                self._entity_key(k): self._prepare_for_json(v)
                for k, v in obj.items()
            }
        if isinstance(obj, (list, tuple)):
            return [self._prepare_for_json(v) for v in obj]
        return obj

    @staticmethod
    def _entity_key(key: Any) -> Any:
        if isinstance(key, Entity):
            return f"{ENTITY_KEY_PREFIX}:{key.id}:{key.generation}"
        return key

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典还原，自动将字符串转回对应 Enum / Entity"""
        data = cls._restore_from_json(data)
        data = cls._convert_strings_to_enums(data)
        data = cls._convert_lists_to_sets(data)
        return cls(**data)

    @classmethod
    def _convert_lists_to_sets(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """将 dataclass 中声明为 set 类型的字段从列表还原为集合"""
        set_fields = {}
        from typing import get_origin
        for f in fields(cls):
            field_type = f.type
            if isinstance(field_type, type) and issubclass(field_type, set):
                set_fields[f.name] = True
            elif get_origin(field_type) is set:
                set_fields[f.name] = True

        result = {}
        for k, v in data.items():
            if k in set_fields and isinstance(v, list):
                v = set(v)
            result[k] = v
        return result

    @classmethod
    def _restore_from_json(cls, obj: Any) -> Any:
        if isinstance(obj, dict):
            if obj.get("__entity__"):
                return Entity(obj["id"], obj["generation"])
            return {
                cls._restore_key(k): cls._restore_from_json(v)
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [cls._restore_from_json(v) for v in obj]
        return obj

    @classmethod
    def _restore_key(cls, key: Any) -> Any:
        if isinstance(key, str) and key.startswith(f"{ENTITY_KEY_PREFIX}:"):
            _, id_str, gen_str = key.split(":", 2)
            return Entity(int(id_str), int(gen_str))
        return key

    @classmethod
    def _convert_strings_to_enums(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        enum_fields = {}
        for f in fields(cls):
            field_type = f.type
            if isinstance(field_type, type) and issubclass(field_type, Enum):
                enum_fields[f.name] = field_type

        result = {}
        for k, v in data.items():
            if k in enum_fields and isinstance(v, str):
                v = enum_fields[k][v]
            result[k] = v
        return result