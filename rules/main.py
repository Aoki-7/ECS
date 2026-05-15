
from rules.rules_config import spoiled_food_condition, spoiled_food_transform
from rules.transformation_rule import TransformationRule
from rules.transformation_system import TransformationSystem


rules = [
    TransformationRule(
        source_component=FoodComponent,
        condition=spoiled_food_condition,
        transform=spoiled_food_transform
    )
]

transformation_system = TransformationSystem(rules)