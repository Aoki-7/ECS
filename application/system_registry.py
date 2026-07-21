#!/usr/bin/env python3
"""
系统注册中心

负责所有 ECS 系统的导入、分组和注册到 World。
将系统初始化逻辑从 SimulationLoop 中剥离。
"""

import os
import re
import importlib
import inspect
import logging
from typing import List, Dict, Any

from core.system import System
from core.world import World
from config.system_priorities import SystemPriority

logger = logging.getLogger(__name__)

# 自动扫描规则：(relative_dir, group, default_priority)
# 按此顺序注册，确保同优先级内顺序可预测
_SCAN_PACKAGES = [
    # 环境层（不含手动注册的 env_pipeline / pathfinding）
    ("environment/systems", "environment", SystemPriority.ENVIRONMENT),
    ("environment/astronomy", "environment", SystemPriority.ATMOSPHERE),
    ("environment/atmosphere", "environment", SystemPriority.ATMOSPHERE),
    ("environment/hydrology", "environment", SystemPriority.ENVIRONMENT),
    # ("environment/hydrology/systems", "environment", SystemPriority.ENVIRONMENT),  # 临时注释，新系统待修复
    ("environment/geology", "environment", SystemPriority.ENVIRONMENT),
    ("environment/pollution", "environment", SystemPriority.ENVIRONMENT),
    ("environment/ocean", "environment", SystemPriority.ENVIRONMENT),
    ("environment/extreme_weather", "environment", SystemPriority.ENVIRONMENT),
    ("environment/phenology", "environment", SystemPriority.ENVIRONMENT),
    ("environment/light_field", "environment", SystemPriority.ENVIRONMENT),
    ("environment/continuum/systems", "environment", SystemPriority.ENVIRONMENT),
    ("environment/soil/systems", "ecology", SystemPriority.BIOLOGY),
    ("human/systems/environment", "environment", SystemPriority.WEATHER_EFFECT),
    ("space", "environment", SystemPriority.COLLISION),
    # 人类层
    ("human/systems/cognitive", "human", SystemPriority.HUMAN_COGNITIVE),
    ("human/systems/action", "human", SystemPriority.HUMAN_COGNITIVE),
    ("human/systems/social", "human", SystemPriority.HUMAN_COGNITIVE),
    ("human/systems/core", "human", SystemPriority.HUMAN_COGNITIVE),
    ("human/systems/combat", "human", SystemPriority.HUMAN_COGNITIVE),
    ("human/systems/interaction", "human", SystemPriority.HUMAN_COGNITIVE),
    ("human/systems/physiological", "human", SystemPriority.PHYSIOLOGY),
    ("human/rl", "human", SystemPriority.HUMAN_COGNITIVE),  # RL意图系统
    # 动物层
    ("animal/systems", "animal", SystemPriority.ANIMAL_NEEDS),
    ("animal/migration/systems", "animal", SystemPriority.ANIMAL_MIGRATION),
    # 植物层
    ("plant/systems", "plant", SystemPriority.PLANT_GROWTH),
    # 生物层
    ("biology/systems", "biology", SystemPriority.BIOLOGY),
    ("biology/lifecycle", "biology", SystemPriority.BIOLOGY),
    ("biology/lifecycle/death/systems", "biology", SystemPriority.BIOLOGY),
    ("biology/lifecycle/corpse/systems", "biology", SystemPriority.BIOLOGY),
    ("biology/ecology", "ecology", SystemPriority.COMPETITION),
    # 分解者
    ("decomposer/systems", "ecology", SystemPriority.BIOLOGY),
    # 资源层
    ("resource/ore/systems", "resource", SystemPriority.BIOLOGY),
    # 文明层
    ("civilization/systems", "civilization", SystemPriority.CIVILIZATION),
    ("civilization/tools/systems", "civilization", SystemPriority.CIVILIZATION),
    ("civilization/settlement/systems", "civilization", SystemPriority.CIVILIZATION),
]


class SystemRegistry:
    """
    系统注册中心

    职责：
        1. 按层级分组管理系统
        2. 自动导入和注册系统
        3. 支持优先级配置
        4. 提供系统查询接口
    """

    def __init__(self, world: World):
        self.world = world
        self._systems: Dict[str, Any] = {}
        self._seen_classes: set[type] = set()
        self._groups: Dict[str, List[Any]] = {
            'infrastructure': [],
            'environment': [],
            'human': [],
            'animal': [],
            'plant': [],
            'biology': [],
            'ecology': [],
            'civilization': [],
            'v35_v36': [],
        }

    # === 注册 ===

    def register(self, name: str, system: Any, group: str = 'default', priority: int = None) -> None:
        """注册单个系统；同一 System 类仅注册一次，保留首次实例"""
        system_class = type(system)
        if system_class in self._seen_classes:
            logger.debug(f"[SystemRegistry] 跳过重复注册 {system_class.__name__}（name={name}）")
            return

        self._seen_classes.add(system_class)
        if priority is not None:
            system.priority = priority
        self.world.add_system(system)
        self._systems[name] = system
        if group in self._groups:
            self._groups[group].append(system)
        logger.debug(f"[SystemRegistry] 注册 {name} -> {group}")

    def get(self, name: str) -> Any:
        """获取已注册的系统"""
        return self._systems.get(name)

    def get_group(self, group: str) -> List[Any]:
        """获取某组的所有系统"""
        return self._groups.get(group, [])

    # === 批量初始化 ===

    def init_all(self) -> None:
        """初始化所有系统（按优先级排序）"""
        # 基础设施层（手动注册，特殊系统）
        self._init_infrastructure()
        # 环境层（手动 + 自动扫描）
        self._init_environment()
        # 其余层级通过自动扫描注册
        self._auto_scan_all()
        # 根据配置启用RL意图系统
        self._init_rl_intent_system()

    def _init_rl_intent_system(self) -> None:
        """根据配置启用RL意图系统"""
        from core.components.world_config_component import WorldConfigComponent
        config = self.world.get_world_component(WorldConfigComponent)
        if config and config.use_rl_intent:
            # 禁用规则驱动的意图系统
            from human.systems.core.intent_system import IntentSystem
            intent_system = self.get('intent')
            if intent_system:
                self.world.remove_system(intent_system)
                logger.info("禁用规则驱动的意图系统")

            # 注册RL意图系统
            from human.rl.rl_intent_system import RLIntentSystem
            rl_system = RLIntentSystem(training=config.rl_training)
            self.register('rl_intent', rl_system, 'human', SystemPriority.HUMAN_COGNITIVE)
            logger.info(f"启用RL驱动的意图系统，训练模式: {config.rl_training}")

    # === 手动注册层（特殊系统） ===

    def _init_infrastructure(self) -> None:
        """基础设施：存档、时间、事件日志"""
        from save_load.systems.save_load_system import SaveLoadSystem
        from time_module.time_system import TimeSystem
        from identity.event_log_system import EventLogSystem

        self.register('save_load', SaveLoadSystem(), 'infrastructure', SystemPriority.TIME)
        self.register('time', TimeSystem(), 'infrastructure', SystemPriority.TIME)
        self.register('event_log', EventLogSystem(), 'infrastructure', SystemPriority.EVENT_LOG)

    def _init_environment(self) -> None:
        """环境层：环境管线、天气效果、碰撞检测、路径规划"""
        from environment.config.environment_builder import EnvironmentBuilder
        from human.systems.navigation.pathfinding_system import PathfindingSystem
        from space.collision_system import CollisionSystem

        # 环境管线（特殊构造参数）
        env_pipeline = EnvironmentBuilder.build(self.world)
        self.register('env_pipeline', env_pipeline, 'environment', SystemPriority.ENVIRONMENT)

        # 路径规划
        self.register('pathfinding', PathfindingSystem(), 'environment', SystemPriority.PATHFINDING)
        # 碰撞检测
        self.register('collision', CollisionSystem(auto_resolve=True), 'environment', SystemPriority.COLLISION)

        # 天气效果系统（特殊命名前缀）
        from human.systems.environment.heat_effect_system import HeatEffectSystem
        from human.systems.environment.cold_effect_system import ColdEffectSystem
        from human.systems.environment.rain_effect_system import RainEffectSystem
        from human.systems.environment.wind_effect_system import WindEffectSystem
        from human.systems.environment.humidity_effect_system import HumidityEffectSystem

        for cls in [HeatEffectSystem, ColdEffectSystem, RainEffectSystem, WindEffectSystem, HumidityEffectSystem]:
            name = cls.__name__.replace('EffectSystem', '').lower()
            self.register(f'weather_{name}', cls(), 'environment', SystemPriority.WEATHER_EFFECT)

    # === 自动扫描层 ===

    def _auto_scan_all(self) -> None:
        """按规则自动扫描并注册所有系统"""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        for relative_dir, group, default_priority in _SCAN_PACKAGES:
            self._scan_dir(project_root, relative_dir, group, default_priority)

    def _scan_dir(self, project_root: str, relative_dir: str, group: str, default_priority: int) -> None:
        """扫描目录下的 *_system.py 模块并注册"""
        target_dir = os.path.join(project_root, relative_dir)
        if not os.path.isdir(target_dir):
            return

        for root, _, files in os.walk(target_dir):
            for fname in sorted(files):
                if not fname.endswith('_system.py') or fname.startswith('test'):
                    continue

                rel_path = os.path.relpath(os.path.join(root, fname), project_root)
                module_name = rel_path.replace(os.sep, '.')[:-3]  # remove .py

                try:
                    module = importlib.import_module(module_name)
                except Exception as e:
                    logger.warning(f"[SystemRegistry] 无法导入 {module_name}: {e}")
                    continue

                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(cls, System) or cls is System:
                        continue
                    # 只注册在本模块中定义的类，避免导入的依赖类被重复注册
                    if cls.__module__ != module.__name__:
                        continue

                    reg_name = self._to_snake_case(name).replace('_system', '')
                    if not reg_name:
                        reg_name = fname.replace('_system.py', '')

                    priority = getattr(cls, 'priority', None)
                    if priority is None:
                        priority = getattr(module, '__priority__', default_priority)

                    self.register(reg_name, cls(), group, priority)

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """CamelCase -> snake_case"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
