from identity.name_component import NameComponent
from resource.food.components.food_component import FoodComponent
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent

from core.world import World

class FoodFactory:
    """食物工厂类"""
    
    @staticmethod
    def create_food(world: World, x, y, food_type="berry", amount=30.0):
        entity = world.create_entity()
        
        space = SpaceComponent(x=x, y=y)
        world.add_component(entity, space)
        # SpaceComponent自动注册到SpaceSystem（在World.add_component中处理）

        name = f"{food_type.capitalize()}"
        world.add_component(entity, NameComponent(name=name, category="food"))
        world.add_component(entity, FoodComponent(amount=amount))
        world.add_component(entity, ResourceComponent(resource_type="food", amount=amount))

        return entity
