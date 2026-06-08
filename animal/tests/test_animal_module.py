#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Animal 模块单元测试（P1 扩展版）

覆盖：
    - Component 创建与属性
    - System 初始化与更新
    - Factory 创建实体
    - 集成：完整动物实体生命周期
    - P1 新增：繁殖组件、记忆驱动觅食
"""

import sys
sys.path.insert(0, r"D:\个人助手\workspace\ECS")

import unittest
from core.world import World
from core.entity import Entity

from animal.components.animal_component import AnimalComponent
from animal.components.animal_needs_component import AnimalNeedsComponent
from animal.components.animal_social_component import AnimalSocialComponent
from animal.components.animal_memory_component import AnimalMemoryComponent, MemoryEntry
from animal.components.animal_territory_component import AnimalTerritoryComponent
from animal.components.animal_reproduction_component import AnimalReproductionComponent

from animal.systems.animal_needs_system import AnimalNeedsSystem
from animal.systems.animal_social_system import AnimalSocialSystem
from animal.systems.animal_memory_system import AnimalMemorySystem
from animal.systems.animal_territory_system import AnimalTerritorySystem
from animal.systems.animal_migration_system import AnimalMigrationSystem
from animal.systems.animal_reproduction_system import AnimalReproductionSystem
from animal.systems.grazing_system import GrazingSystem

from animal.animal_factory import AnimalFactory

from biology.lifecycle.components.energy_component import EnergyComponent
from space.space_component import SpaceComponent


class TestAnimalComponents(unittest.TestCase):
    """测试动物组件"""

    def test_animal_component_creation(self):
        comp = AnimalComponent(species="fast", diet="carnivore", gender="female")
        self.assertEqual(comp.species, "fast")
        self.assertEqual(comp.diet, "carnivore")
        self.assertEqual(comp.gender, "female")
        self.assertFalse(comp.is_adult)

    def test_animal_needs_component(self):
        needs = AnimalNeedsComponent(hunger=0.5, thirst=0.3)
        self.assertEqual(needs.get_dominant_need(), "hunger")
        self.assertFalse(needs.is_critical())
        needs.hunger = 0.9
        self.assertTrue(needs.is_critical())

    def test_animal_social_component(self):
        social = AnimalSocialComponent(group_id=1, group_role="leader")
        social.update_relationship(2, 0.5)
        self.assertAlmostEqual(social.get_relationship(2), 0.5)
        social.update_relationship(2, 0.6)
        self.assertAlmostEqual(social.get_relationship(2), 1.0)  # 上限 1.0

    def test_animal_memory_component(self):
        memory = AnimalMemoryComponent(max_memories=3)
        memory.add_memory(1.0, 2.0, "food", entity_id=10, value=0.8, timestamp=0)
        memory.add_memory(3.0, 4.0, "water", entity_id=20, value=0.6, timestamp=0)

        recalled = memory.recall_by_type("food")
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.entity_id, 10)

        # 测试容量限制
        memory.add_memory(5.0, 6.0, "shelter", value=0.9, timestamp=0)
        memory.add_memory(7.0, 8.0, "food", value=0.7, timestamp=0)  # 应淘汰最弱的
        self.assertLessEqual(len(memory.memories), 3)

    def test_animal_territory_component(self):
        terr = AnimalTerritoryComponent(center_x=5.0, center_y=5.0, radius=3.0)
        self.assertTrue(terr.is_inside(5.0, 5.0))
        self.assertTrue(terr.is_inside(7.0, 5.0))
        self.assertFalse(terr.is_inside(10.0, 10.0))

        terr.add_intruder(99)
        self.assertIn(99, terr.intruders)
        terr.remove_intruder(99)
        self.assertNotIn(99, terr.intruders)

    def test_animal_reproduction_component(self):
        """测试繁殖组件"""
        repro = AnimalReproductionComponent()
        self.assertTrue(repro.is_ready(0))  # 初始状态可繁殖
        self.assertFalse(repro.is_pregnant)

        repro.record_reproduction(10)
        self.assertEqual(repro.reproduction_count, 1)
        self.assertFalse(repro.is_ready(10))  # 冷却期内
        self.assertTrue(repro.is_ready(50))  # 冷却期后

        repro.start_pregnancy(20, mate_id=5)
        self.assertTrue(repro.is_pregnant)
        self.assertEqual(repro.mate_id, 5)
        self.assertFalse(repro.check_birth_ready(20))  # 刚怀孕
        self.assertTrue(repro.check_birth_ready(80))  # 超过怀孕期

        repro.give_birth()
        self.assertFalse(repro.is_pregnant)


class TestAnimalSystems(unittest.TestCase):
    """测试动物系统"""

    def setUp(self):
        self.world = World()

    def test_animal_needs_system(self):
        """测试需求系统更新"""
        entity = self.world.create_entity()
        needs = AnimalNeedsComponent(hunger=0.0)
        energy = EnergyComponent(max_energy=100.0)
        energy.value = 50.0

        self.world.add_component(entity, AnimalComponent())
        self.world.add_component(entity, needs)
        self.world.add_component(entity, energy)

        system = AnimalNeedsSystem()
        system.update(self.world, dt=1.0)

        # 饥饿度应上升（因为能量只有 50%）
        self.assertGreater(needs.hunger, 0.0)

    def test_animal_memory_system(self):
        """测试记忆系统衰减"""
        entity = self.world.create_entity()
        memory = AnimalMemoryComponent(decay_rate=0.5)
        memory.add_memory(1.0, 2.0, "food", value=0.8, timestamp=0)

        self.world.add_component(entity, AnimalComponent())
        self.world.add_component(entity, memory)
        self.world.add_component(entity, SpaceComponent(x=0, y=0))

        system = AnimalMemorySystem()
        system.update(self.world, dt=1.0)

        # 记忆应衰减
        self.assertLess(memory.memories[0].strength, 1.0)

    def test_animal_reproduction_system(self):
        """测试繁殖系统"""
        # 创建雌性动物
        female = self.world.create_entity()
        self.world.add_component(female, AnimalComponent(gender="female", species="basic"))
        self.world.add_component(female, AnimalReproductionComponent())
        energy = EnergyComponent(max_energy=100.0)
        energy.value = 80.0
        self.world.add_component(female, energy)
        from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
        lifecycle = LifeCycleComponent(stage=LifeCycleComponent.MATURE)
        self.world.add_component(female, lifecycle)
        from biology.components.genome_component import GenomeComponent
        self.world.add_component(female, GenomeComponent())
        self.world.add_component(female, SpaceComponent(x=0, y=0))

        # 创建雄性配偶
        male = self.world.create_entity()
        self.world.add_component(male, AnimalComponent(gender="male", species="basic"))
        self.world.add_component(male, AnimalSocialComponent(mate_id=female.id))

        # 为雌性添加社交组件指向雄性
        self.world.add_component(female, AnimalSocialComponent(mate_id=male.id))

        # 运行繁殖系统（tick_counter 足够大以通过冷却期检查）
        system = AnimalReproductionSystem()
        system._tick_counter = 9999
        system.update(self.world, dt=1.0)

        # 雌性应进入怀孕状态或已记录繁殖
        repro = self.world.get_component(female, AnimalReproductionComponent)
        self.assertTrue(repro.is_pregnant or repro.reproduction_count > 0,
                       f"is_pregnant={repro.is_pregnant}, count={repro.reproduction_count}")


class TestAnimalFactory(unittest.TestCase):
    """测试动物工厂"""

    def setUp(self):
        self.world = World()

    def test_create_animal_basic(self):
        """测试创建基础动物"""
        entity = AnimalFactory.create_animal(self.world, species="basic", x=10, y=20)
        self.assertIsInstance(entity, Entity)

        # 检查必要组件
        animal = self.world.get_component(entity, AnimalComponent)
        self.assertIsNotNone(animal)
        self.assertEqual(animal.species, "basic")

        energy = self.world.get_component(entity, EnergyComponent)
        self.assertIsNotNone(energy)

        space = self.world.get_component(entity, SpaceComponent)
        self.assertIsNotNone(space)
        self.assertEqual(space.x, 10)
        self.assertEqual(space.y, 20)

    def test_create_animal_with_new_components(self):
        """测试新组件是否正确挂载"""
        entity = AnimalFactory.create_animal(self.world, species="fast")

        needs = self.world.get_component(entity, AnimalNeedsComponent)
        self.assertIsNotNone(needs)

        social = self.world.get_component(entity, AnimalSocialComponent)
        self.assertIsNotNone(social)

        memory = self.world.get_component(entity, AnimalMemoryComponent)
        self.assertIsNotNone(memory)

        territory = self.world.get_component(entity, AnimalTerritoryComponent)
        self.assertIsNotNone(territory)

        repro = self.world.get_component(entity, AnimalReproductionComponent)
        self.assertIsNotNone(repro)

    def test_create_batch(self):
        """测试批量创建"""
        entities = AnimalFactory.create_batch(self.world, count=5, species="tank")
        self.assertEqual(len(entities), 5)

        for entity in entities:
            animal = self.world.get_component(entity, AnimalComponent)
            self.assertEqual(animal.species, "tank")


class TestAnimalIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        self.world = World()

    def test_full_animal_lifecycle(self):
        """测试完整动物生命周期"""
        # 创建动物
        entity = AnimalFactory.create_animal(self.world, species="predator", x=5, y=5)

        # 运行需求系统
        needs_system = AnimalNeedsSystem()
        needs_system.update(self.world, dt=1.0)

        needs = self.world.get_component(entity, AnimalNeedsComponent)
        self.assertIsNotNone(needs)

        # 运行记忆系统
        memory_system = AnimalMemorySystem()
        memory_system.update(self.world, dt=1.0)

        memory = self.world.get_component(entity, AnimalMemoryComponent)
        self.assertIsNotNone(memory)

        # 验证实体完整性
        self.assertIsNotNone(self.world.get_component(entity, AnimalComponent))
        self.assertIsNotNone(self.world.get_component(entity, EnergyComponent))
        self.assertIsNotNone(self.world.get_component(entity, SpaceComponent))
        self.assertIsNotNone(self.world.get_component(entity, AnimalReproductionComponent))


if __name__ == "__main__":
    unittest.main(verbosity=2)
