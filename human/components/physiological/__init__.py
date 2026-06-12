"""
生理包 — 健康、饥饿、口渴、睡眠

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
# human/components/physiological/__init__.py
from .death_component import DeathComponent

__all__ = ["DeathComponent"]

