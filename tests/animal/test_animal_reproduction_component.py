#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
动物繁殖组件测试

v3.9 适配：方法迁移到 AnimalReproductionSystem
"""

import unittest
from biology.organisms.animal.components.animal_reproduction_component import AnimalReproductionComponent
from biology.organisms.animal.systems.animal_reproduction_system import AnimalReproductionSystem


class TestAnimalReproductionComponent(unittest.TestCase):
    """测试繁殖组件"""

    def test_is_ready(self):
        """测试冷却期检查"""
        repro = AnimalReproductionComponent()
        self.assertTrue(AnimalReproductionSystem.is_ready(repro, 0))

        AnimalReproductionSystem.record_reproduction(repro, 10)
        self.assertFalse(AnimalReproductionSystem.is_ready(repro, 10))
        self.assertTrue(AnimalReproductionSystem.is_ready(repro, 35))

    def test_pregnancy(self):
        """测试怀孕流程"""
        repro = AnimalReproductionComponent()
        AnimalReproductionSystem.start_pregnancy(repro, 50, mate_id=99)
        self.assertTrue(repro.is_pregnant)
        self.assertEqual(repro.mate_id, 99)

        self.assertFalse(AnimalReproductionSystem.check_birth_ready(repro, 80))
        self.assertTrue(AnimalReproductionSystem.check_birth_ready(repro, 110))

        AnimalReproductionSystem.give_birth(repro)
        self.assertFalse(repro.is_pregnant)
        self.assertEqual(repro.mate_id, -1)


if __name__ == "__main__":
    unittest.main()