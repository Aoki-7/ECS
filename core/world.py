
import traceback


from collections import defaultdict
import bisect
from core.entity import Entity
from core.component import Component

from world.world_entity import WorldEntity
from time_module.time_component import TimeComponent
from environment.environment_component import EnvironmentComponent

from space.space_system import SpaceSystem



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

        self.systems = []

        # === 创建唯一世界实体 ===
        self._world_entity = WorldEntity()
        # === 强制初始化核心组件 ===
        self._world_entity.add_component(TimeComponent())

        # === 通过标准接口添加空间系统 ===
        space_system = SpaceSystem()
        self.add_system(space_system)

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

        # 从SpaceSystem反注册
        space_system = self.get_system(SpaceSystem)
        if space_system:
            space_system.remove_entity(entity.id)

        # 移除组件
        for comp_dict in self.components.values():
            comp_dict.pop(entity.id, None)

        # 移除实体
        self.entities.pop(entity.id, None)

        # 回收 id
        Entity.destroy(entity)

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
            print(f"[错误] 实体 {entity.id} 不存在或已失效")
            return

        print("=" * 50)
        print(f"实体ID: {entity.id}")
        print(f"实体代数: {entity.generation}")

        component_count = 0

        for comp_type, comp_dict in self.components.items():
            if entity.id in comp_dict:
                component_count += 1
                comp = comp_dict[entity.id]

                print(f"\n组件类型: {comp_type.__name__}")

                if verbose:
                    print(comp.to_dict())
                    # for attr, value in vars(comp).items():
                    #     print(f"  - {attr}: {value}")

        if component_count == 0:
            print("该实体没有任何组件")

        print("=" * 50)


    def debug_print_all_entities(self):
        """
        打印当前世界中的所有实体
        """
        print("\n====== 当前世界实体列表 ======")

        for entity in self.entities.values():
            self.debug_print_entity(entity, verbose=False)

        print("====== 打印结束 ======\n")
        
    # ====
    # Component
    # ====

    def add_component(self, entity: Entity, component):
        if not self.has_entity(entity):
            raise ValueError("Entity 不存在，无法添加组件")

        self.components[type(component)][entity.id] = component

        # 自动注册SpaceComponent到SpaceSystem
        from space.space_component import SpaceComponent
        if isinstance(component, SpaceComponent):
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.add_entity(entity.id, component)

    def remove_component(self, entity: Entity, component_type):
        # 从SpaceSystem反注册
        from space.space_component import SpaceComponent
        if component_type is SpaceComponent or issubclass(component_type, SpaceComponent):
            space_system = self.get_system(SpaceSystem)
            if space_system:
                space_system.remove_entity(entity.id)

        self.components.get(component_type, {}).pop(entity.id, None)

    def get_component(self, entity: Entity, component_type) -> Component | None:
        """获取实体的组件"""
        return self.components.get(component_type, {}).get(entity.id)

    def get_components(self, *component_types):
        if not component_types:
            return

        pools = [
            self.components.get(ct, {})
            for ct in component_types
        ]

        smallest_pool = min(pools, key=len) if pools else {}

        visited = set()

        # 普通 entity
        for entity_id in list(smallest_pool.keys()):
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
                visited.add(entity_id)
                yield entity, components


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
    # 世界级访问接口
    # =====

    def get_time(self) -> TimeComponent:
        return self._world_entity.get_component(TimeComponent)

    def get_environment(self) -> EnvironmentComponent:
        return self._world_entity.get_component(EnvironmentComponent)

    def get_world_entity(self) -> WorldEntity:
        return self._world_entity

    def get_world_component(self, component_type) -> Component:
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

    def update(self, dt: float):
        """
        更新所有 System（按优先级排序）
        使用 copy 防止系统内部删除实体导致迭代异常
        """
        # 按 priority 排序，数字越小越先执行
        sorted_systems = sorted(self.systems, key=lambda s: getattr(s, 'priority', 0))

        for system in sorted_systems:

            try:

                system.update(self, dt)

            except Exception as e:

                system_name = system.__class__.__name__

                print("\n==")
                print("ECS System Error")
                print("System:", system_name)
                print("dt:", dt)
                print("------------------------------")
                traceback.print_exc()
                print("==\n")

                raise

    def get_system(self, system_type):
        for system in self.systems:
            if isinstance(system, system_type):
                return system
            
    # ====
    # Search
    # ====

    def get_entities_with(self, *component_types):
        """
            获取由特定组件类型组成的实体列表
        """
        return [
            entity
            for entity, _ in self.get_components(*component_types)
        ]

    # ====
    # Debug
    # ====

    def entity_count(self):
        return len(self.entities)

    def component_count(self, component_type):
        return len(self.components.get(component_type, {}))

