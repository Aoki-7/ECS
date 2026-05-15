from identity.name_component import NameComponent
from resource.metal.components.metal_component import MetalComponent
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent

from core.world import World

class MetalFactory:
    """金属工厂类"""
    
    @staticmethod
    def create_metal(world: World, x, y):
        entity = world.create_entity()
        
        space = SpaceComponent(x=x, y=y)
        world.add_component(entity, space)
        world.space_system.add_entity(entity.id, space)

        world.add_component(entity, NameComponent(name="金属", category="metal"))
        world.add_component(entity, MetalComponent())
        world.add_component(entity, ResourceComponent(resource_type="metal", amount=1.0))

        return entity