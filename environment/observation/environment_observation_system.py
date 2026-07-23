

from core.system import System
from core.world import World

from environment.season.season_component import SeasonComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.physics_weather.utils.weather_classifier import (
    classify_from_component,
)
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent

from environment.observation.environment_observation_component import (
    EnvironmentObservationComponent,
)


class EnvironmentObservationSystem(System):
    tick_interval = 20  # 每20帧执行一次

    def update(self, world: World, delta_hours: float):

        time = world.get_time()

        season, weather, atm, obs = world.get_world_entity().get_components(
            SeasonComponent,
            PhysicalWeatherComponent,
            AtmosphereComponent,
            EnvironmentObservationComponent,
        )
        season: SeasonComponent
        weather: PhysicalWeatherComponent
        atm: AtmosphereComponent
        obs: EnvironmentObservationComponent

        record = {}
        record.update(time.to_dict())
        record.update(season.to_dict())
        record.update(weather.to_dict())
        # 添加天气标签（从物理量实时推导）
        state = classify_from_component(weather)
        record["weather_label"] = state.label
        record["weather_full_label"] = state.full_label
        record.update(atm.to_dict())

        obs.history.append(record)
        
        # 限制历史记录大小
        if len(obs.history) > obs.max_history:
            obs.history = obs.history[-obs.max_history:]