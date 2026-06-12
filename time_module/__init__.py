"""
时间系统 — 时间推进、调度器、事件触发

职责：
    - 世界时间推进与事件调度
    - 最小堆调度器支持一次性/周期性/条件性事件
    - 为所有需要时间感知的系统提供时间服务

依赖：
    - core/

"""
from .time_component import TimeComponent
from .time_scheduler import TimeScheduler

__all__ = ["TimeComponent", "TimeScheduler"]

