from core.world import World

class System:
    """
    ECS 基础系统类
    """

    priority = 0  # 默认优先级，数字越小越先执行

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

    # ============================
    # 生命周期
    # ============================

    def on_add(self, world: World):
        """系统被添加到 world 时调用"""
        pass

    def on_remove(self, world: World):
        """系统从 world 移除时调用"""
        pass

    # ============================
    # 主执行入口
    # ============================

    def update(self, world: World, dt: float = 1.0):
        """
        不建议子类重写此方法。
        子类应重写 _update。
        """
        if not self.enabled:
            return
        self._update(world, dt)

    def _update(self, world: World, dt: float = 1.0):
        """
        子类必须实现
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} 必须实现 _update 方法"
        )

    # ============================
    # 调试信息
    # ============================

    @property
    def last_duration(self):
        return self._last_duration

    def __repr__(self):
        return f"<System {self.__class__.__name__} enabled={self.enabled}>"