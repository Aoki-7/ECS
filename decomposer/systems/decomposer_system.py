#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
微生物分解系统

将尸体实体（CorpseComponent）分解为土壤养分，完成生态闭环：
    尸体 → 氮/磷/钾/有机质 → 土壤 → 植物吸收 → 生长

与 CorpseSystem 的关系：
    - CorpseSystem 负责推进 decay_progress（受温度影响）
    - DecomposerSystem 负责根据 decay_progress 释放养分到土壤
    - 两者协同工作：CorpseSystem "腐败"，DecomposerSystem "分解"

增强（拆分后）：
    - 引入 DecompositionComponent，记录逐尸体的剩余养分和微生物活性
    - 养分释放从"固定比例"改为"剩余养分池"模型，更真实
    - 支持温度/湿度因子动态调节分解速率
"""

import logging

from core.system import System
from core.world import World

from biology.lifecycle.corpse.components.corpse_component import CorpseComponent
from space.space_component import SpaceComponent
from environment.soil.components.soil_component import SoilComponent

from decomposer.components.decomposition_component import DecompositionComponent
from identity.category_component import CategoryComponent
from identity.category import EntityCategory
from identity.subcategory import CorpseSubCategory

logger = logging.getLogger(__name__)


class DecomposerSystem(System):
    tick_interval = 10
    """
    微生物分解系统

    职责：
        1. 扫描所有尸体实体（CorpseComponent）
        2. 为缺少 DecompositionComponent 的尸体自动挂载分解状态
        3. 根据腐败进度（decay_progress）和微生物活性从剩余养分池释放养分
        4. 查找尸体所在位置的土壤并写入养分
        5. 腐败完全后（decay_progress >= 1.0 或养分耗尽）销毁尸体实体
    """

    # 基础微生物活性基准值
    BASE_MICROBIAL_ACTIVITY = 0.5

    # 尸体养分已由硬编码改为从尸体形态/能量动态推导：
    #   - 氮/磷/钾含量 = f(体重, 能量上限, 原始类型)
    #   - 植物：N=体重×0.5, P=体重×0.2, K=体重×0.3
    #   - 动物/人类：N=体重×0.8, P=体重×0.3, K=体重×0.5
    #   - 有机质 = 能量上限 × 0.1
    # 这样小老鼠（体重0.1）和大象（体重50）的养分差异自然体现

    def __init__(self):
        super().__init__()
        self._soil_cache: dict = {}

    def update(self, world: World, dt: float = 1.0) -> None:
        """执行分解更新"""
        self._build_soil_cache(world)

        for entity, (corpse, space) in list(
            world.get_components(CorpseComponent, SpaceComponent)
        ):
            if not world.has_entity(entity):
                continue
            self._process_decomposition(world, entity, corpse, space)

    def _process_decomposition(self, world, entity, corpse, space) -> None:
        """处理单个尸体的分解"""
        # 确保尸体挂载 DecompositionComponent
        decomp = world.get_component(entity, DecompositionComponent)
        if decomp is None:
            decomp = self._init_decomposition(corpse, world, entity)
            world.add_component(entity, decomp)

        # 确保尸体有 CategoryComponent
        self._ensure_category(world, entity, corpse)

        # 查找尸体所在位置的土壤
        soil = self._get_soil_at(space)
        if soil is None:
            return

        # 根据环境更新微生物活性
        self._update_microbial_activity(decomp, soil)

        # 计算并释放养分
        release = self._compute_release(decomp, corpse)
        self._apply_release_to_soil(soil, release)
        decomp.total_released += sum(release.values())

        # 检查是否完全分解
        if self._is_fully_decomposed(corpse, decomp):
            world.remove_entity(entity)
            logger.debug(
                f"[Decomposer] 尸体 E{corpse.original_entity_id}({corpse.original_type}) "
                f"完全分解，累计释放养分 {decomp.total_released:.2f} "
                f"到土壤 ({int(space.x)}, {int(space.y)})"
            )

    def _ensure_category(self, world, entity, corpse) -> None:
        """确保尸体有 CategoryComponent"""
        cat = world.get_component(entity, CategoryComponent)
        if cat is not None:
            return
        corpse_subtype = CorpseSubCategory.UNKNOWN
        if corpse.original_type == "human":
            corpse_subtype = CorpseSubCategory.HUMAN
        elif corpse.original_type == "animal":
            corpse_subtype = CorpseSubCategory.ANIMAL
        elif corpse.original_type == "plant":
            corpse_subtype = CorpseSubCategory.PLANT
        world.add_component(entity, CategoryComponent(
            category=EntityCategory.CORPSE,
            subcategory=corpse_subtype,
        ))

    def _apply_release_to_soil(self, soil, release: dict) -> None:
        """将释放的养分应用到土壤"""
        soil.nitrogen += release["nitrogen"]
        soil.phosphorus += release["phosphorus"]
        soil.potassium += release["potassium"]
        soil.organic_matter += release["organic_matter"]

    def _is_fully_decomposed(self, corpse, decomp) -> bool:
        """检查尸体是否完全分解"""
        fully_decomposed = corpse.decay_progress >= 1.0
        nutrients_depleted = (
            decomp.remaining_nitrogen < 0.01
            and decomp.remaining_phosphorus < 0.01
            and decomp.remaining_potassium < 0.01
            and decomp.remaining_organic_matter < 0.01
        )
        return fully_decomposed or nutrients_depleted

    # -------------------------------------------------
    # 分解初始化
    # -------------------------------------------------

    def _init_decomposition(
        self, corpse: CorpseComponent, world: World, entity
    ) -> DecompositionComponent:
        """
        根据尸体的形态和能量动态推导养分含量。

        推导规则：
            - 体重来自 MorphologyComponent.weight
            - 能量上限来自 EnergyComponent.max_energy
            - 植物 vs 动物/人类使用不同的养分密度系数
        """
        from biology.lifecycle.components.morphology_component import MorphologyComponent
        from biology.lifecycle.components.energy_component import EnergyComponent

        morph = world.get_component(entity, MorphologyComponent)
        energy = world.get_component(entity, EnergyComponent)

        weight = morph.weight if morph else 10.0
        max_energy = energy.max_energy if energy else 100.0

        # 根据原始类型选择养分密度系数
        is_plant = corpse.original_type == "plant"
        n_density = 0.5 if is_plant else 0.8
        p_density = 0.2 if is_plant else 0.3
        k_density = 0.3 if is_plant else 0.5

        # 有机质与能量储备成正比
        organic = max_energy * 0.05

        return DecompositionComponent(
            remaining_nitrogen=weight * n_density,
            remaining_phosphorus=weight * p_density,
            remaining_potassium=weight * k_density,
            remaining_organic_matter=organic,
            microbial_activity=0.5,
            rate_multiplier=1.0,
            total_released=0.0,
        )

    # -------------------------------------------------
    # 释放计算
    # -------------------------------------------------

    def _compute_release(self, decomp: DecompositionComponent, corpse: CorpseComponent) -> dict:
        """计算本次 tick 释放的养分量"""
        # 释放比例 = 腐败速率 × 微生物活性 × 速率倍率
        # 使用 min 保证即使 decay_rate 较大也不会一次释放过多
        factor = min(
            corpse.decay_rate * decomp.microbial_activity * decomp.rate_multiplier,
            1.0,
        )

        release = {
            "nitrogen": decomp.remaining_nitrogen * factor,
            "phosphorus": decomp.remaining_phosphorus * factor,
            "potassium": decomp.remaining_potassium * factor,
            "organic_matter": decomp.remaining_organic_matter * factor,
        }

        # 从剩余养分池扣除
        decomp.remaining_nitrogen -= release["nitrogen"]
        decomp.remaining_phosphorus -= release["phosphorus"]
        decomp.remaining_potassium -= release["potassium"]
        decomp.remaining_organic_matter -= release["organic_matter"]

        # 防止浮点负数
        for key in ("nitrogen", "phosphorus", "potassium", "organic_matter"):
            remaining_attr = f"remaining_{key}"
            if getattr(decomp, remaining_attr) < 0:
                setattr(decomp, remaining_attr, 0.0)

        return release

    # -------------------------------------------------
    # 环境因子
    # -------------------------------------------------

    def _update_microbial_activity(self, decomp: DecompositionComponent, soil: SoilComponent):
        """根据土壤温度/湿度更新微生物活性"""
        # 温度因子：微生物最适温度约 25-35°C，偏离时活性下降
        temp = getattr(soil, "temperature", 25.0)
        temp_factor = 1.0 - abs(temp - 30.0) / 50.0
        temp_factor = max(0.1, min(1.0, temp_factor))

        # 湿度因子：微生物需要适度湿度
        moisture = getattr(soil, "moisture", 0.5)
        moisture_factor = 1.0 - abs(moisture - 0.6) / 0.6
        moisture_factor = max(0.1, min(1.0, moisture_factor))

        decomp.microbial_activity = self.BASE_MICROBIAL_ACTIVITY * temp_factor * moisture_factor
        decomp.rate_multiplier = temp_factor * moisture_factor

    # -------------------------------------------------
    # 土壤缓存
    # -------------------------------------------------

    def _build_soil_cache(self, world: World):
        """建立网格坐标 -> SoilComponent 的映射"""
        self._soil_cache = {}
        for _, (soil, space) in world.get_components(SoilComponent, SpaceComponent):
            gx = int(space.x) // 10
            gy = int(space.y) // 10
            self._soil_cache[(gx, gy)] = soil

    def _get_soil_at(self, space: SpaceComponent):
        """获取尸体坐标对应的土壤组件"""
        gx = int(space.x) // 10
        gy = int(space.y) // 10
        return self._soil_cache.get((gx, gy))
