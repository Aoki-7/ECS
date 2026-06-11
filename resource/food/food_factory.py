from identity.name_component import NameComponent
from resource.food.components.food_component import FoodComponent
from resource.components.resource_component import ResourceComponent
from space.space_component import SpaceComponent

from core.world import World
from identity.category_component import CategoryComponent
from identity.category import EntityCategory
from identity.subcategory import FoodSubCategory

class FoodFactory:
    """食物工厂类"""

    _FOOD_TYPE_MAP = {
        "berry": FoodSubCategory.BERRY,
        "meat": FoodSubCategory.MEAT,
        "fish": FoodSubCategory.FISH,
        "grain": FoodSubCategory.GRAIN,
        "cooked": FoodSubCategory.COOKED,
        "raw": FoodSubCategory.RAW,
    }

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

        # 分类组件
        subcategory = FoodFactory._FOOD_TYPE_MAP.get(food_type, FoodSubCategory.RAW)
        world.add_component(entity, CategoryComponent(
            category=EntityCategory.FOOD,
            subcategory=subcategory,
        ))

        return entity
