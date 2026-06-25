from core.system import System
from core.world import World
from core.constants import DEFAULT_MAX_AMOUNT
from resource.components.resource_component import ResourceComponent

class ResourceRegenerationSystem(System):
    tick_interval = 20  # 每20帧执行一次
    """
    处理资源再生的系统。
    定期再生环境中的资源。
    """

    # 资源再生速率
    REGEN_RATE = 0.1

    def update(self, world: World, dt: float):
        for entity, resource in world.query_components(ResourceComponent):
            if resource.resource_type in ["tree", "fruit"]:
                resource.amount += self.REGEN_RATE * dt  # 树木和果实随时间再生

                # 限制资源的最大值
                if resource.amount > DEFAULT_MAX_AMOUNT:
                    resource.amount = DEFAULT_MAX_AMOUNT