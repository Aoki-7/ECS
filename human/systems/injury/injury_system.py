from core.system import System
from core.world import World
from biology.components.health_status_component import HealthStatusComponent


class InjurySystem(System):
    tick_interval = 5  # 每5帧执行一次
    """
    处理受伤状态的系统。
    根据伤口严重程度减少生命值，并计算持续伤害。
    """

    def update(self, world: World, dt: float):
        for entity, (health,) in world.query_components(HealthStatusComponent):
            health: HealthStatusComponent

            # 更新伤口年龄并获取持续伤害
            dot = health.update_wounds(dt)

            # 根据伤口严重程度减少生命值
            health.hp -= (health.get_total_severity() * 0.01 + dot) * dt
            health.hp = max(0.0, health.hp)

            # 清理已愈合伤口
            health.remove_healed_wounds()