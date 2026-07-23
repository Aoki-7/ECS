"""
死亡档案 — 实体死亡记录、历史统计

职责：

依赖：
    - core/

"""
from death_archive.components.record_entry import RecordEntry
from death_archive.components.death_archive_component import DeathArchiveComponent
from death_archive.systems.death_archive_system import DeathArchiveSystem

__all__ = [
    "RecordEntry",
    "DeathArchiveComponent",
    "DeathArchiveSystem",
]
