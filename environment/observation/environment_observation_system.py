

from core.system import System
from core.world import World

from environment.season.season_component import SeasonComponent
from environment.weather.components.weather_component import WeatherComponent
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
# from environment.soil.components.soil_component import SoilComponent

from environment.observation.environment_observation_component import EnvironmentObservationComponent


class EnvironmentObservationSystem(System):

    def update(self, world: World, delta_hours: float):

        time = world.get_time()

        season, weather, atm, obs = world._world_entity.get_components(
            SeasonComponent,
            WeatherComponent,
            AtmosphereComponent,
            EnvironmentObservationComponent,

        )
        season: SeasonComponent
        weather: WeatherComponent
        atm: AtmosphereComponent
        obs: EnvironmentObservationComponent


        record = {}
        record.update(time.to_dict())
        record.update(season.to_dict())
        record.update(weather.to_dict())
        record.update(atm.to_dict())
        
        obs.history.append(record)

        # print("时间:", time.to_dict())
        print("天气:", weather.to_dict())