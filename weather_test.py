from environment.physics_weather import (
    PhysicalWeatherComponent,
    PhysicalWeatherSystem,
    classify_from_component,
)

from core.world import World

world = World()


# 挂载组件
world.get_world_entity().add_component(PhysicalWeatherComponent())

# 创建系统（可指定纬度进行季节耦合）
weather_system = PhysicalWeatherSystem(latitude=35.0)
world.add_system(weather_system)

# 每步更新

# 获取物理量 + 推导天气
wc: PhysicalWeatherComponent = world.get_world_entity().get_component(PhysicalWeatherComponent)

for _ in range(100):
    weather_system.update(world, delta_hours=1.0)

    state = classify_from_component(wc)
    print(f"Weather: {state.label}")
    print(f"Temp: {wc.temperature:.1f}°C, Rain: {wc.precipitation_rate:.2f}mm/h")
