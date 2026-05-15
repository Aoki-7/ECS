from core.system import System
from core.world import World

from human.components.physiological.physiology_needs_component import PhysiologyNeedsComponent
from human.components.physiological.health_component import HealthComponent


class HungerSystem(System):
    """
    饥饿系统
    
    处理饥饿状态的系统。随时间增加饥饿值，并在饥饿过高时减少健康值。
    
    注：该系统使用 PhysiologyNeedsComponent 管理饥饿值，而非独立的 HungerComponent。
    """

    # 饥饿增长速率（单位：hunger值/小时）
    HUNGER_INCREASE_RATE = 0.1
    
    # 饥饿对健康的影响阈值
    HEALTH_DAMAGE_THRESHOLD = 80.0
    
    # 饥饿对健康的伤害速率
    HEALTH_DAMAGE_RATE = 0.05

    def update(self, world: World, dt: float):
        """
        更新所有实体的饥饿状态
        
        Args:
            world: World实例
            dt: 时间增量（秒）
        """
        for entity, (needs, health) in world.get_components(
            PhysiologyNeedsComponent, HealthComponent
        ):
            self._update_hunger(needs, health, dt)

    def _update_hunger(self, needs: PhysiologyNeedsComponent, 
                      health: HealthComponent, dt: float):
        """
        更新单个实体的饥饿状态
        
        Args:
            needs: 生理需求组件
            health: 健康组件
            dt: 时间增量
        """
        # 随时间增加饥饿值
        needs.hunger = min(
            needs.max_hunger,
            needs.hunger + self.HUNGER_INCREASE_RATE * dt
        )
        
        # 如果饥饿值过高，减少健康值
        if needs.hunger > self.HEALTH_DAMAGE_THRESHOLD and health:
            # 饥饿越严重，造成的伤害越大
            damage = (needs.hunger - self.HEALTH_DAMAGE_THRESHOLD) * self.HEALTH_DAMAGE_RATE * dt
            health.hp = max(0, health.hp - damage)
