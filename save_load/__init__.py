"""
存档系统 — 世界序列化、增量存档、自动保存

职责：
    - 世界状态序列化与反序列化
    - 增量存档（只保存差异）
    - 自动保存与存档管理

依赖：
    - core/
    - memory_layer/

"""
from save_load.systems.save_load_system import SaveLoadSystem

__all__ = ["SaveLoadSystem"]


"""
存档读取系统

"""
