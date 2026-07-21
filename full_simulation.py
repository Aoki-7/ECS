#!/usr/bin/env python3
"""
ECS 世界模拟引擎 — 全面模拟入口模块 (Full Simulation)

职责：
    - 扩展自 application/SimulationLoop，注册所有可用子系统
    - 整合完整的环境管线（天气、季节、气候、大气、光照、连续体同步）
    - 整合资源腐败与再生（食物腐败、木材腐朽、石头风化、金属氧化）
    - 整合完整人类管线（生理、认知、社交、生存、身份、年龄）
    - 整合生物系统（基因表达、植物生长、形态变化、死亡判定）
    - 整合文明与规则系统（科技树、建筑、贸易、技能提升）

与 main.py 的区别：
    main.py         → 轻量启动，仅注册核心系统，适合快速调试
    full_simulation.py → 全系统注册，丰富初始世界，适合完整模拟

运行方式：
    python full_simulation.py
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import random
import logging
import argparse

logger = logging.getLogger(__name__)

# =========================================================
# 复用 application 层的核心模拟循环
# =========================================================
from application.simulation_loop import SimulationLoop

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

# 文明系统（用于统计真实阶段）
from civilization.systems.civilization_system import CivilizationSystem

# 额外组件（用于统计）
from biology.components.genome_component import GenomeComponent
from resource.wood.components.wood_component import WoodComponent
from resource.stone.components.stone_component import StoneComponent
from resource.metal.components.metal_component import MetalComponent
from environment.environment_component import EnvironmentComponent
from human.components.basic.human_component import HumanComponent
from resource.food.components.food_component import FoodComponent
from resource.water.components.water_component import WaterComponent
from plant.components.plant_component import PlantComponent


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
    def init(self) -> None:
        """初始化所有系统：先调用父类基础系统，再注册扩展系统。"""
        super().init()
        self._init_extended_systems()

    def _init_extended_systems(self):
        """注册父类未涵盖的扩展系统"""

        # 1. 环境同步（将天气+光场状态同步到每个 EnvironmentComponent 单元格）
        self._env_sync_system = EnvironmentSyncSystem()
        self.world.add_system(self._env_sync_system)

        # 2. 资源再生（树木/果实缓慢再生）
        self._resource_regen_system = ResourceRegenerationSystem()
        self.world.add_system(self._resource_regen_system)

        # 3. 资源腐败与清理系统
        self._resource_decay_systems = [
            FoodCleanupSystem(),      # 清理已耗尽/腐败的食物实体
            FoodDecaySystem(),        # 食物新鲜度衰减
            WoodDecaySystem(),        # 木材腐朽
            StoneWeatherSystem(),     # 石头风化
            MetalOxidationSystem(),   # 金属氧化
            GarbageCleanupSystem(max_garbage=30),  # 清理垃圾实体，防止无限积累
        ]
        for system in self._resource_decay_systems:
            self.world.add_system(system)

        # 4. 人类身份系统（阵营合法性约束）
        self._identity_system = IdentitySystem()
        self.world.add_system(self._identity_system)

        # 5. 年龄增长系统
        self._age_system = AgeSystem()
        self.world.add_system(self._age_system)

    # 环境同步系统引用（供统计等外部访问）
    env_sync_system = property(lambda self: getattr(self, '_env_sync_system', None))

    # 资源腐败系统列表（供统计等外部访问）
    resource_decay_systems = property(lambda self: getattr(self, '_resource_decay_systems', []))

    # 资源再生系统引用（供统计等外部访问）
    resource_regen_system = property(lambda self: getattr(self, '_resource_regen_system', None))

    # 身份系统引用（供统计等外部访问）
    identity_system = property(lambda self: getattr(self, '_identity_system', None))

    # 年龄系统引用（供统计等外部访问）
    age_system = property(lambda self: getattr(self, '_age_system', None))

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

        logger.info(f"[Init] 植物: {plant_count} 株")
        for i in range(plant_count):
            x = random.randint(5, 94)
            y = random.randint(5, 94)
            plant = self.plant_factory.create_plant(self.world, species="basic", variation=0.1)
            # 植物工厂未自动添加 SpaceComponent，手动补充以便出现在地图上
            from space.space_component import SpaceComponent
            self.world.add_component(plant, SpaceComponent(x=x, y=y))

        logger.info(f"[Init] 木材: {wood_count} 堆")
        for i in range(wood_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            self.wood_factory.create_wood(self.world, x=x, y=y)

        logger.info(f"[Init] 石头: {stone_count} 块")
        for i in range(stone_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            self.stone_factory.create_stone(self.world, x=x, y=y)

        logger.info(f"[Init] 金属: {metal_count} 块")
        for i in range(metal_count):
            x = random.randint(0, 99)
            y = random.randint(0, 99)
            self.metal_factory.create_metal(self.world, x=x, y=y)

    # -----------------------------------------------------
    # 更新循环扩展 —— 在父类 update 基础上追加扩展系统
    # -----------------------------------------------------
    def update(self, delta_hours: float = 1.0):
        """
        执行一个时间步的更新：复用父类调度器，不再手动调用扩展系统。

        所有扩展系统（环境同步、资源腐败/再生、身份、年龄）均已通过
        _init_extended_systems 注册到 World 调度器，由 SystemScheduler 统一
        按 tick_interval 与优先级调度，避免重复执行与 tick_interval 失效。
        """
        super().update(delta_hours)

    # -----------------------------------------------------
    # 统计信息扩展
    # -----------------------------------------------------
    def get_stats(self) -> dict:
        """获取当前统计信息（扩展版）"""
        import time

        stats = super().get_stats()
        step = stats.get('step', 0)

        # 计算步速
        now = time.perf_counter()
        if not hasattr(self, '_stats_start_time'):
            self._stats_start_time = now
        elapsed = now - self._stats_start_time
        stats['steps_per_second'] = step / elapsed if elapsed > 0 else 0.0

        # 使用 get_components() 避免 O(E) 全量遍历
        stats['total_entities'] = len(self.world.entities)
        stats['human_count'] = sum(1 for _ in self.world.get_components(HumanComponent))
        stats['food_count'] = sum(1 for _ in self.world.get_components(FoodComponent))
        stats['water_count'] = sum(1 for _ in self.world.get_components(WaterComponent))
        stats['plant_count'] = sum(1 for _ in self.world.get_components(PlantComponent))
        stats['wood_count'] = sum(1 for _ in self.world.get_components(WoodComponent))
        stats['stone_count'] = sum(1 for _ in self.world.get_components(StoneComponent))
        stats['metal_count'] = sum(1 for _ in self.world.get_components(MetalComponent))
        stats['env_cell_count'] = sum(1 for _ in self.world.get_components(EnvironmentComponent))

        # 文明阶段：优先从 CivilizationSystem 读取实际状态
        civ_system = self.world.get_system(CivilizationSystem)
        if civ_system is not None:
            stage = getattr(civ_system, 'civilization_stage', 'hunter_gatherer')
        else:
            stage = 'hunter_gatherer'
        stage_display_map = {
            'hunter_gatherer': '狩猎采集',
            'agricultural': '农业社会',
            'bronze_age': '青铜时代',
            'iron_age': '铁器时代',
        }
        stats['civilization_stage'] = stage_display_map.get(stage, '部落')

        return stats

    def run_simulation(self, steps: int = 300, delta_hours: float = 1.0,
                       verbose: bool = True, show_panel: bool = False,
                       panel_interval: int = 50):
        """
        运行全面模拟（扩展版输出格式）。
        """
        # 确保扩展系统已初始化
        if not hasattr(self, 'env_sync_system'):
            self.init()

        logger.info(f"[Run] 全面模拟: {steps} 步 × {delta_hours}h")

        for step in range(steps):
            if verbose and step % 50 == 0:
                stats = self.get_stats()
                logger.info(
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
        logger.info(
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


def run_single_simulation(args, round_num: int = 0) -> dict:
    """运行单轮模拟，返回该轮统计结果"""
    import random
    import time
    logger.info(f"\n=== [轮次 {round_num}] 模拟开始 ===")

    world = World()
    simulation = FullSimulationLoop(world)
    simulation.init()

    # 应用时间加速倍率
    if args.time_scale != 1.0:
        from core.components.world_config_component import WorldConfigComponent
        world_config = world.get_world_component(WorldConfigComponent)
        if world_config is not None:
            world_config.time_scale = args.time_scale
            logger.info(f"[Config] 时间加速倍率: {args.time_scale}x")

    # 自适应初始配置：每轮微调参数避免完全重复
    base_food = 80 + random.randint(-10, 20)
    base_water = 80 + random.randint(-10, 20)
    base_plants = 30 + random.randint(-5, 10)
    base_humans = 10
    logger.info(f"[Config] 本轮初始配置: 食物={base_food} 水源={base_water} 植物={base_plants} 人口={base_humans}")

    simulation.create_initial_resources(
        food_count=base_food,
        water_count=base_water,
        plant_count=base_plants,
        wood_count=20 + random.randint(-3, 5),
        stone_count=15 + random.randint(-3, 5),
        metal_count=5 + random.randint(-1, 3),
    )
    simulation.create_initial_population(human_count=base_humans)

    # 运行模拟
    start_time = time.perf_counter()
    step = 0
    max_steps = args.steps
    human_count = base_humans

    while step < max_steps and human_count > 0:
        simulation.update(delta_hours=args.delta_hours)
        if step % 100 == 0 and not args.quiet:
            stats = simulation.get_stats()
            human_count = stats['human_count']
            logger.info(
                f"  Step {step:>4}/{max_steps} | "
                f"人口:{stats['human_count']:>2} "
                f"食物:{stats['food_count']:>2} "
                f"植物:{stats['plant_count']:>2} "
                f"文明:{stats['civilization_stage']}"
            )
        step += 1

    # 统计结果
    final_stats = simulation.get_stats()
    elapsed = time.perf_counter() - start_time
    result = {
        'round': round_num,
        'survived_steps': step,
        'max_steps': max_steps,
        'final_human_count': final_stats['human_count'],
        'final_food': final_stats['food_count'],
        'final_water': final_stats['water_count'],
        'final_plants': final_stats['plant_count'],
        'max_civilization_stage': final_stats['civilization_stage'],
        'elapsed_seconds': round(elapsed, 2),
        'cause_of_end': 'population_extinct' if final_stats['human_count'] == 0 else 'max_steps_reached'
    }

    logger.info(f"[轮次 {round_num}] 结束: {result['cause_of_end']}, 存活{result['survived_steps']}步, 最高文明: {result['max_civilization_stage']}")
    return result


def main():
    """全面模拟主函数"""
    parser = argparse.ArgumentParser(description="ECS 世界模拟 — 完整版")
    parser.add_argument("--steps", type=int, default=300, help="单轮最大运行步数")
    parser.add_argument("--delta-hours", type=float, default=1.0, help="每步小时数")
    parser.add_argument("--time-scale", type=float, default=10.0, help="时间加速倍率（默认10.0，1.0=实时）")
    parser.add_argument("--quiet", action="store_true", help="关闭 verbose 输出")
    parser.add_argument("--rounds", type=int, default=1, help="循环模拟轮数（默认1轮，0=无限循环）")
    args = parser.parse_args()

    logger.info("=== ECS 全面世界模拟 - 多轮循环模式 ===")
    logger.info(f"配置: 单轮最大步数={args.steps}, 循环轮数={args.rounds if args.rounds>0 else '无限'}")

    history = []
    current_round = 1
    try:
        while args.rounds == 0 or current_round <= args.rounds:
            result = run_single_simulation(args, current_round)
            history.append(result)
            current_round += 1
    except KeyboardInterrupt:
        logger.info("\n[用户中断] 模拟停止")
    finally:
        # 输出历史统计
        logger.info("\n=== 全部模拟历史统计 ===")
        logger.info(f"共运行 {len(history)} 轮")
        for res in history:
            logger.info(
                f"轮次 {res['round']:2d}: "
                f"{res['cause_of_end']:15s} | "
                f"存活步数: {res['survived_steps']:4d} | "
                f"最高文明: {res['max_civilization_stage']:6s} | "
                f"耗时: {res['elapsed_seconds']:.2f}s"
            )


if __name__ == "__main__":
    from core.world import World
    main()
