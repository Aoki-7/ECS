


from dataclasses import dataclass, asdict

@dataclass
class Component:
    """
    ECS 基础组件类
    """

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)