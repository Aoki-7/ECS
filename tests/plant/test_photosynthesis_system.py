#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PhotosynthesisSystem 测试

v4.0 新增 — 补充植物模块测试
"""

import pytest

from core.world import World
from core.entity import Entity

from environment.light_field.components.light_receiver_component import LightReceiverComponent
from plant.components.canopy_component import CanopyComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.systems.phenotype_system import PhenotypeSystem
from plant.systems.photosynthesis_system import PlantPhotosynthesisSystem


class TestPhotosynthesisSystem:
    """测试光合作用系统"""

    @pytest.fixture
    def world(self):
        return World()

    def test_photosynthesis_updates_phenotype(self, world):
        """测试光合作用更新表型"""
        entity = world.create_entity()
        light = LightReceiverComponent(received_total=100.0, shade_ratio=0.2)
        canopy = CanopyComponent(photosynthetic_efficiency=0.5)
        pheno = PhenotypeComponent()

        world.add_component(entity, light)
        world.add_component(entity, canopy)
        world.add_component(entity, pheno)

        system = PlantPhotosynthesisSystem()
        system.update(world, dt=1.0)

        # 表型应被更新
        effective_par = PhenotypeSystem.get(pheno, "effective_par")
        assert effective_par is not None
        assert effective_par == 80.0  # 100 * (1 - 0.2)

    def test_photosynthesis_rate(self, world):
        """测试光合速率计算"""
        entity = world.create_entity()
        light = LightReceiverComponent(received_total=200.0, shade_ratio=0.0)
        canopy = CanopyComponent(photosynthetic_efficiency=0.8)
        pheno = PhenotypeComponent()
        PhenotypeSystem.set_trait(pheno, type('Trait', (), {'name': 'max_photosynthesis_rate', 'value': 50.0, 'source': 'test'})())

        world.add_component(entity, light)
        world.add_component(entity, canopy)
        world.add_component(entity, pheno)

        system = PlantPhotosynthesisSystem()
        system.update(world, dt=1.0)

        photo_rate = PhenotypeSystem.get(pheno, "canopy_photosynthesis_rate")
        assert photo_rate is not None
        assert photo_rate > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
