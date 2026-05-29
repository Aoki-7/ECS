from core.system import System
from biology.components.injury.injury_component import InjuryComponent
from biology.components.health_component import HealthComponent

class InjurySystem(System):
    """
    处理受伤状态的系统。
    根据受伤的严重程度减少健康值。
    """

    def update(self, world, dt):
        for entity, (injury, health) in world.query_components(InjuryComponent, HealthComponent):
            total_severity = injury.get_total_severity()
            health.health -= total_severity * dt  # 根据严重程度减少健康值

            # 如果健康值降到0，标记实体为死亡
            if health.health <= 0:
                world.mark_entity_as_dead(entity)