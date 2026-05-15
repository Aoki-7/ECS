
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
# from environment.soil.components.soil_component import SoilComponent

from environment.observation.environment_observation_component import (
    EnvironmentObservationComponent,
)


class EnvironmentObservationSystem(System):

    def update(self, world: World, delta_hours: float):

        time = world.get_time()

        season, weather, atm, obs = world._world_entity.get_components(
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

        # print("时间:", time.to_dict())
        print("天气:", weather)
        print("天气标签:", state.full_label)
