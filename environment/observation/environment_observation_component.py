

from core.component import Component
from dataclasses import dataclass, field

@dataclass
class EnvironmentObservationComponent(Component):

    history: list = field(default_factory=list)
    max_history: int = 1000  # 历史记录上限