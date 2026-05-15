# ECS Simulation Enhancement Skill

## Purpose
This skill is designed to enhance and extend the ECS (Entity-Component-System) architecture by systematically identifying and filling gaps in components and systems. It ensures logical consistency and completeness within the simulation framework.

## Features
- **Component Creation**: Automatically generates missing components based on logical requirements.
- **System Creation**: Implements systems to process and update the state of components.
- **Logical Consistency**: Ensures that every component has a corresponding system to handle its logic.
- **Iterative Enhancement**: Iteratively improves the ECS framework until a logical closure is achieved.

## Workflow
1. **Analyze Existing Structure**:
   - Identify missing components and systems by analyzing the current ECS structure.

2. **Generate Missing Components**:
   - Create new components to represent missing data or states in the simulation.
   - Example: `InjuryComponent`, `EmotionComponent`, `HungerComponent`.

3. **Generate Missing Systems**:
   - Create systems to process the logic of the new components.
   - Example: `InjurySystem`, `EmotionSystem`, `HungerSystem`.

4. **Ensure Logical Closure**:
   - Verify that all components are paired with systems.
   - Ensure that systems interact logically with other systems and components.

## Example Usage
### Components
#### InjuryComponent
```python
from core.component import Component
from dataclasses import dataclass
from typing import Dict

@dataclass
class InjuryComponent(Component):
    """
    Describes the injury state of an entity.
    Includes bleeding, fractures, poisoning, etc.
    """
    injuries: Dict[str, float] = None  # Injury type and severity

    def __post_init__(self):
        if self.injuries is None:
            self.injuries = {}

    def add_injury(self, injury_type: str, severity: float):
        self.injuries[injury_type] = severity

    def heal_injury(self, injury_type: str):
        if injury_type in self.injuries:
            del self.injuries[injury_type]

    def get_total_severity(self) -> float:
        return sum(self.injuries.values())
```

### Systems
#### InjurySystem
```python
from core.system import System
from human.components.injury.injury_component import InjuryComponent
from human.components.physiological.health_component import HealthComponent

class InjurySystem(System):
    """
    Processes injury states and reduces health based on severity.
    """

    def update(self, world, dt):
        for entity, (injury, health) in world.query_components(InjuryComponent, HealthComponent):
            total_severity = injury.get_total_severity()
            health.health -= total_severity * dt

            if health.health <= 0:
                world.mark_entity_as_dead(entity)
```

## How to Use
1. Place this skill in the `.github/skills/` directory of your ECS project.
2. Invoke the skill to analyze and enhance your ECS framework.
3. The skill will iteratively add missing components and systems until the framework is logically complete.

## Limitations
- This skill assumes a Python-based ECS framework.
- It requires a well-defined directory structure for components and systems.

## Future Enhancements
- Add support for more complex interactions between systems.
- Introduce configuration files to customize the enhancement process.
- Support other programming languages and ECS frameworks.