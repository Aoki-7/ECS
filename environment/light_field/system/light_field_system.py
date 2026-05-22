

from core.system import System
from core.world import World

from environment.light_field.components.light_scatter_component import LightScatterComponent
from environment.light_field.components.solar_radiation_component import SolarRadiationComponent
from environment.light_field.components.surface_light_component import SurfaceLightComponent


class LightFieldSystem(System):
    """
    根据太阳辐射、云层、大气散射等参数，计算地表光照强度。

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

        # 大气散射（确保总损失不超过 1，避免直接光为负）
        scatter_loss = min(scatter.rayleigh_factor + scatter.mie_factor, 1.0)

        # 透射率：考虑云和散射的复合衰减
        # 云衰减与散射衰减为串联过程，用乘法
        transmittance = max(0.0, (1.0 - cloud_loss) * (1.0 - scatter_loss))

        direct = toa * transmittance

        # 漫射光：被散射的能量不会全部到达地面，部分反向散射回太空。
        # 典型地表反照率下，约 50% 散射能量向下成为漫射光；
        # 云层存在时，会再次拦截部分向下漫射光。
        diffuse_ratio = 0.5 * scatter_loss * (1.0 - cloud_loss * 0.5)
        diffuse = toa * max(0.0, diffuse_ratio)

        surface.direct_light = direct
        surface.diffuse_light = diffuse
