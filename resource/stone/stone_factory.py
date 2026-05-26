from identity.name_component import NameComponent
from resource.stone.components.stone_component import StoneComponent
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from core.world import World

class StoneFactory:
    """石头工厂类"""
    
    @staticmethod
    def create_stone(world: World, x, y):
        entity = world.create_entity()
        
        space = SpaceComponent(x=x, y=y)
        world.add_component(entity, space)
        space_system = world.get_system(SpaceSystem)
        if space_system:
            space_system.add_entity(entity.id, space)

        world.add_component(entity, NameComponent(name="石头", category="stone"))
        world.add_component(entity, StoneComponent())
        world.add_component(entity, ResourceComponent(resource_type="stone", amount=1.0))

        return entity