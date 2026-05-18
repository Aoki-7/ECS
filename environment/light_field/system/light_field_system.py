

from core.system import System
from core.world import World

from environment.light_field.components.light_scatter_component import LightScatterComponent
from environment.light_field.components.solar_radiation_component import SolarRadiationComponent
from environment.light_field.components.surface_light_component import SurfaceLightComponent


class LightFieldSystem(System):
    """
    根据太阳辐射、云层、大气散射等参数，计算地表光照强度
    云层
    大气散射
    直射光
    漫射光
    """
    def update(self, world: World, delta_hours: float = 0.0):

        radiation, scatter, surface = world._world_entity.get_components(
            SolarRadiationComponent,
            LightScatterComponent,
            SurfaceLightComponent
        )

        radiation: SolarRadiationComponent
        scatter: LightScatterComponent
        surface: SurfaceLightComponent

        # 太阳辐射
        toa = radiation.toa_radiation

        if toa <= 0:
            surface.direct_light = 0.0
            surface.diffuse_light = 0.0
            return

        # 云遮挡
        cloud_loss = scatter.cloud_attenuation

        # 大气散射
        scatter_loss = scatter.rayleigh_factor + scatter.mie_factor

        direct = toa * (1 - cloud_loss) * (1 - scatter_loss)

        diffuse = toa * scatter_loss

        surface.direct_light = max(direct, 0.0)
        surface.diffuse_light = max(diffuse, 0.0)