"""
环境连续统系统 — 相邻单元格物质-能量交换

【核心概念】
    每个环境单元格不是孤立的。相邻单元格通过扩散、平流、重力水流
    互相影响，使 10×10 网格表现为一个有弹性的连续体。
    即使局部受到扰动（人为破坏/火灾/污染），邻近区域的物质-能量
    会自然流入，体现环境的自适应性和恢复性。

【物理模型 — 5 大机制】

    1. 🌡 热扩散 (Thermal Diffusion)
       傅里叶热传导：热流从高温区流向低温区。
       系数受植被覆盖和水域缓冲调节。

    2. 💧 湿度扩散 (Humidity Diffusion)
       水汽从高湿区向低湿区扩散。
       土壤水分通过地下渗流和毛细作用横向传递。

    3. 🌊 重力水流 (Gravity Water Flow)
       水分沿地形坡度从高海拔向低海拔渗透。
       坡度越大，流速越快。
       水域地形作为蓄水池，吸收/释放水分。

    4. 🌬 风驱平流 (Wind-driven Advection)
       盛行风将热量、水汽、CO₂ 顺风方向传递。
       使用单元格级风速和全局盛行风向。

    5. 🌿 生态自恢复 (Ecological Self-Recovery)
       每个单元格有一个"气候顶极状态"（由地形类型决定）。
       偏离越大，恢复力越强（sigmoid 驱动）。
       恢复速率因变量而异：气温快（小时级）→ 养分慢（天级）。

【数值稳定性】
    CFL 条件：diff_coeff * dt < 0.5
    对于 dt=1h，所有扩散系数设计在安全范围内。

【边界条件】
    reflective: 网格边缘无通量交换（默认）
    periodic: 左↔右、上↔下循环（模拟无限平面）

【性能】
    10×10 网格（100 单元格）× 8 邻域 = 800 次交换/步。
    纯 Python 下每步 < 1ms，完全不影响主循环。
"""

import math
from typing import Dict, List, Optional, Tuple

from core.world import World
from core.system import System
from core.entity import Entity

from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import (
    TerrainType,
    is_water_terrain,
)

from .continuum_config import *


class EnvironmentalContinuumSystem(System):
    """
    环境连续统系统

    在管线中应运行在 EnvironmentSyncSystem 之后，
    作为所有环境更新的"空间平滑"步骤。
    """

    def __init__(
        self,
        neighborhood: str = "moore",
        boundary: str = "reflective",
        prevailing_wind_deg: float = 270.0,
    ):
        super().__init__()
        self.neighborhood = neighborhood
        self.boundary = boundary
        self.prevailing_wind_direction = prevailing_wind_deg
        self._neighbor_offsets = (
            NEIGHBOR_OFFSETS_MOORE if neighborhood == "moore"
            else NEIGHBOR_OFFSETS_VON_NEUMANN
        )
        self._step_count = 0

    # ═══════════════════════════════════════════════
    # 🚀 主更新入口
    # ═══════════════════════════════════════════════

    def update(self, world: World, delta_hours: float):
        """
        主更新入口 — 执行所有邻域交互。

        分 5 个阶段执行：
        1. 热扩散
        2. 湿度扩散
        3. 重力水流
        4. 风驱平流
        5. 生态自恢复
        """
        self._step_count += 1

        # 构建空间索引
        grid = self._build_grid(world)
        if not grid:
            return

        # 限制时间步长防止震荡
        dt = min(delta_hours, 2.0)

        # 预计算边界范围（避免 _resolve_boundary 每次重复计算）
        xs = [k[0] for k in grid.keys()]
        ys = [k[1] for k in grid.keys()]
        bounds = (min(xs), max(xs), min(ys), max(ys))

        # 阶段 1-5
        self._apply_thermal_diffusion(world, grid, dt, bounds)
        self._apply_humidity_diffusion(world, grid, dt)
        self._apply_gravity_water_flow(world, grid, dt)
        self._apply_wind_advection(world, grid, dt)
        self._apply_self_recovery(world, grid, dt)

    # ═══════════════════════════════════════════════
    # 🧩 网格构建
    # ═══════════════════════════════════════════════

    def _build_grid(
        self, world: World
    ) -> Dict[Tuple[int, int], Entity]:
        """
        构建二维网格索引。

        返回 dict[(x,y) → Entity]，
        便于按坐标快速查找邻居及其组件。
        """
        grid: Dict[Tuple[int, int], Entity] = {}
        for entity, (space,) in world.get_components(SpaceComponent):
            if world.get_component(entity, EnvironmentComponent) is not None:
                grid[(space.x, space.y)] = entity
        return grid

    # ═══════════════════════════════════════════════
    # 🌡 阶段 1: 热扩散
    # ═══════════════════════════════════════════════

    def _apply_thermal_diffusion(
        self, world: World, grid: Dict, dt: float, bounds: Tuple
    ):
        """
        热扩散：傅里叶热传导。

        空气温度和土壤温度各自独立扩散。
        植被覆盖和水域调节扩散速度。
        """
        fluxes = {}  # key → net_temp_flux, net_soil_flux

        for (x, y), eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 植被阻尼 & 水域缓冲
            veg = terrain.vegetation_cover if terrain else 0.0
            is_water = (terrain is not None
                        and is_water_terrain(terrain.terrain_type))
            veg_damp = 1.0 - VEGETATION_THERMAL_DAMPING * veg
            water_buf = WATER_THERMAL_BUFFER if is_water else 1.0

            net_temp = 0.0
            net_soil = 0.0

            for dx, dy in self._neighbor_offsets:
                nk = self._resolve_boundary((x + dx, y + dy), grid, bounds)
                if nk is None or nk not in grid:
                    continue

                n_env = world.get_component(
                    grid[nk], EnvironmentComponent
                )
                n_terrain = world.get_component(
                    grid[nk], TerrainComponent
                )
                if n_env is None:
                    continue

                n_veg = n_terrain.vegetation_cover if n_terrain else 0.0
                n_water = (n_terrain is not None
                           and is_water_terrain(n_terrain.terrain_type))
                n_veg_damp = 1.0 - VEGETATION_THERMAL_DAMPING * n_veg
                n_water_buf = WATER_THERMAL_BUFFER if n_water else 1.0

                # 平均阻尼
                avg_damp = (veg_damp + n_veg_damp) / 2.0
                avg_buf = (water_buf + n_water_buf) / 2.0
                eff_temp = TEMP_DIFFUSION_COEFF * avg_damp * avg_buf

                # 大气温度
                dT = n_env.air_temperature - env.air_temperature
                flux = eff_temp * dT * dt
                flux = max(-MAX_TEMP_CHANGE_PER_STEP,
                           min(MAX_TEMP_CHANGE_PER_STEP, flux))
                net_temp += flux

                # 土壤温度
                eff_soil = SOIL_TEMP_DIFFUSION_COEFF * avg_damp
                dTs = n_env.soil_temperature - env.soil_temperature
                sflux = eff_soil * dTs * dt
                sflux = max(-MAX_TEMP_CHANGE_PER_STEP,
                            min(MAX_TEMP_CHANGE_PER_STEP, sflux))
                net_soil += sflux

            fluxes[(x, y)] = (net_temp, net_soil)

        # 应用通量
        n_nei = len(self._neighbor_offsets)
        for (x, y), (net_t, net_s) in fluxes.items():
            eid = grid[(x, y)]
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            # 归一化：除以邻居数以保持总能量守恒
            env.air_temperature += net_t / n_nei
            env.soil_temperature += net_s / n_nei
            env.air_temperature = max(-30.0, min(50.0, env.air_temperature))
            env.soil_temperature = max(-20.0, min(60.0, env.soil_temperature))

    # ═══════════════════════════════════════════════
    # 💧 阶段 2: 湿度扩散
    # ═══════════════════════════════════════════════

    def _apply_humidity_diffusion(
        self, world: World, grid: Dict, dt: float
    ):
        """
        湿度扩散：空气湿度 + 土壤湿度。
        水域作为湿度源向周围释放水汽。
        """
        fluxes = {}

        for (x, y), eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            is_water = (terrain is not None
                        and is_water_terrain(terrain.terrain_type))

            net_humid = 0.0
            net_moist = 0.0

            for dx, dy in self._neighbor_offsets:
                nk = self._resolve_boundary((x + dx, y + dy), grid)
                if nk is None or nk not in grid:
                    continue

                n_env = world.get_component(
                    grid[nk], EnvironmentComponent
                )
                if n_env is None:
                    continue

                # 空气湿度扩散
                dh = n_env.air_humidity - env.air_humidity
                net_humid += HUMIDITY_DIFFUSION_COEFF * dh * dt

                # 土壤湿度扩散
                dm = n_env.soil_moisture - env.soil_moisture
                m_flux = SOIL_MOISTURE_DIFFUSION_COEFF * dm * dt
                m_flux = max(-MAX_MOISTURE_CHANGE_PER_STEP,
                             min(MAX_MOISTURE_CHANGE_PER_STEP, m_flux))
                net_moist += m_flux

                # 水域额外释放水汽
                if is_water and n_env.air_humidity < 0.95:
                    net_humid += 0.02 * (1.0 - n_env.air_humidity) * dt

            fluxes[(x, y)] = (net_humid, net_moist)

        n_nei = len(self._neighbor_offsets)
        for (x, y), (net_h, net_m) in fluxes.items():
            eid = grid[(x, y)]
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            env.air_humidity += net_h / n_nei
            env.soil_moisture += net_m / n_nei
            env.air_humidity = max(0.01, min(1.0, env.air_humidity))
            env.soil_moisture = max(0.0, min(1.0, env.soil_moisture))

    # ═══════════════════════════════════════════════
    # 🌊 阶段 3: 重力水流
    # ═══════════════════════════════════════════════

    def _apply_gravity_water_flow(
        self, world: World, grid: Dict, dt: float
    ):
        """
        重力水流：水分沿地形坡度从高往低流。

        只处理下坡方向。坡度越大流速越快。
        水域作为蓄水池，持续向下游供水。
        """
        # 预取海拔
        elevs = {}
        waters = {}
        for key, eid in grid.items():
            terrain = world.get_component(eid, TerrainComponent)
            elevs[key] = terrain.elevation if terrain else 0.0
            waters[key] = (terrain is not None
                           and is_water_terrain(terrain.terrain_type))

        # 计算净水分损失/增益
        losses = {key: 0.0 for key in grid}

        for (x, y), eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue

            cur_elev = elevs[(x, y)]
            is_water = waters[(x, y)]
            available = 0.5 if is_water else env.soil_moisture

            for dx, dy in self._neighbor_offsets:
                nk = self._resolve_boundary((x + dx, y + dy), grid)
                if nk is None or nk not in grid:
                    continue

                # 只流向下坡
                elev_diff = cur_elev - elevs[nk]
                if elev_diff <= 0:
                    continue

                dist = math.sqrt(dx*dx + dy*dy)
                slope = elev_diff / max(dist, 0.1)

                flow = (
                    WATER_FLOW_BASE_RATE
                    * (slope ** WATER_FLOW_SLOPE_EXPONENT)
                    * available
                    * dt
                )
                flow = min(flow, env.soil_moisture * 0.5)

                losses[(x, y)] -= flow
                losses[nk] += flow

        # 应用
        for key, delta in losses.items():
            if abs(delta) < 1e-10:
                continue
            eid = grid[key]
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            env.soil_moisture += delta
            env.soil_moisture = max(0.0, min(1.0, env.soil_moisture))

    # ═══════════════════════════════════════════════
    # 🌬 阶段 4: 风驱平流
    # ═══════════════════════════════════════════════

    def _apply_wind_advection(
        self, world: World, grid: Dict, dt: float
    ):
        """
        风驱平流：盛行风将温度/湿度顺风传递。

        方向匹配度 = 风向与邻域方向的内积。
        匹配度正 → 顺风，负 → 逆风（忽略逆风）。
        """
        wind_rad = math.radians(self.prevailing_wind_direction)
        # 风向"来自"方向 → 转换为"指向"方向
        wind_vx = -math.sin(wind_rad)
        wind_vy = -math.cos(wind_rad)

        fluxes = {}

        for (x, y), eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            net_t = 0.0
            net_h = 0.0

            for dx, dy in self._neighbor_offsets:
                nk = self._resolve_boundary((x + dx, y + dy), grid)
                if nk is None or nk not in grid:
                    continue

                n_env = world.get_component(
                    grid[nk], EnvironmentComponent
                )
                if n_env is None:
                    continue

                # 从邻居到当前的方向向量
                dist = math.sqrt(dx * dx + dy * dy)
                to_vx = -dx / dist
                to_vy = -dy / dist

                # 方向匹配度
                match = to_vx * wind_vx + to_vy * wind_vy
                if match <= 0:
                    continue

                strength = WIND_ADVECTION_COEFF * env.wind_speed * match * dt
                strength = min(strength, 0.3)

                net_t += strength * (n_env.air_temperature - env.air_temperature)
                net_h += strength * (n_env.air_humidity - env.air_humidity)

            fluxes[(x, y)] = (net_t, net_h)

        n_nei = len(self._neighbor_offsets)
        for (x, y), (net_t, net_h) in fluxes.items():
            eid = grid[(x, y)]
            env = world.get_component(eid, EnvironmentComponent)
            if env is None:
                continue
            env.air_temperature += net_t / n_nei
            env.air_humidity += net_h / n_nei
            env.air_temperature = max(-30.0, min(50.0, env.air_temperature))
            env.air_humidity = max(0.01, min(1.0, env.air_humidity))

    # ═══════════════════════════════════════════════
    # 🌿 阶段 5: 生态自恢复
    # ═══════════════════════════════════════════════

    def _apply_self_recovery(
        self, world: World, grid: Dict, dt: float
    ):
        """
        生态自恢复：每个单元格向其"气候顶极状态"漂移。

        Δstate = rate × sigmoid(deviation) × deviation × dt

        偏离越大恢复越快（sigmoid 加速）。
        气温恢复快（小时），养分恢复慢（天）。
        """
        for key, eid in grid.items():
            env = world.get_component(eid, EnvironmentComponent)
            terrain = world.get_component(eid, TerrainComponent)
            if env is None:
                continue

            # 顶极状态
            if terrain and terrain.terrain_type:
                climax = TERRAIN_CLIMAX_STATE.get(
                    terrain.terrain_type, DEFAULT_CLIMAX
                )
            else:
                climax = DEFAULT_CLIMAX

            c_t, c_h, c_m, c_n, c_p, c_k = climax

            # 气温
            d = c_t - env.air_temperature
            env.air_temperature += RECOVERY_RATE_TEMPERATURE * self._sig(d) * d * dt

            # 空气湿度
            d = c_h - env.air_humidity
            env.air_humidity += RECOVERY_RATE_HUMIDITY * self._sig(d) * d * dt
            env.air_humidity = max(0.01, min(1.0, env.air_humidity))

            # 土壤湿度
            d = c_m - env.soil_moisture
            env.soil_moisture += RECOVERY_RATE_MOISTURE * self._sig(d) * d * dt
            env.soil_moisture = max(0.0, min(1.0, env.soil_moisture))

            # 氮
            d = c_n - env.nitrogen
            env.nitrogen += RECOVERY_RATE_NITROGEN * self._sig(d) * d * dt
            env.nitrogen = max(0.0, min(200.0, env.nitrogen))

            # 磷
            d = c_p - env.phosphorus
            env.phosphorus += RECOVERY_RATE_PHOSPHORUS * self._sig(d) * d * dt
            env.phosphorus = max(0.0, min(100.0, env.phosphorus))

            # 钾
            d = c_k - env.potassium
            env.potassium += RECOVERY_RATE_POTASSIUM * self._sig(d) * d * dt
            env.potassium = max(0.0, min(200.0, env.potassium))

    # ═══════════════════════════════════════════════
    # 🧮 辅助方法
    # ═══════════════════════════════════════════════

    def _resolve_boundary(
        self, coord: Tuple[int, int], grid: Dict,
        _bounds: Optional[Tuple[int, int, int, int]] = None,
    ) -> Optional[Tuple[int, int]]:
        """
        边界处理。

        reflective: 超出范围 → None（无邻居）
        periodic: 循环映射（适用于矩形网格）

        _bounds 可传 (min_x, max_x, min_y, max_y) 避免重复计算。
        """
        x, y = coord

        if not grid:
            return None

        if _bounds is not None:
            min_x, max_x, min_y, max_y = _bounds
        else:
            xs = [k[0] for k in grid.keys()]
            ys = [k[1] for k in grid.keys()]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

        if self.boundary == "reflective":
            if x < min_x or x > max_x or y < min_y or y > max_y:
                return None
            return (x, y)

        elif self.boundary == "periodic":
            w = max_x - min_x + 1
            h = max_y - min_y + 1
            x = ((x - min_x) % w) + min_x
            y = ((y - min_y) % h) + min_y
            return (x, y)

        return None

    @staticmethod
    def _sig(dev: float) -> float:
        """
        Sigmoid 形状函数，用于自适应恢复加速。

        σ(x) = 2/(1+e^(-K|x|)) - 1
        返回符号与 dev 相同，范围 [-1, 1]。
        """
        if dev == 0:
            return 0.0
        x = RECOVERY_SIGMOID_K * abs(dev)
        s = 2.0 / (1.0 + math.exp(-x)) - 1.0
        return s if dev > 0 else -s

    def report(self) -> str:
        return (
            f"EnvironmentalContinuumSystem\n"
            f"  Neighborhood: {self.neighborhood} "
            f"({len(self._neighbor_offsets)} neighbors)\n"
            f"  Boundary: {self.boundary}\n"
            f"  Wind: {self.prevailing_wind_direction:.0f} deg\n"
            f"  Steps: {self._step_count}"
        )
