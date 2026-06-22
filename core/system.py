from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.world import World


class System:
    """ECS 基础系统类"""

    priority = 0  # 默认优先级，数字越小越先执行
    tick_interval = 1  # 执行间隔（帧数），1表示每帧执行，2表示隔1帧执行

    def __init__(self):
        self._enabled = True
        self._last_duration = 0.0

    @property
    def is_enabled(self) -> bool:
        """检查系统是否启用"""
        return self._enabled

    @property
    def enabled(self) -> bool:
        """启用/禁用系统"""
        return self._enabled

    def set_enabled(self, value: bool):
        """启用/禁用系统"""
        self._enabled = value

    #     # 生命周期
    def on_add(self, world: World):
        """系统被添加到 world 时调用"""
        pass

    def on_remove(self, world: World):
        """系统从 world 移除时调用"""
        pass

    # 主执行入口
    def update(self, world: World, dt: float = 1.0) -> None:
        """
        系统主更新入口。
        
        子类应直接重写此方法，实现具体的系统逻辑。
        基类保留 enabled 检查作为统一前置条件。
        """
        if not self.enabled:
            return

    # 调试信息
    @property
    def last_duration(self):
        return self._last_duration

    def __repr__(self):
        return f"<System {self.__class__.__name__} enabled={self.enabled}>"
