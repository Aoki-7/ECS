"""快速测试 visualize_continuum — headless 模式初始化测试"""
import os
os.environ["MPLBACKEND"] = "Agg"  # no display needed
import sys
sys.path.insert(0, "D:\\个人助手\\workspace\\ECS")

from visualize_continuum import ContinuumVisualizer, SCENARIOS
import matplotlib
matplotlib.use("Agg")

for key in ["1", "2", "3"]:
    viz = ContinuumVisualizer(scenario_key=key, steps_per_frame=2, wind_deg=270.0)
    # 跑 10 帧
    for f in range(10):
        viz._animate(f)
    print(f"  [OK] Scenario {key}: {SCENARIOS[key][0]} — 10 frames, hour={viz.hour}")
    matplotlib.pyplot.close("all")

print("All 3 scenarios OK!")
