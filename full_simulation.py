#!/usr/bin/env python3
"""
全面模拟入口模块 (Full Simulation)

该脚本基于 main.py 的 SimulationLoop 扩展，整合所有可用系统：
- 环境系统：完整天气、季节、气候、大气、光照、连续体同步
- 资源系统：食物腐败/清理、木材腐朽、石头风化、金属氧化、资源再生
- 生物系统：基因表达、植物生长、形态变化、死亡判定
- 人类系统：完整生理、认知、社交、生存、采集、身份、导航
- 文明系统：资源采集、建筑、贸易、科技树
- 规则系统：食物腐败、资源枯竭、技能提升、财富积累

运行方式：
    python full_simulation.py
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
import math
import random

# =========================================================
# 复用 main.py 的核心模拟循环
# =========================================================
from main import SimulationLoop

# =========================================================
# 额外系统导入
# =========================================================

# 环境同步与资源再生
from environment.systems.environment_sync_system import EnvironmentSyncSystem
from environment.systems.resource_regeneration_system import ResourceRegenerationSystem

# 资源腐败与清理系统
from resource.food.systems.food_clean_up_system import FoodCleanupSystem
from resource.food.systems.food_decay_system import FoodDecaySystem
from resource.wood.systems.wood_decay_system import WoodDecaySystem
from resource.stone.systems.stone_weather_system import StoneWeatherSystem
from resource.metal.systems.metal_oxidation_system import MetalOxidationSystem
from garbage.systems.garbage_cleanup_system import GarbageCleanupSystem

# 人类额外系统
from human.systems.identity.identity_system import IdentitySystem
from human.systems.identity.age_system import AgeSystem

# 额外工厂
from plant.plant_factory import PlantFactory
from resource.wood.wood_factory import WoodFactory
from resource.stone.stone_factory import StoneFactory
from resource.metal.metal_factory import MetalFactory

# 额外组件（用于统计）
from biology.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.components.morphology_component import MorphologyComponent
from resource.wood.components.wood_component import WoodComponent
from resource.stone.components.stone_component import StoneComponent
from resource.metal.components.metal_component import MetalComponent
from environment.environment_component import EnvironmentComponent


class FullSimulationLoop(SimulationLoop):
    """
    全面模拟循环 —— 扩展自 SimulationLoop，注册所有可用系统并创建丰富初始世界。
    """

    def __init__(self, world):
        super().__init__(world)

        # 扩展工厂
        self.plant_factory = PlantFactory()
        self.wood_factory = WoodFactory()
        self.stone_factory = StoneFactory()
        self.metal_factory = MetalFactory()

    # -----------------------------------------------------
    # 系统初始化扩展
    # -----------------------------------------------------
    def _init_systems(self):
        """初始化所有系统：先调用父类基础系统，再注册扩展系统。"""
        super()._init_systems()
        self._init_extended_systems()

    def _init_extended_systems(self):
        """注册父类未涵盖的扩展系统"""

        # 1. 环境同步（将天气+光场状态同步到每个 EnvironmentComponent 单元格）
        self.env_sync_system = EnvironmentSyncSystem()
        self.world.add_system(self.env_sync_system)

        # 2. 资源再生（树木/果实缓慢再生）
        self.resource_regen_system = ResourceRegenerationSystem()
        self.world.add_system(self.resource_regen_system)

        # 3. 资源腐败与清理系统
        self.resource_decay_systems = [
            FoodCleanupSystem(),      # 清理已耗尽/腐败的食物实体
            FoodDecaySystem(),        # 食物新鲜度衰减
            WoodDecaySystem(),        # 木材腐朽
            StoneWeatherSystem(),     # 石头风化
            MetalOxidationSystem(),   # 金属氧化
            GarbageCleanupSystem(max_garbage=30),  # 清理垃圾实体，防止无限积累
        ]
        for system in self.resource_decay_systems:
            self.world.add_system(system)

        # 4. 人类身份系统（阵营合法性约束）
        self.identity_system = IdentitySystem()
        self.world.add_system(self.identity_system)

        # 5. 年龄增长系统
        self.age_system = AgeSystem()
        self.world.add_system(self.age_system)

    # -----------------------------------------------------
    # 初始资源创建扩展
    # -----------------------------------------------------
    def create_initial_resources(
        self,
        food_count: int = 80,
        water_count: int = 80,
        plant_count: int = 30,
        wood_count: int = 20,
        stone_count: int = 15,
        metal_count: int = 5,
    ):
        """
        创建丰富的初始资源：食物、水源、植物、木材、石头、金属。
        """
        # 先调用父类创建食物和水源
        super().create_initial_resources(food_count=food_count, water_count=water_count)

        print(f"[Init] 植物: {plant_count} 株")
        for i in range(plant_count):
            x = random.randint(5, 94)
            y = random.randint(5, 94)
            plant = self.plant_factory.create_plant(self.world, species="basic", variation=0.1)
            # 植物工厂未自动添加 SpaceComponent，手动补充以便出现在地图上
            from space.space_component import SpaceComponent
            self.world.add_component(plant, SpaceComponent(x=x, y=y))

        print(f"[Init] 木材: {wood_count} 堆")
        for i in range(wood_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            self.wood_factory.create_wood(self.world, x=x, y=y)

        print(f"[Init] 石头: {stone_count} 块")
        for i in range(stone_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            self.stone_factory.create_stone(self.world, x=x, y=y)

        print(f"[Init] 金属: {metal_count} 块")
        for i in range(metal_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            self.metal_factory.create_metal(self.world, x=x, y=y)

    # -----------------------------------------------------
    # 更新循环扩展 —— 在父类 update 基础上追加扩展系统
    # -----------------------------------------------------
    def update(self, delta_hours: float = 1.0):
        """
        执行一个时间步的更新：先调用父类完整管线，再追加扩展系统。
        """
        # 调用父类 update（已包含时间、环境、人类、生理、生物、规则、文明、资源再生）
        super().update(delta_hours)

        # 扩展系统更新（在父类之后执行，确保依赖数据已就绪）
        # 1. 环境同步（将最新天气同步到环境单元格）
        self.env_sync_system.update(self.world, delta_hours)

        # 2. 资源腐败系统
        for system in self.resource_decay_systems:
            system.update(self.world, delta_hours)

        # 3. 资源再生
        self.resource_regen_system.update(self.world, delta_hours)

        # 4. 身份系统
        self.identity_system.update(self.world, delta_hours)

        # 5. 年龄增长系统
        self.age_system.update(self.world, delta_hours)

    # -----------------------------------------------------
    # 统计信息扩展
    # -----------------------------------------------------
    def get_stats(self) -> dict:
        """获取当前统计信息（扩展版）"""
        stats = super().get_stats()

        # 使用 get_components() 避免 O(E) 全量遍历
        plant_count = sum(1 for _ in self.world.get_components(GenomeComponent))
        wood_count = sum(1 for _ in self.world.get_components(WoodComponent))
        stone_count = sum(1 for _ in self.world.get_components(StoneComponent))
        metal_count = sum(1 for _ in self.world.get_components(MetalComponent))
        env_cell_count = sum(1 for _ in self.world.get_components(EnvironmentComponent))

        stats.update({
            'plant_count': plant_count,
            'wood_count': wood_count,
            'stone_count': stone_count,
            'metal_count': metal_count,
            'env_cell_count': env_cell_count,
        })
        return stats

    def run_simulation(self, steps: int = 300, delta_hours: float = 1.0,
                       verbose: bool = True, show_panel: bool = False,
                       panel_interval: int = 50):
        """
        运行全面模拟（扩展版输出格式）。
        """
        print(f"[Run] 全面模拟: {steps} 步 × {delta_hours}h")

        for step in range(steps):
            if verbose and step % 50 == 0:
                stats = self.get_stats()
                print(
                    f"  Step {step:>4}/{steps} | "
                    f"实体:{stats['total_entities']:>3} "
                    f"人口:{stats['human_count']:>2} "
                    f"食物:{stats['food_count']:>2} "
                    f"水源:{stats['water_count']:>2} "
                    f"植物:{stats['plant_count']:>2} "
                    f"木材:{stats['wood_count']:>2} "
                    f"石头:{stats['stone_count']:>2} "
                    f"金属:{stats['metal_count']:>2} "
                    f"{stats['steps_per_second']:>6.1f}步/s"
                )

            if show_panel and step % panel_interval == 0 and step > 0:
                self.human_panel.print_panel(self.world, step)

            self.update(delta_hours)

        final_stats = self.get_stats()
        print(
            f"[Done] 实体:{final_stats['total_entities']} "
            f"人口:{final_stats['human_count']} "
            f"食物:{final_stats['food_count']} "
            f"水源:{final_stats['water_count']} "
            f"植物:{final_stats['plant_count']} "
            f"木材:{final_stats['wood_count']} "
            f"石头:{final_stats['stone_count']} "
            f"金属:{final_stats['metal_count']} "
            f"文明:{final_stats['civilization_stage']} "
            f"{final_stats['steps_per_second']:.0f}步/s"
        )


def main():
    """全面模拟主函数"""
    print("=== ECS 全面世界模拟 ===")

    world = World()
    simulation = FullSimulationLoop(world)
    simulation.create_initial_resources(
        food_count=80,
        water_count=80,
        plant_count=30,
        wood_count=20,
        stone_count=15,
        metal_count=5,
    )
    simulation.create_initial_population(human_count=10)
    simulation.run_simulation(steps=300, delta_hours=1.0, verbose=True)


if __name__ == "__main__":
    from core.world import World
    main()
