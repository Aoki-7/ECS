#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
植物光合作用系统

基于 LightReceiverComponent 的实际接收光照，计算有效光合有效辐射 (PAR)，
并考虑冠层结构修正，将结果写入 PhenotypeComponent 供 GrowthSystem 使用。

与 GrowthSystem 的配合：
    GrowthSystem 优先读取 PhenotypeSystem.get(phenotype, "effective_par")，
    若不存在则回退到全局 EnvironmentComponent.par。
"""

import math

from core.system import System
from core.world import World

from environment.light_field.components.light_receiver_component import LightReceiverComponent
from biology.organisms.plant.components.canopy_component import CanopyComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.traits.trait import Trait
from biology.systems.phenotype_system import PhenotypeSystem


class PlantPhotosynthesisSystem(System):
    tick_interval = 20
    """
    植物光合作用增强系统

    职责：
        1. 读取 LightReceiverComponent 的实际接收光照
        2. 结合 CanopyComponent 计算有效 PAR
        3. 计算冠层修正后的光合速率
        4. 将 effective_par 和 photosynthesis_rate 写入 PhenotypeComponent
    """

    def update(self, world: World, dt: float = 1.0) -> None:
        """
        执行光合作用计算

        Args:
            world: World 实例
            dt: 时间步长（小时，预留）
        """
        for _, (light, canopy, pheno) in world.get_components(
            LightReceiverComponent,
            CanopyComponent,
            PhenotypeComponent,
        ):  
            # 有效 PAR = 接收到的总光照 × (1 - 遮光率)
            effective_par = light.received_total * (1.0 - light.shade_ratio)

            # 冠层光合效率修正
            efficiency = canopy.photosynthetic_efficiency

            # 读取基因决定的最大光合速率
            max_photo = PhenotypeSystem.get(pheno, "max_photosynthesis_rate", 20.0)

            # 简化 Michaelis-Menten 光响应
            if max_photo <= 0 or effective_par <= 0:
                photo_rate = 0.0
            else:
                photo_rate = (
                    efficiency * effective_par
                ) / (1.0 + efficiency * effective_par / max_photo)

            # 将有效 PAR 写入 phenotype，供 GrowthSystem 读取
            PhenotypeSystem.set_trait(pheno, 
                Trait(
                    name="effective_par",
                    value=effective_par,
                    source="plant_photosynthesis",
                )
            )

            # 同时写入冠层修正后的光合速率预估
            PhenotypeSystem.set_trait(pheno, 
                Trait(
                    name="canopy_photosynthesis_rate",
                    value=photo_rate,
                    source="plant_photosynthesis",
                )
            )