



from core.world import World
from core.system import System
from environment.season.season_component import SeasonComponent, Season
from environment.weather.components.weather_modifier_component import WeatherEventTagComponent
from environment.weather.weather_event_factory import WeatherEventFactory
import random


class WeatherEventSystem(System):
    """
    极端天气事件生成
    """
    def __init__(self, world: World, event_probability_per_hour: float = 0.002):
        self.world = world
        self.factory = WeatherEventFactory(world)
        self.event_probability = event_probability_per_hour

    def update(self, world: World, delta_hours: float):

        # ======================
        # 1 检查当前是否存在极端天气
        # ======================

        active_events = list(
            self.world.get_components(WeatherEventTagComponent)
        )

        if active_events:
            for _, [w_comp] in active_events:
                w_comp: WeatherEventTagComponent
                print("当前存在极端天气：", w_comp.name)
            return  # 已经存在极端天气，不生成新的

        # ======================
        # 2 按概率生成极端天气
        #    基础概率 = event_probability * delta_hours
        #    夏季极端天气更频繁（概率 x5）
        # ======================

        prob = self.event_probability * delta_hours

        season: SeasonComponent = self.world._world_entity.get_component(SeasonComponent)
        if season and season.season == Season.SUMMER:
            prob *= 5.0  # 夏季极端天气概率 x5

        if random.random() < prob:

            weather_event = self.factory.create_random_event()
            print("极端天气产生了！类型：", weather_event.__class__.__name__)