from identity.name_component import NameComponent
from resource.wood.components.wood_component import WoodComponent
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent
from space.space_system import SpaceSystem

from core.world import World
from core.category_component import CategoryComponent
from core.category import EntityCategory
from core.subcategory import ResourceSubCategory

class WoodFactory:
    """木材工厂类"""

    @staticmethod
    def create_wood(world: World, x, y):
        entity = world.create_entity()

        space = SpaceComponent(x=x, y=y)
        world.add_component(entity, space)
        space_system = world.get_system(SpaceSystem)
        if space_system:
            space_system.add_entity(entity.id, space)

        world.add_component(entity, NameComponent(name="木材", category="wood"))
        world.add_component(entity, WoodComponent())
        world.add_component(entity, ResourceComponent(resource_type="wood", amount=1.0))

        world.add_component(entity, CategoryComponent(
            category=EntityCategory.RESOURCE,
            subcategory=ResourceSubCategory.WOOD,
        ))

        return entity