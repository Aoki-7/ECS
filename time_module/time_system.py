
from core.system import System
from core.world import World
from time_module.time_component import TimeComponent


import logging

logger = logging.getLogger(__name__)


class TimeSystem(System):
    tick_interval = 1  # 每1帧执行一次
    """
    纯时间推进系统
    - 支持时间倍率
    - 支持负时间
    - 支持跨多日快速推进
    - 每次 update 打印当前时间
    """

    def __init__(self, time_scale: float = 1.0, verbose: bool = True):
        if time_scale == 0:
            raise ValueError("time_scale cannot be 0")

        self.time_scale = time_scale
        self.verbose = verbose

    def update(self, world: World, dt: float = 1.0):
        delta_hours = dt

        scaled_delta = delta_hours * self.time_scale

        time = world.get_time()
        
        # 防御：如果 get_time() 返回 None，初始化一个默认时间
        if time is None:
            from time_module.time_component import TimeComponent
            time = TimeComponent()
            # 尝试将时间组件添加到世界实体
            world_entity = world.get_world_entity()
            if world_entity is not None:
                world.add_component(world_entity, time)
            else:
                # 如果连世界实体都没有，创建一个
                world_entity = world.create_entity()
                world.add_component(world_entity, time)
                world.set_world_entity(world_entity)
            logger.debug("[TimeSystem] 世界时间组件未初始化，已自动创建")
            world.set_time(time)

        # 更新总时间
        time.total_hours += scaled_delta
        
        # =
        # 小时推进
        # =
        total_hours = time.hour + scaled_delta

        # floor 除法在负数情况下仍然正确
        day_change = int(total_hours // time.day_hours)
        new_hour = total_hours - day_change * time.day_hours

        time.hour = new_hour

        # =
        # 日期推进
        # =
        if day_change != 0:
            time.day_of_year += day_change

            # 统一转成从 0 开始计算更安全
            zero_based_day = time.day_of_year - 1

            year_change = zero_based_day // time.days_per_year
            zero_based_day = zero_based_day % time.days_per_year

            time.day_of_year = zero_based_day + 1
            time.year += year_change

        # 只取第一个时间实体用于打印
        current_time_repr = (
            f"Year {time.year} | "
            f"Day {time.day_of_year} | "
            f"{time.hour:.2f}h"
        )

        # 时间打印已精简，不再每步输出