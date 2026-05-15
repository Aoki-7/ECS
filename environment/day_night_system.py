



# simulation/environment/day_night_system.py

import math
from core.world import World

class DayNightSystem:

    def update(self, world: World):

        time = world.get_time()
        env = world.get_environment()

        light_curve = math.sin(math.pi * time.day_progress)

        # env.light_intensity = (
        #     max(0.0, light_curve) *
        #     env.day_length_factor
        # )