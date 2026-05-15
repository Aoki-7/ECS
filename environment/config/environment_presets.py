






"""
不同区域的环境模板
"""

from environment.config.environment_profile import EnvironmentProfile


FOREST = EnvironmentProfile(
    avg_temp=18,
    rainfall_yearly=1200,
    humidity_avg=0.8,
    wind_speed=1.5,
    soil_moisture=0.7,
    soil_nutrients=0.8
)


DESERT = EnvironmentProfile(
    avg_temp=30,
    rainfall_yearly=100,
    humidity_avg=0.2,
    wind_speed=4,
    soil_moisture=0.1,
    soil_nutrients=0.2
)


PLAINS = EnvironmentProfile(
    avg_temp=22,
    rainfall_yearly=600,
    humidity_avg=0.5,
    wind_speed=3
)