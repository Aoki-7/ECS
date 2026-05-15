from core.system import System
from resource.components.resource_component import ResourceComponent

class ResourceRegenerationSystem(System):
    """
    处理资源再生的系统。
    定期再生环境中的资源。
    """

    def update(self, world, dt):
        for entity, resource in world.query_components(ResourceComponent):
            if resource.resource_type in ["tree", "fruit"]:
                resource.amount += 0.1 * dt  # 树木和果实随时间再生

                # 限制资源的最大值
                if resource.amount > 100.0:
                    resource.amount = 100.0