
import logging
import traceback


from collections import defaultdict

logger = logging.getLogger(__name__)

from core.entity import Entity
from core.component import Component

# 注意：core/world.py 不再在顶层导入任何应用层模块（如 time_module, environment, world.entity）
# 以避免框架层依赖应用层。相关组件由 application 层在初始化时注入。



class World:
    """
    轻量级 ECS World
    - 统一管理 Entity
    - 统一存储 Component
    - 统一调度 System
    """

    def __init__(self):
        # id -> Entity
        self.entities: dict[int, Entity] = {}

        # {ComponentType: {entity_id -> Component}}
        self.components = defaultdict(dict)
        # 反向索引: {ComponentType: set(entity_id)} 用于加速 get_components
        self._component_entities: dict = defaultdict(set)

        self.systems = []
        self.tick_count = 0  # 世界 tick 计数，供 System 执行间隔判断

        # === 查询缓存：相同组件组合的查询结果在同一 tick 内复用 ===
        self._query_cache: dict = {}

        # === 世界实体（由 application 层注入，不由 core 自动创建）===
        self._world_entity: Entity | None = None

    # ====
    # Entity
    # ====

    def create_entity(self) -> Entity:
        entity = Entity.create()
        self.entities[entity.id] = entity
        return entity

    def remove_entity(self, entity: Entity):
        """
        删除实体及其所有组件
        """

        # 校验 generation，防止删除旧引用
        if not self.has_entity(entity):
            return  # 非法或过期 entity

        # 从 SpaceSystem 反注册
        self._unregister_entity_from_space(entity.id)

        # 移除组件
        for comp_dict in self.components.values():
            comp_dict.pop(entity.id, None)

        # 清理反向索引
        for comp_type in self._component_entities:
            self._component_entities[comp_type].discard(entity.id)

        # 移除实体
        self.entities.pop(entity.id, None)

        # 实体删除使查询缓存失效
        self._query_cache.clear()

        # 回收 id
        Entity.destroy(entity)

    def _unregister_entity_from_space(self, entity_id: int):
        """从 SpaceSystem 反注册实体（提取为独立方法，减少重复内联导入）"""
        try:
            from space.space_system import SpaceSystem
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.remove_entity(entity_id)
        except ImportError:
            logger.warning("SpaceSystem not available, skipping spatial cleanup")

    def has_entity(self, entity: Entity) -> bool:
        """检查实体是否存在且未过期"""
        current = self.entities.get(entity.id)
        return (
            current is not None
            and current.generation == entity.generation
        )

    def query_entity(self, id: int) -> Entity | None:
        """根据 id 查询实体"""
        return self.entities.get(id)
    

    def debug_print_entity(self, entity: Entity, verbose: bool = True):
        """
        打印某个实体的详细信息
        :param verbose: 是否打印组件内部字段
        """

        if not self.has_entity(entity):
            logger.debug(f"[错误] 实体 {entity.id} 不存在或已失效")
            return

        lines = [
            "=" * 50,
            f"实体ID: {entity.id}",
            f"实体代数: {entity.generation}",
        ]

        component_count = 0

        for comp_type, comp_dict in self.components.items():
            if entity.id in comp_dict:
                component_count += 1
                comp = comp_dict[entity.id]

                lines.append(f"\n组件类型: {comp_type.__name__}")

                if verbose:
                    lines.append(str(comp.to_dict()))

        if component_count == 0:
            lines.append("该实体没有任何组件")

        lines.append("=" * 50)
        logger.debug("\n".join(lines))


    def debug_print_all_entities(self):
        """
        打印当前世界中的所有实体
        """
        logger.debug("\n====== 当前世界实体列表 ======")

        for entity in self.entities.values():
            self.debug_print_entity(entity, verbose=False)

        logger.debug("====== 打印结束 ======\n")
        
    # ===================================
    # Component
    # ===================================

    def add_component(self, entity: Entity, component):
        if not self.has_entity(entity):
            raise ValueError("Entity 不存在，无法添加组件")

        comp_type = type(component)
        self.components[comp_type][entity.id] = component
        self._component_entities[comp_type].add(entity.id)

        # 自动注册 SpaceComponent 到 SpaceSystem
        self._register_component_to_space(entity.id, component)

        # 组件变更使查询缓存失效
        self._query_cache.clear()

    def _register_component_to_space(self, entity_id: int, component):
        """将 SpaceComponent 注册到 SpaceSystem（提取为独立方法）"""
        from space.space_component import SpaceComponent
        if isinstance(component, SpaceComponent):
            from space.space_system import SpaceSystem
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.add_entity(entity_id, component)

    def remove_component(self, entity: Entity, component_type):
        # 从 SpaceSystem 反注册
        self._unregister_component_from_space(entity.id, component_type)

        self.components.get(component_type, {}).pop(entity.id, None)
        self._component_entities.get(component_type, set()).discard(entity.id)

        # 组件变更使查询缓存失效
        self._query_cache.clear()

    def _unregister_component_from_space(self, entity_id: int, component_type):
        """从 SpaceSystem 反注册 SpaceComponent（提取为独立方法）"""
        from space.space_component import SpaceComponent
        if component_type is SpaceComponent or issubclass(component_type, SpaceComponent):
            from space.space_system import SpaceSystem
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.remove_entity(entity_id)

    def get_component(self, entity: Entity, component_type) -> Component | None:
        """获取实体的组件"""
        return self.components.get(component_type, {}).get(entity.id)

    def get_components(self, *component_types):
        if not component_types:
            return

        # 查询缓存命中：直接复用已计算的结果
        cache_key = component_types
        cached = self._query_cache.get(cache_key)
        if cached is not None:
            yield from cached
            return

        # 使用反向索引快速找到候选实体（取交集）
        pools = [
            self._component_entities.get(ct, set())
            for ct in component_types
        ]

        if not pools:
            return

        # 从最小的集合开始求交集，减少迭代量
        pools.sort(key=len)
        candidate_ids = set(pools[0])
        for pool in pools[1:]:
            candidate_ids &= pool
            if not candidate_ids:
                return

        result = []
        for entity_id in candidate_ids:
            entity = self.entities.get(entity_id)
            if entity is None:
                continue

            components = []
            for ct in component_types:
                comp = self.components.get(ct, {}).get(entity_id)
                if comp is None:
                    break
                components.append(comp)
            else:
                item = (entity, components)
                result.append(item)

        # 缓存完整结果（即使调用方提前 break，缓存也是完整的）
        self._query_cache[cache_key] = result
        yield from result


    def query_components(self, *component_types):
        """
        返回 (Entity, Component) 或 (Entity, [Component...])
        当只查询一个组件类型时，返回单个组件对象；
        多组件查询时，返回组件列表。
        """
        for entity, components in self.get_components(*component_types):
            if len(components) == 1:
                yield entity, components[0]
            else:
                yield entity, components

    # =====
    # 分类查询接口（基于 CategoryComponent）
    # =====

    def get_entities_by_category(self, category, subcategory=None):
        """
        按主分类（和可选的子分类）查询实体。

        Args:
            category: EntityCategory 枚举值
            subcategory: 可选的子分类枚举值

        Returns:
            生成器，产出 (Entity, CategoryComponent) 元组
        """
        from core.category_component import CategoryComponent
        for entity, comp in self.query_components(CategoryComponent):
            if comp.matches(category, subcategory):
                yield entity, comp

    def count_by_category(self, category, subcategory=None) -> int:
        """
        统计指定分类的实体数量。

        Args:
            category: EntityCategory 枚举值
            subcategory: 可选的子分类枚举值

        Returns:
            实体数量
        """
        return sum(1 for _ in self.get_entities_by_category(category, subcategory))

    # =====
    # 世界级访问接口
    # =====

    def get_time(self):
        """获取世界时间组件。返回 None 表示尚未注册 TimeComponent。"""
        if self._world_entity is None:
            return None
        from time_module.time_component import TimeComponent
        return self._world_entity.get_component(TimeComponent)

    def get_environment(self):
        """获取环境组件。返回 None 表示尚未注册 EnvironmentComponent。"""
        if self._world_entity is None:
            return None
        from environment.environment_component import EnvironmentComponent
        return self._world_entity.get_component(EnvironmentComponent)

    def get_world_entity(self) -> Entity | None:
        """获取世界实体。返回 None 表示尚未设置。"""
        return self._world_entity

    def set_world_entity(self, entity: Entity) -> None:
        """设置世界实体。由 application 层在初始化时调用。"""
        self._world_entity = entity

    def get_world_component(self, component_type) -> Component | None:
        """从世界实体上获取指定类型的组件。"""
        if self._world_entity is None:
            return None
        return self._world_entity.get_component(component_type)

        
    # ====
    # System
    # ====

    def add_system(self, system):
        """添加系统，按优先级插入到正确位置"""
        import bisect
        # 如果系统有 priority 属性，插入到正确排序位置
        if hasattr(system, 'priority'):
            priority = system.priority
            bisect.insort_left(self.systems, system, key=lambda s: getattr(s, 'priority', 0))
        else:
            self.systems.append(system)
        # 清除系统查询缓存
        self._system_cache = {}


    def update(self, dt: float):
        """
        更新所有 System（按优先级排序）
        支持 tick_interval 跳过机制，低频系统不必每帧执行。
        """
        self.tick_count += 1
        # systems 已通过 add_system() 的 bisect 保持有序，无需每帧排序
        for system in self.systems:
            # 跳过未启用的系统（兼容非System子类，如SpaceSystem）
            if getattr(system, 'enabled', True) is False:
                continue
            # 跳过非本帧执行的系统（按 tick_interval 分频，兼容无tick_interval的老系统）
            interval = getattr(system, 'tick_interval', 1)
            if interval > 1 and self.tick_count % interval != 0:
                continue

            try:
                # 低频系统 dt 缩放：当 tick_interval > 1 时，累计 dt 应反映实际间隔
                interval = getattr(system, 'tick_interval', 1)
                scaled_dt = dt * interval if interval > 1 else dt
                system.update(self, scaled_dt)
            except Exception:
                system_name = system.__class__.__name__
                tb = traceback.format_exc(limit=8)
                logger.error(
                    f"\n==\nECS System Error\nSystem: {system_name}\ndt: {dt}\n"
                    f"------------------------------\n{tb}\n==\n"
                )
                # One System failing should not prevent other Systems from running.

    def get_system(self, system_type):
        # 使用缓存避免每帧线性扫描
        if not hasattr(self, '_system_cache'):
            self._system_cache = {}
        if system_type not in self._system_cache:
            for system in self.systems:
                if isinstance(system, system_type):
                    self._system_cache[system_type] = system
                    return system
            self._system_cache[system_type] = None
            return None
        return self._system_cache[system_type]
    
    # ====
    # Search
    # ====

    def get_entities_with(self, *component_types):
        """
            获取由特定组件类型组成的实体列表
        """
        yield from (entity for entity, _ in self.get_components(*component_types))

    # ====
    # Debug
    # ====

    def entity_count(self):
        return len(self.entities)

    def component_count(self, component_type):
        return len(self.components.get(component_type, {}))

