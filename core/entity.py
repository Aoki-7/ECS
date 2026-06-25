



class Entity:
    """
    轻量级 ECS Entity
    - 使用 id + generation 防止悬挂引用
    - 支持回收复用
    """

    __slots__ = ("id", "generation", "metadata")

    _next_id: int = 0
    _free_ids: list[int] = []
    _generations: list[int] = []

    # ==
    # 限制不可变对象（仅限制属性重新赋值，不限制可变对象内部修改）
    # ==

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise AttributeError("Entity is immutable")
        super().__setattr__(key, value)

    # ==
    # 创建
    # ==

    @classmethod
    def create(cls, pool=None):
        """
        创建新 Entity
        自动复用已释放 ID
        
        Args:
            pool: 可选的 EntityPool，如果提供且启用，优先从池中获取
        """
        # 尝试从实体池获取
        if pool is not None and pool.is_enabled():
            pooled = pool.acquire()
            if pooled is not None:
                return pooled
        
        if cls._free_ids:
            entity_id = cls._free_ids.pop()
        else:
            entity_id = cls._next_id
            cls._next_id += 1
            cls._generations.append(0)

        return cls(entity_id, cls._generations[entity_id])

    def __init__(self, entity_id: int, generation: int):
        self.id = entity_id
        self.generation = generation
        self.metadata: dict = {}

    # ==
    # 销毁
    # ==

    @classmethod
    def destroy(cls, entity):

        if not entity.is_alive():
            return

        cls._generations[entity.id] += 1
        cls._free_ids.append(entity.id)


    def is_alive(self):
        return (
            self.id < len(self._generations)
            and self.generation == self._generations[self.id]
        )
    # ==
    # 比较 & 哈希
    # ==

    def __eq__(self, other):
        return (
            isinstance(other, Entity)
            and self.id == other.id
            and self.generation == other.generation
        )

    def __hash__(self):
        return hash((self.id, self.generation))

    # ==
    # 调试
    # ==

    def __repr__(self):
        return f"<Entity id={self.id} gen={self.generation}>"

    # ==
    # 兼容方法（v3.9 API）
    # ==

    @property
    def _components(self):
        """兼容 v3.9 API：返回 metadata 中的组件字典"""
        if 'components' not in self.metadata:
            self.metadata['components'] = {}
        return self.metadata['components']

    def add_component(self, component_type, component=None):
        """兼容 v3.9 API：添加组件到实体
        
        注意：实际组件存储由 World 管理，此方法仅用于兼容旧代码。
        新代码应使用 world.add_component(entity, component)。
        """
        # 如果传入的是组件实例，存储在 metadata 中
        if component is not None:
            if 'components' not in self.metadata:
                self.metadata['components'] = {}
            self.metadata['components'][component_type] = component
        return self

    def get_component(self, component_type):
        """兼容 v3.9 API：获取组件"""
        if 'components' in self.metadata:
            return self.metadata['components'].get(component_type)
        return None

    def has_component(self, component_type):
        """兼容 v3.9 API：检查是否有组件"""
        if 'components' in self.metadata:
            return component_type in self.metadata['components']
        return False

    def remove_component(self, component_type):
        """兼容 v3.9 API：移除组件"""
        if 'components' in self.metadata:
            self.metadata['components'].pop(component_type, None)
        return self

    # ==
    # 序列化
    # ==

    def to_dict(self):
        return {
            "id": self.id,
            "generation": self.generation,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["generation"])