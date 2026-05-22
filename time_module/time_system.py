
from core.world import World
from time_module.time_component import TimeComponent


class TimeSystem:
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

    def update(self, world: World, delta_hours: float):

        scaled_delta = delta_hours * self.time_scale

        time = world.get_time()
        
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