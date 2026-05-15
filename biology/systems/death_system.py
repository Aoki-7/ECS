



from biology.components.energy_component import EnergyComponent
from core.world import World
from core.system import System


class DeathSystem(System):
    """
        死亡系统
    """
    def update(self, world: World):
        """所有包含 Energy 组件的实体，如果能量小于等于 0，则移除该实体"""
        dead = []

        for entity, [energy] in world.get_components(EnergyComponent):
            if energy.value <= 0:
                dead.append(entity)

        for e in dead:
            world.remove_entity(e)