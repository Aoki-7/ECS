
from core.system import System
from core.world import World
from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.light_field.components.light_scatter_component import LightScatterComponent



class LightAtmosphereCouplingSystem:
    """
        把大气变量转换为光学变量
    """
    def update(self, world: World, delta_hour: float):

        atmosphere, scatter = world._world_entity.get_components(
            AtmosphereComponent,
            LightScatterComponent
        )

        atmosphere: AtmosphereComponent
        scatter: LightScatterComponent

        # Rayleigh散射（空气密度）
        scatter.rayleigh_factor = 0.08 * atmosphere.air_density

        # Mie散射（气溶胶+湿度）
        scatter.mie_factor = (
            0.15 * atmosphere.aerosol +
            0.05 * atmosphere.humidity
        )

        # 云遮挡
        scatter.cloud_attenuation = (
            atmosphere.cloud_cover *
            (0.5 + atmosphere.cloud_density)
        )