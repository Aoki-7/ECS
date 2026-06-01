



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
    # 限制不可变对象
    # ==

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise AttributeError("Entity is immutable")
        super().__setattr__(key, value)

    # ==
    # 创建
    # ==

    @classmethod
    def create(cls):
        """
        创建新 Entity
        自动复用已释放 ID
        """
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