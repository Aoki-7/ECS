#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
环境管线 — 定义系统执行顺序和 I/O 契约

【作用】
    统一编排所有环境子系统的执行顺序，保证数据流为单向 DAG。
    Pipeline 自身不创建系统，由 environment_builder 构建好传入。

【管线执行顺序（自上而下）】
  LAYER 1: 外部强迫
    1. SolarPositionSystem       Time → 太阳位置 (高度角, 方位角, 昼长)
    2. SolarRadiationSystem      太阳位置 → 大气顶辐射 (TOA)
    3. SeasonSystem              Time → 季节偏置 (温度/降雨/日照因子)
    4. ClimateSystem             Time → 气候偏移 (ENSO相位, 湿度/降雨偏置)

  LAYER 2: 大气物理
    5. PhysicalWeatherSystem     季节+气候+太阳 → 连续天气物理量
       ┃ 内部反馈:
       ┃   Temperature ──→ 饱和水汽压 ──→ 相对湿度
       ┃   RH ──→ 云量 (形成/消散)
       ┃   云量 ──→ 温度阻尼 (反馈)
       ┃   云量 + RH ──→ 降水
       ┃   降水 ──→ 绝对湿度下降
       ┃   气压梯度 ──→ 风速
       ┃   风速 ──→ 蒸发 (下一帧)
    6. AtmosphereCouplingSystem  云量+湿度+气溶胶 → 光学散射参数
    7. LightFieldSystem          TOA辐射+散射 → 地表光照 (直射/散射)

  LAYER 3: 极端事件 (覆盖层)
    8. WeatherModifierBridgeSystem  极端事件 modifier → 天气物理量叠加
    9. WeatherEventSystem           天气状态 → 极端事件创建
   10. WeatherLifetimeSystem        过期事件清理

  LAYER 4: 地表层
   11. SoilTemperatureSystem    天气温度 → 土壤温度
   12. SoilWaterBalanceSystem   天气降水 → 土壤水分
   13. SoilSystem               环境温度 → 土壤养分/pH
   14. EnvironmentSyncSystem    天气+光照 → 单元格环境 (EnvironmentComponent)

【扩展方式】
    新物理过程的接入步骤:
    1. 实现 XxxSystem, 继承 core.system.System, 定义 update(world, dt)
    2. 在 environment_builder.py 的 PIPELINE_SPEC 中找到目标 LAYER 位置
    3. 将 (XxxSystem(), "名称", "输入→输出说明") 插入对应位置
    4. 若需要新的 world-level 组件，在 build() 中 add_component
"""

from typing import List, Tuple, Dict, Any, Optional

from core.system import System
from core.world import World

# Pipeline 条目: (系统实例, 系统名称, I/O 说明)
PipelineEntry = Tuple[System, str, str]


class EnvironmentPipeline(System):
    """
    环境管线 — 编排执行的权威来源

    用法:
        pipeline = EnvironmentPipeline(pipeline_spec)
        pipeline.update(world, delta_hours)
        pipeline.report()   # 打印管线结构
    """

    def __init__(self, entries: List[PipelineEntry]):
        """
        Args:
            entries: [(system_instance, "name", "I/O description"), ...]
                     顺序即执行顺序，由 builder 决定。
        """
        super().__init__()
        self._entries = entries
        # 缓存：按 tick_interval 分组，避免每帧全量遍历
        self._grouped_entries: Dict[int, List[PipelineEntry]] = {}
        self._rebuild_groups()

    def _rebuild_groups(self) -> None:
        """按 tick_interval 分组缓存"""
        self._grouped_entries.clear()
        for entry in self._entries:
            system = entry[0]
            interval = getattr(system, 'tick_interval', 1)
            self._grouped_entries.setdefault(interval, []).append(entry)

    def update(self, world: World, delta_hours: float):
        """按管线顺序执行所有系统，带异常捕获和缓存优化"""
        tick = world.tick_count if hasattr(world, 'tick_count') else 0
        
        for interval, entries in self._grouped_entries.items():
            # 只有满足 tick_interval 的系统才执行
            if tick % interval != 0:
                continue
            
            for system, name, _ in entries:
                try:
                    system.update(world, delta_hours)
                except Exception as e:
                    # 防御：捕获子系统异常，避免一个系统失败导致整个管线中断
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"[EnvironmentPipeline] 系统 {name} 执行失败: {e}")

    def __len__(self) -> int:
        return len(self._entries)

    def report(self) -> str:
        """返回管线结构报告"""
        lines = ["=" * 70, "Environment Pipeline Report", "=" * 70]
        for i, (_, name, desc) in enumerate(self._entries):
            lines.append(f"  [{i:2d}] {name:30s}  ← {desc}")
        lines.append(f"\nTotal: {len(self._entries)} systems")
        return "\n".join(lines)
