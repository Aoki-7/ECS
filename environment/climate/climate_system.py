

import random

from core.world import World
from environment.climate.climate_component import ClimateComponent

class ClimateSystem:
    
    def update(self, world: World, delta_hours):

        climate: ClimateComponent = world._world_entity.get_component(ClimateComponent)

        climate.phase_remaining_days -= delta_hours / 24

        if climate.phase_remaining_days <= 0:
            climate.climate_phase = random.choice(
                ["Neutral", "ElNino", "LaNina"]
            )
            climate.phase_remaining_days = random.uniform(90, 400)

        if climate.climate_phase == "ElNino":
            climate.rainfall_bias = 0.3
            climate.humidity_bias = 0.2

        elif climate.climate_phase == "LaNina":
            climate.rainfall_bias = -0.2