

from core.world import World
from core.system import System
from environment.season.season_component import SeasonComponent


from environment.season.season_state import Season, SEASON_EFFECT


class SeasonSystem(System):
    """
    季节系统

    提供长期气候趋势
    """

    def update(self, world: World, delta_hours: float):

        season: SeasonComponent = world._world_entity.get_component(
            SeasonComponent
        )

        # =
        # 1 更新年份时间
        # =

        season.year_progress += delta_hours

        if season.year_progress > season.year_length_hours:
            season.year_progress = 0

        # =
        # 2 更新季节时间
        # =

        season.season_remaining_hours -= delta_hours

        if season.season_remaining_hours <= 0:

            season.season = self._next_season(season.season)

            season.season_remaining_hours = 90 * 24

        # =
        # 3 更新季节气候
        # =

        effect = SEASON_EFFECT[season.season]

        season.temperature_offset = effect["temp"]
        season.rainfall_factor = effect["rain"]
        season.sunlight_factor = effect["sun"]

    def _next_season(self, season):

        order = [
            Season.SPRING,
            Season.SUMMER,
            Season.AUTUMN,
            Season.WINTER
        ]

        i = order.index(season)

        return order[(i + 1) % 4]