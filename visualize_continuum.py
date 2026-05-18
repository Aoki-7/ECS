#!/usr/bin/env python3
"""
环境连续统系统 — 可视化展示

实时动画展示 10×10 网格的 4 个环境变量：
  🌡  气温        — 热扩散、风驱平流
  💧  空气湿度     — 湿度扩散、湖-漠交换
  🌱  土壤水分     — 重力水流、蒸发回馈
  🌍  生态系统指数 — 自恢复、扰动康复

操作：空格 暂停/继续，+/- 加速/减速
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib
matplotlib.use("TkAgg")  # 稳定交互式后端
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch
import numpy as np

from core.world import World
from core.entity import Entity
from space.space_component import SpaceComponent
from environment.environment_component import EnvironmentComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import TerrainType
from environment.continuum.environmental_continuum_system import (
    EnvironmentalContinuumSystem,
)

# ─── 预设场景：3 种可切换的地形布局 ────────────────────────

SCENARIOS = {}

def _build_scenario_desert_oasis(world: World, grid: dict):
    """场景 A：沙漠绿洲 — 左上绿洲、右下沙漠、中间过渡"""
    for (x, y), e in grid.items():
        tc = world.get_component(e, TerrainComponent)
        ec = world.get_component(e, EnvironmentComponent)
        # 左上绿洲 (0-3, 0-3)
        if x < 4 and y < 4:
            tc.terrain_type = TerrainType.LAKE
            tc.elevation = 0.0
            ec.air_temperature = 18.0
            ec.air_humidity = 0.90
            ec.soil_moisture = 0.90
        # 右下沙漠 (6-9, 6-9)
        elif x >= 6 and y >= 6:
            tc.terrain_type = TerrainType.DESERT
            tc.elevation = 30.0
            ec.air_temperature = 42.0
            ec.air_humidity = 0.05
            ec.soil_moisture = 0.01
        # 左上-右下对角线走廊 — 渐变
        else:
            d = (x + y) / 18.0  # 0~1 归一化
            tc.terrain_type = TerrainType.PLAIN
            tc.elevation = 5.0 + d * 25.0
            ec.air_temperature = 20.0 + d * 22.0
            ec.air_humidity = 0.80 - d * 0.75
            ec.soil_moisture = 0.70 - d * 0.69

def _build_scenario_fire_recovery(world: World, grid: dict):
    """场景 B：森林火灾恢复 — 中心火烧区，周围健康森林"""
    for (x, y), e in grid.items():
        tc = world.get_component(e, TerrainComponent)
        ec = world.get_component(e, EnvironmentComponent)
        tc.terrain_type = TerrainType.FOREST
        # 中心 4×4 为火烧区
        if 3 <= x <= 6 and 3 <= y <= 6:
            tc.vegetation_cover = 0.05
            ec.air_temperature = 55.0  # 火烧后高温
            ec.air_humidity = 0.02
            ec.soil_moisture = 0.01
            ec.nitrogen = 2.0
            ec.phosphorus = 1.0
            ec.potassium = 3.0
            tc.elevation = 20.0
        else:
            tc.vegetation_cover = 0.85
            ec.air_temperature = 23.0
            ec.air_humidity = 0.72
            ec.soil_moisture = 0.45
            ec.nitrogen = 60.0
            ec.phosphorus = 30.0
            ec.potassium = 70.0
            tc.elevation = 20.0 + (x - 5) * 0.5  # 微起伏

def _build_scenario_mountain_river(world: World, grid: dict):
    """场景 C：山地河流 — 左高右低，河流从山上下山"""
    for (x, y), e in grid.items():
        tc = world.get_component(e, TerrainComponent)
        ec = world.get_component(e, EnvironmentComponent)
        # 高程从左到右递减
        tc.elevation = 50.0 - x * 5.0 + math.sin(y) * 2.0
        tc.slope = 5.0

        if x < 3:  # 高山
            tc.terrain_type = TerrainType.MOUNTAIN
            ec.air_temperature = 5.0
            ec.soil_moisture = 0.60
            ec.air_humidity = 0.70
        elif x > 7:  # 平原/三角洲
            tc.terrain_type = TerrainType.PLAIN
            ec.air_temperature = 25.0
            ec.soil_moisture = 0.30
            ec.air_humidity = 0.50
        else:  # 山麓
            tc.terrain_type = TerrainType.FOREST
            ec.air_temperature = 15.0 + (x - 3) * 2.5
            ec.soil_moisture = 0.50 - (x - 3) * 0.04
            ec.air_humidity = 0.60 - (x - 3) * 0.02

        ec.nitrogen = 30.0 + x * 5.0
        ec.phosphorus = 15.0 + x * 2.0
        ec.potassium = 40.0 + x * 3.0

    # 中间河道 (y=4~5, x=0~9)：更低高程、高湿度
    for x in range(10):
        for y in [4, 5]:
            e = grid[(x, y)]
            tc = world.get_component(e, TerrainComponent)
            ec = world.get_component(e, EnvironmentComponent)
            tc.elevation -= 8.0
            tc.terrain_type = TerrainType.LAKE if x > 2 else TerrainType.RIVER
            ec.soil_moisture = 0.95
            ec.air_humidity = 0.85
            ec.air_temperature = max(ec.air_temperature - 2.0, 8.0)


SCENARIOS = {
    "1": ("🌵 沙漠绿洲", _build_scenario_desert_oasis, "绿洲↔沙漠水分交换"),
    "2": ("🔥 火灾恢复", _build_scenario_fire_recovery, "火烧区→森林生态恢复"),
    "3": ("🏔 山地河流", _build_scenario_mountain_river, "高山水流→平原扩散"),
}


# ─── 核心可视化类 ───────────────────────────────────────

class ContinuumVisualizer:
    """环境连续统 10×10 网格动画可视化"""

    TERRAIN_COLORS = {
        TerrainType.PLAIN:    "#8BC34A",
        TerrainType.FOREST:   "#2E7D32",
        TerrainType.DESERT:   "#FFCC80",
        TerrainType.LAKE:     "#42A5F5",
        TerrainType.RIVER:    "#1E88E5",
        TerrainType.MOUNTAIN: "#8D6E63",
        TerrainType.TUNDRA:   "#BDBDBD",
        TerrainType.SWAMP:    "#6A1B9A",
    }

    def __init__(self, scenario_key="1", steps_per_frame=3, wind_deg=270.0):
        self.scenario_key = scenario_key
        self.steps_per_frame = steps_per_frame
        self.hour = 0
        self.paused = False
        self.speed = 1.0

        # ─ 构建世界 ─
        self.world = World()
        self.grid = self._create_base_grid()
        SCENARIOS[scenario_key][1](self.world, self.grid)

        # ─ 连续统系统 ─
        wind_label = {90: "东风 →", 270: "← 西风", 0: "↑ 北风", 180: "↓ 南风"}
        self.wind_deg = wind_deg
        self.continuum = EnvironmentalContinuumSystem(
            neighborhood="moore",
            boundary="reflective",
            prevailing_wind_deg=wind_deg,
        )

        # 手动触发气候顶极初始化
        self.continuum._init_climax_states(self.world, self.grid)
        self.wind_label = wind_label.get(wind_deg, f"{wind_deg}°")

        # ─ 提取数据用辅助 ─
        self._extract = lambda attr: np.array([
            [getattr(self.world.get_component(self.grid[(x, y)], EnvironmentComponent), attr)
             for y in range(10)]
            for x in range(10)
        ])

        # ─ 图形设置 ─
        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 12))
        self.fig.suptitle("", fontsize=14, fontweight="bold")
        self.fig.subplots_adjust(left=0.08, right=0.88, top=0.93, bottom=0.06, wspace=0.30, hspace=0.35)

        # 4 个子图
        self.ax_temp, self.ax_humid = self.axes[0]
        self.ax_moist, self.ax_eco = self.axes[1]

        self._setup_temp_plot()
        self._setup_humid_plot()
        self._setup_moist_plot()
        self._setup_eco_plot()

        # 状态信息
        self.info_text = self.fig.text(0.5, 0.01, "", ha="center", fontsize=10, family="monospace")

        # 键盘绑定
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)

        # 动画
        self.anim = animation.FuncAnimation(
            self.fig, self._animate, frames=None,
            interval=80, blit=False, cache_frame_data=False,
        )

    # ─── 网格创建 ──────────────────────────────────
    def _create_base_grid(self):
        grid = {}
        for x in range(10):
            for y in range(10):
                e = self.world.create_entity()
                self.world.add_component(e, SpaceComponent(x=x, y=y, layer=0))
                self.world.add_component(e, EnvironmentComponent(
                    air_temperature=20.0, soil_temperature=18.0,
                    air_humidity=0.50, soil_moisture=0.30,
                    nitrogen=30.0, phosphorus=15.0, potassium=40.0,
                ))
                self.world.add_component(e, TerrainComponent(
                    elevation=10.0, slope=0.0,
                    vegetation_cover=0.3, terrain_type=TerrainType.PLAIN,
                ))
                grid[(x, y)] = e
        return grid

    # ─── 子图设置 ──────────────────────────────────
    def _setup_temp_plot(self):
        ax = self.ax_temp
        ax.set_title("🌡 气温 (Air Temperature)", fontsize=12, fontweight="bold")
        ax.set_xlabel("X →"); ax.set_ylabel("Y →")
        ax.set_xticks(range(10)); ax.set_yticks(range(10))
        ax.set_xlim(-0.5, 9.5); ax.set_ylim(9.5, -0.5)

        data = self._extract("air_temperature")
        vmin, vmax = self._get_global_range("air_temperature")
        self.im_temp = ax.imshow(data.T, cmap="RdYlBu_r", vmin=vmin, vmax=vmax,
                                  origin="upper", aspect="equal")
        self.cb_temp = self.fig.colorbar(self.im_temp, ax=ax, fraction=0.046, pad=0.04)
        self.cb_temp.set_label("°C")

        # 风向箭头
        self.quiv = ax.quiver(
            np.arange(10), np.arange(10),
            np.full((10, 10), math.cos(math.radians(self.wind_deg))),
            np.full((10, 10), -math.sin(math.radians(self.wind_deg))),
            scale=30, width=0.015, color="gray", alpha=0.5,
        )

        # 单元格数值标签
        self.temp_labels = [[
            ax.text(x, y, "", ha="center", va="center", fontsize=7,
                    color="black" if vmin + vmax > 30 else "white")
            for y in range(10)
        ] for x in range(10)]

    def _setup_humid_plot(self):
        ax = self.ax_humid
        ax.set_title("💧 空气湿度 (Air Humidity)", fontsize=12, fontweight="bold")
        ax.set_xlabel("X →"); ax.set_ylabel("Y →")
        ax.set_xticks(range(10)); ax.set_yticks(range(10))
        ax.set_xlim(-0.5, 9.5); ax.set_ylim(9.5, -0.5)

        data = self._extract("air_humidity")
        self.im_humid = ax.imshow(data.T, cmap="Blues", vmin=0, vmax=1.0,
                                   origin="upper", aspect="equal")
        self.cb_humid = self.fig.colorbar(self.im_humid, ax=ax, fraction=0.046, pad=0.04)
        self.cb_humid.set_label("RH")

    def _setup_moist_plot(self):
        ax = self.ax_moist
        ax.set_title("🌱 土壤水分 (Soil Moisture)", fontsize=12, fontweight="bold")
        ax.set_xlabel("X →"); ax.set_ylabel("Y →")
        ax.set_xticks(range(10)); ax.set_yticks(range(10))
        ax.set_xlim(-0.5, 9.5); ax.set_ylim(9.5, -0.5)

        data = self._extract("soil_moisture")
        self.im_moist = ax.imshow(data.T, cmap="YlGnBu", vmin=0, vmax=1.0,
                                   origin="upper", aspect="equal")
        self.cb_moist = self.fig.colorbar(self.im_moist, ax=ax, fraction=0.046, pad=0.04)
        self.cb_moist.set_label("m³/m³")

        # 高程等高线和坡度箭头
        elev = np.array([[self.world.get_component(self.grid[(x, y)], TerrainComponent).elevation
                          for y in range(10)] for x in range(10)])
        self.contour = ax.contour(np.arange(10), np.arange(10), elev.T,
                                   levels=8, colors="white", linewidths=0.8, alpha=0.6)

    def _setup_eco_plot(self):
        ax = self.ax_eco
        ax.set_title("🌍 生态系统 (Ecosystem)", fontsize=12, fontweight="bold")
        ax.set_xlabel("X →"); ax.set_ylabel("Y →")
        ax.set_xticks(range(10)); ax.set_yticks(range(10))
        ax.set_xlim(-0.5, 9.5); ax.set_ylim(9.5, -0.5)

        # 地形底图
        terrain_grid = np.array([
            [self.world.get_component(self.grid[(x, y)], TerrainComponent).terrain_type
             for y in range(10)]
            for x in range(10)
        ])
        color_grid = np.array([
            [self._terrain_to_rgb(self.world.get_component(self.grid[(x, y)], TerrainComponent).terrain_type)
             for y in range(10)]
            for x in range(10)
        ])
        self.im_eco = ax.imshow(np.ones((10, 10, 3)), origin="upper", aspect="equal")

        # 生态健康指数（归一化指标）
        self.eco_data = ax.imshow(np.zeros((10, 10)), cmap="RdYlGn", vmin=0, vmax=1,
                                   origin="upper", aspect="equal", alpha=0.6)
        self.cb_eco = self.fig.colorbar(self.eco_data, ax=ax, fraction=0.046, pad=0.04)
        self.cb_eco.set_label("健康指数")

        # 地形文字标注
        self.terrain_labels = [[
            ax.text(x, y, "", ha="center", va="center", fontsize=7,
                    fontweight="bold", color="white")
            for y in range(10)
        ] for x in range(10)]

        # 图例
        for i, (ttype, color) in enumerate(self.TERRAIN_COLORS.items()):
            ax.plot([], [], "s", color=color, label=ttype.name)
        ax.legend(loc="upper left", fontsize=6, ncol=2,
                   bbox_to_anchor=(0, -0.15), framealpha=0.7)

    # ─── 辅助 ──────────────────────────────────────
    def _get_global_range(self, attr):
        """根据场景确定颜色映射范围"""
        ranges = {
            "air_temperature": (0, 60),
            "air_humidity":    (0, 1),
            "soil_moisture":   (0, 1),
        }
        return ranges.get(attr, (0, 1))

    def _terrain_to_rgb(self, ttype):
        color = self.TERRAIN_COLORS.get(ttype, "#CCCCCC")
        return np.array([int(color[i:i+2], 16) for i in (1, 3, 5)]) / 255.0

    def _compute_eco_health(self):
        """计算生态健康指数 0~1（结合温度、湿度、水分与顶极状态的接近程度）"""
        health = np.zeros((10, 10))
        for x in range(10):
            for y in range(10):
                e = self.grid[(x, y)]
                env = self.world.get_component(e, EnvironmentComponent)
                tc = self.world.get_component(e, TerrainComponent)
                ttype = tc.terrain_type
                # 获取该地形的顶极状态
                climax = self.continuum.CLIMAX_STATES.get(ttype, None) or \
                         self.continuum.CLIMAX_STATES.get(TerrainType.PLAIN)
                if not climax:
                    health[x, y] = 0.5
                    continue
                # 各维度的归一化距离
                d_temp = 1 - min(abs(env.air_temperature - climax["temp"]) / 30.0, 1.0)
                d_hum  = 1 - min(abs(env.air_humidity - climax["humid"]) / 1.0, 1.0)
                d_moist = 1 - min(abs(env.soil_moisture - climax["moist"]) / 1.0, 1.0)
                d_n = 1 - min(abs(env.nitrogen - climax["N"]) / 80.0, 1.0)
                health[x, y] = 0.25 * d_temp + 0.25 * d_hum + 0.25 * d_moist + 0.25 * d_n
        return health

    # ─── 键盘控制 ──────────────────────────────────
    def _on_key(self, event):
        if event.key == " ":
            self.paused = not self.paused
        elif event.key in ("+", "="):
            self.steps_per_frame = min(self.steps_per_frame + 2, 30)
        elif event.key == "-":
            self.steps_per_frame = max(self.steps_per_frame - 2, 1)
        elif event.key in ("r", "R"):
            # 重置 — 重新构建
            self.hour = 0
            for (x, y), e in self.grid.items():
                ec = self.world.get_component(e, EnvironmentComponent)
                tc = self.world.get_component(e, TerrainComponent)
                # 还原初始值（略）
            SCENARIOS[self.scenario_key][1](self.world, self.grid)
            self.continuum._init_climax_states(self.world, self.grid)

    # ─── 动画帧更新 ────────────────────────────────
    def _animate(self, frame):
        if not self.paused:
            for _ in range(self.steps_per_frame):
                self.continuum.update(self.world, 1.0)
                self.hour += 1

        # 更新标题
        scenario_name = SCENARIOS[self.scenario_key][0]
        status = "▶" if not self.paused else "⏸"
        self.fig.suptitle(
            f"{scenario_name}   |   ⏱ {self.hour}h   {status}   "
            f"💨 {self.wind_label}   "
            f"步长/帧: {self.steps_per_frame}   "
            f"[空格=暂停  +/-=速度  r=重置]",
            fontsize=13, fontweight="bold",
        )

        # 更新各子图
        self._update_temp()
        self._update_humid()
        self._update_moist()
        self._update_eco()

        # 信息条
        self.info_text.set_text(
            f"帧 {frame}  |  "
            f"总模拟 {self.hour}h ({self.hour//24}d {self.hour%24}h)  |  "
            f"扩散 ×{self.steps_per_frame} / 帧"
        )
        return []

    def _update_temp(self):
        data = self._extract("air_temperature")
        self.im_temp.set_array(data.T)
        for x in range(10):
            for y in range(10):
                self.temp_labels[x][y].set_text(f"{data[x,y]:.0f}")
        # 刷新 CB（略，固定范围）

    def _update_humid(self):
        data = self._extract("air_humidity")
        self.im_humid.set_array(data.T)

    def _update_moist(self):
        data = self._extract("soil_moisture")
        self.im_moist.set_array(data.T)

    def _update_eco(self):
        health = self._compute_eco_health()
        self.eco_data.set_array(health.T)
        for x in range(10):
            for y in range(10):
                e = self.grid[(x, y)]
                tc = self.world.get_component(e, TerrainComponent)
                abbrev = tc.terrain_type.name[:3]
                self.terrain_labels[x][y].set_text(abbrev)

    def show(self):
        plt.tight_layout()
        plt.show()


# ─── 入口 ──────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="环境连续统可视化")
    parser.add_argument("-s", "--scenario", choices=["1", "2", "3"], default="1",
                        help="场景编号: 1=沙漠绿洲 2=火灾恢复 3=山地河流")
    parser.add_argument("-w", "--wind", type=float, default=270.0,
                        help="盛行风方向（度，0=北 90=东 180=南 270=西，默认 270=西风）")
    parser.add_argument("--steps", type=int, default=3,
                        help="每帧模拟步数（默认 3）")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  场景: {SCENARIOS[args.scenario][0]}")
    print(f"  说明: {SCENARIOS[args.scenario][2]}")
    print(f"  风向: {args.wind}°")
    print(f"  操作: 空格=暂停  +/-=速度  r=重置场景")
    print("=" * 60)

    viz = ContinuumVisualizer(
        scenario_key=args.scenario,
        steps_per_frame=args.steps,
        wind_deg=args.wind,
    )
    viz.show()
