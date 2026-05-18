"""
把大气变量转换为光学变量

从 AtmosphereComponent + PhysicalWeatherComponent 读取大气/云参数，
写入 LightScatterComponent 供 LightFieldSystem 使用。

当 AtmosphereComponent 不存在时，使用物理默认值。
"""

from core.system import System
from core.world import World

from environment.atmosphere.components.atmosphere_component import AtmosphereComponent
from environment.physics_weather.components.physical_weather_component import (
    PhysicalWeatherComponent,
)
from environment.light_field.components.light_scatter_component import (
    LightScatterComponent,
)


class LightAtmosphereCouplingSystem(System):
    """大气-光耦合系统"""

    # 默认大气常数（当 AtmosphereComponent 不存在时使用）
    DEFAULT_AIR_DENSITY = 1.225       # kg/m³ 海平面标准
    DEFAULT_AEROSOL = 0.05            # 轻污染
    DEFAULT_HUMIDITY = 50.0           # 50% (0-100 scale)
    DEFAULT_CLOUD_DENSITY = 0.3       # 中等云密度

    def update(self, world: World, delta_hour: float):
        results = world._world_entity.get_components(
            AtmosphereComponent,
            PhysicalWeatherComponent,
            LightScatterComponent,
        )

        atmosphere, weather, scatter = results

        if scatter is None:
            return

        # ── Rayleigh 散射 ──
        air_density = (
            atmosphere.air_density
            if atmosphere is not None
            else self.DEFAULT_AIR_DENSITY
        )
        scatter.rayleigh_factor = 0.08 * air_density

        # ── Mie 散射 ──
        if atmosphere is not None:
            aerosol = atmosphere.aerosol
            atm_humidity = atmosphere.humidity if atmosphere.humidity else self.DEFAULT_HUMIDITY
            cloud_density = atmosphere.cloud_density
        else:
            aerosol = self.DEFAULT_AEROSOL
            atm_humidity = self.DEFAULT_HUMIDITY
            cloud_density = self.DEFAULT_CLOUD_DENSITY

        scatter.mie_factor = 0.15 * aerosol + 0.05 * (atm_humidity / 100.0)

        # ── 云遮挡 ──
        weather_cloud = weather.cloud_cover if weather is not None else 0.0
        combined_cloud = max(weather_cloud, cloud_density)
        scatter.cloud_attenuation = combined_cloud * (0.5 + cloud_density)
