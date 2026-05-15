# AI Generated
"""
光场系统
处理光照计算和阴影
"""

import math
from core.system import System
from core.world import World
from environment.light_field.components.light_field_component import LightFieldComponent
from environment.terrain.components.terrain_component import TerrainComponent


class LightFieldSystem(System):
    """
    光场系统

    负责更新光照状态：
    - 计算太阳位置
    - 计算光照强度
    - 处理阴影
    """

    def __init__(self):
        super().__init__()
        self.priority = 5

    def update(self, world: World, delta_hours: float):
        """
        更新所有光场组件
        """
        time = world.get_time()

        # 计算太阳位置
        sun_elevation, sun_azimuth = self._compute_sun_position(time)

        # 遍历所有拥有LightFieldComponent的实体
        for entity, (light, terrain) in world.get_components(
            LightFieldComponent, TerrainComponent
        ):
            self._update_light_field(light, terrain, sun_elevation, sun_azimuth, delta_hours)

    def _compute_sun_position(self, time) -> tuple[float, float]:
        """
        计算太阳位置（简化模型）

        返回：(高度角, 方位角)
        """
        # 简化模型：根据一天中的时间计算太阳位置
        # 假设太阳在6点升起，18点落下

        hour = time.hour
        day_hours = time.day_hours

        # 计算白天进度 (0-1)
        sunrise = 6.0
        sunset = 18.0

        if hour < sunrise or hour > sunset:
            # 夜晚
            elevation = 0.0
            azimuth = 180.0
        else:
            # 白天
            day_progress = (hour - sunrise) / (sunset - sunrise)

            # 高度角：正午最高
            elevation = 90.0 * math.sin(day_progress * math.pi)

            # 方位角：从东到西
            azimuth = 90.0 + day_progress * 180.0

        return elevation, azimuth

    def _update_light_field(
        self,
        light: LightFieldComponent,
        terrain: TerrainComponent,
        sun_elevation: float,
        sun_azimuth: float,
        delta_hours: float
    ):
        """
        更新单个光场组件
        """
        # 更新太阳位置
        light.sun_elevation = sun_elevation
        light.sun_azimuth = sun_azimuth

        # 计算基础光照强度
        if sun_elevation > 0:
            # 白天
            base_par = 300.0 * math.sin(math.radians(sun_elevation))
            light.total_radiation = 500.0 * math.sin(math.radians(sun_elevation))
        else:
            # 夜晚
            base_par = 0.0
            light.total_radiation = 0.0

        # 计算阴影
        self._compute_shadow(light, terrain, sun_elevation, sun_azimuth)

        # 应用阴影影响
        if light.in_shadow:
            shadow_factor = 1.0 - light.shadow_intensity
            light.par = base_par * shadow_factor
            light.direct_radiation = light.total_radiation * 0.7 * shadow_factor
        else:
            light.par = base_par
            light.direct_radiation = light.total_radiation * 0.7

        # 散射辐射（不受阴影影响）
        light.diffuse_radiation = light.total_radiation * 0.3

        # 计算光照时长
        if light.par > 0:
            light.light_duration += delta_hours

    def _compute_shadow(
        self,
        light: LightFieldComponent,
        terrain: TerrainComponent,
        sun_elevation: float,
        sun_azimuth: float
    ):
        """
        计算阴影（简化模型）
        """
        if sun_elevation <= 0:
            # 夜晚
            light.in_shadow = True
            light.shadow_intensity = 1.0
            return

        # 根据坡度和坡向计算阴影
        # 简化模型：如果坡向背对太阳，则可能有阴影

        # 计算坡向与太阳方位角的差值
        aspect_diff = abs(terrain.aspect - sun_azimuth)
        if aspect_diff > 180:
            aspect_diff = 360 - aspect_diff

        # 如果坡度较大且背对太阳，则产生阴影
        if terrain.slope > 30 and aspect_diff > 90:
            light.in_shadow = True
            light.shadow_intensity = min(0.8, terrain.slope / 90.0)
        else:
            light.in_shadow = False
            light.shadow_intensity = 0.0
