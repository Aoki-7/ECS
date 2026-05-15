

# | 来源         | 影响    |
# | ---------- | ----- |
# | Season     | 太阳高度角 |
# | Weather    | 云量遮挡  |
# | Atmosphere | 散射    |
# | Terrain    | 阴影    |
# | TimeSystem | 昼夜变化  |


# | 系统          | 用途   |
# | ----------- | ---- |
# | Vegetation  | 光合作用 |
# | Temperature | 地表加热 |
# | Evaporation | 蒸发   |
# | Agent       | 视觉   |


# environment/
#  └── light_field/
#       ├── components/
#       │     light_scatter_component.py        # 大气光散射组件
#       │     solar_position_component.py       # 太阳位置组件
#       │     solar_radiation_component.py      # 大气光散射
#       │
#       ├── system/
#       │     light_field_system.py              # 
#       │     could_system.py
#       │     pressure_system.py
#       │     convection_system.py
#       │     thermodynamics_system.py
#       │     wind_system.py