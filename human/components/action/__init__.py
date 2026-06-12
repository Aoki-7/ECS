"""
行动包 — 搜索、移动、进食、采集、建造

依赖：
    - human.components/
    - core/
    - biology/
    - space/
    - environment/
    - animal/
    - plant/
    - resource/
    - civilization/
    - memory_layer/

版本：v4.0

"""
# human/components/action/__init__.py
from .action_component import ActionComponent, ActionType, ActionStatus
from .search_component import SearchComponent

__all__ = ["ActionComponent", "ActionType", "ActionStatus", "SearchComponent"]

