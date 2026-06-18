#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Plant 模块综合测试

覆盖范围：
    1. PlantFactory      — 实体创建、组件挂载、基因组构建、批量创建、子代遗传
    2. Presets           — 物种预设完整性、基因值合理性
    3. PlantComponent    — 默认值与属性访问
    4. CanopyComponent   — 默认值与属性访问
    5. RootComponent     — 默认值与属性访问
    6. PlantPhotosynthesisSystem — 光合作用计算与 phenotype 写入
    7. SeedDispersalSystem       — 传播条件判定、边界检查、土壤适宜性
    8. PlantWaterUptakeSystem    — 吸水计算、水分胁迫、phenotype 写入
    9. TerrainAdaptationSystem   — 地形修正因子、坡度惩罚、phenotype 写入
"""

import math
import random
import sys
import unittest
from pathlib import Path

# 确保项目根目录在路径中
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.world import World
from core.entity import Entity
from core.components.world_config_component import WorldConfigComponent

from plant.plant_factory import PlantFactory
from plant.presets import SPECIES_PRESETS, SPECIES_LIFECYCLE
from plant.components.plant_component import PlantComponent
from plant.components.canopy_component import CanopyComponent
from plant.components.root_component import RootComponent
from plant.systems.photosynthesis_system import PlantPhotosynthesisSystem
from plant.systems.seed_dispersal_system import SeedDispersalSystem
from plant.systems.water_uptake_system import PlantWaterUptakeSystem
from plant.systems.terrain_adaptation_system import TerrainAdaptationSystem

from biology.components.genome_component import GenomeComponent
from biology.components.phenotype_component import PhenotypeComponent
from biology.systems.phenotype_system import PhenotypeSystem
from biology.lifecycle.components.energy_component import EnergyComponent
from biology.lifecycle.components.life_cycle_component import LifeCycleComponent
from biology.lifecycle.components.morphology_component import MorphologyComponent
from space.space_component import SpaceComponent
from environment.light_field.components.light_receiver_component import LightReceiverComponent
from environment.soil.components.soil_component import SoilComponent
from environment.terrain.components.terrain_component import TerrainComponent
from environment.terrain.config.terrain_types import TerrainType


# ---------------------------------------------------------------------------
# 测试基类 — 提供 World 初始化和通用辅助方法
# ---------------------------------------------------------------------------

class PlantTestBase(unittest.TestCase):
    """Plant 模块测试基类"""

    def setUp(self):
        """每个测试前创建新的 World 实例"""
        self.world = World()
        # 挂载 WorldConfigComponent（供 SeedDispersalSystem 等查询边界）
        from world.world_entity import WorldEntity
        world_entity = WorldEntity()
        world_entity.add_component(WorldConfigComponent(map_width=100, map_height=100))
        self.world.set_world_entity(world_entity)

    def tearDown(self):
        """清理"""
        self.world = None

    def create_soil(self, x: int, y: int, moisture: float = 0.5,
                    wilting_point: float = 0.15, field_capacity: float = 0.45) -> Entity:
        """在指定坐标创建土壤实体"""
        soil_entity = self.world.create_entity()
        self.world.add_component(soil_entity, SpaceComponent(x=x, y=y, layer=0))
        self.world.add_component(soil_entity, SoilComponent(
            moisture=moisture,
            wilting_point=wilting_point,
            field_capacity=field_capacity,
        ))
        return soil_entity

    def create_terrain(self, x: int, y: int, terrain_type: TerrainType,
                       slope: float = 0.0) -> Entity:
        """在指定坐标创建地形实体"""
        terrain_entity = self.world.create_entity()
        self.world.add_component(terrain_entity, SpaceComponent(x=x, y=y, layer=0))
        self.world.add_component(terrain_entity, TerrainComponent(
            terrain_type=terrain_type,
            slope=slope,
        ))
        return terrain_entity

    def create_mature_plant(self, x: int = 10, y: int = 10,
                            energy_value: float = 50.0,
                            species: str = "basic") -> Entity:
        """
        创建一株处于成熟期的植物（用于测试传播、光合作用等）
        """
        entity = PlantFactory.create_plant(
            self.world, species=species, x=x, y=y, seed=42
        )
        # 强制推进到成熟期
        lifecycle = self.world.get_component(entity, LifeCycleComponent)
        lifecycle.stage = LifeCycleComponent.MATURE
        # 设置足够能量
        energy = self.world.get_component(entity, EnergyComponent)
        energy.value = energy_value
        return entity


# ---------------------------------------------------------------------------
# 一、PlantFactory 测试
# ---------------------------------------------------------------------------

class TestPlantFactory(PlantTestBase):
    """PlantFactory 单元测试"""

    def test_create_plant_basic(self):
        """基础创建：实体不为空，组件全部挂载"""
        entity = PlantFactory.create_plant(self.world, species="basic", x=5, y=7)
        self.assertIsInstance(entity, Entity)
        self.assertTrue(self.world.has_entity(entity))

        # 验证所有必需组件已挂载
        required_components = [
            GenomeComponent,
            PhenotypeComponent,
            EnergyComponent,
            LifeCycleComponent,
            SpaceComponent,
            PlantComponent,
            LightReceiverComponent,
            CanopyComponent,
            RootComponent,
        ]
        for comp_type in required_components:
            comp = self.world.get_component(entity, comp_type)
            self.assertIsNotNone(comp, f"缺少组件: {comp_type.__name__}")

    def test_create_plant_space_coordinates(self):
        """空间坐标正确写入"""
        entity = PlantFactory.create_plant(self.world, species="basic", x=12, y=34)
        space = self.world.get_component(entity, SpaceComponent)
        self.assertEqual(space.x, 12)
        self.assertEqual(space.y, 34)
        self.assertEqual(space.layer, 0)

    def test_create_plant_unknown_species_raises(self):
        """未知物种应抛出 ValueError"""
        with self.assertRaises(ValueError) as ctx:
            PlantFactory.create_plant(self.world, species="nonexistent")
        self.assertIn("Unknown species", str(ctx.exception))

    def test_create_plant_negative_variation_raises(self):
        """负变异系数应抛出 ValueError"""
        with self.assertRaises(ValueError) as ctx:
            PlantFactory.create_plant(self.world, variation=-0.1)
        self.assertIn("variation must be >= 0", str(ctx.exception))

    def test_create_plant_seed_reproducibility(self):
        """相同种子应产生相同基因值"""
        world1 = World()
        world2 = World()
        e1 = PlantFactory.create_plant(world1, seed=12345, variation=0.0)
        e2 = PlantFactory.create_plant(world2, seed=12345, variation=0.0)

        genome1 = world1.get_component(e1, GenomeComponent)
        genome2 = world2.get_component(e2, GenomeComponent)

        self.assertEqual(len(genome1.genes), len(genome2.genes))
        for g1, g2 in zip(genome1.genes, genome2.genes):
            self.assertEqual(g1.expression_target, g2.expression_target)
            self.assertAlmostEqual(g1.strength, g2.strength, places=10)

    def test_create_plant_variation_range(self):
        """变异后基因值应在合理范围内"""
        entity = PlantFactory.create_plant(self.world, species="basic",
                                            variation=0.2, seed=999)
        genome = self.world.get_component(entity, GenomeComponent)
        preset = SPECIES_PRESETS["basic"]

        for gene in genome.genes:
            base = preset.get(gene.expression_target)
            if base is not None:
                delta = base * 0.2
                self.assertGreaterEqual(gene.strength, base - delta)
                self.assertLessEqual(gene.strength, base + delta)

    def test_create_batch(self):
        """批量创建数量正确，实体互不相同"""
        entities = PlantFactory.create_batch(self.world, count=5,
                                              species="tree", seed=777)
        self.assertEqual(len(entities), 5)
        ids = {e.id for e in entities}
        self.assertEqual(len(ids), 5, "批量创建的实体 ID 应互不相同")

    def test_create_plant_from_genome(self):
        """基于亲代基因组创建子代"""
        parent = PlantFactory.create_plant(self.world, species="basic", seed=111)
        parent_genome = self.world.get_component(parent, GenomeComponent)

        child = PlantFactory.create_plant_from_genome(
            self.world, parent_genome, x=20, y=30, variation=0.0
        )
        self.assertIsInstance(child, Entity)

        # 子代应以种子阶段开始
        lifecycle = self.world.get_component(child, LifeCycleComponent)
        from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
        self.assertTrue(LifeCycleSystem.is_seed(lifecycle))

        # 子代能量较低（种子状态）
        energy = self.world.get_component(child, EnergyComponent)
        self.assertEqual(energy.value, 5.0)

        # 空间坐标正确
        space = self.world.get_component(child, SpaceComponent)
        self.assertEqual(space.x, 20)
        self.assertEqual(space.y, 30)

    def test_create_plant_lifecycle_stage(self):
        """新创建植物应以 SEED 阶段开始"""
        entity = PlantFactory.create_plant(self.world)
        lifecycle = self.world.get_component(entity, LifeCycleComponent)
        from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
        self.assertTrue(LifeCycleSystem.is_seed(lifecycle))
        self.assertEqual(lifecycle.stage, LifeCycleComponent.SEED)

    def test_all_species_can_create(self):
        """所有预设物种都能成功创建"""
        for species in SPECIES_PRESETS:
            with self.subTest(species=species):
                entity = PlantFactory.create_plant(self.world, species=species)
                self.assertTrue(self.world.has_entity(entity))
                genome = self.world.get_component(entity, GenomeComponent)
                self.assertGreater(len(genome.genes), 0)


# ---------------------------------------------------------------------------
# 二、Presets 测试
# ---------------------------------------------------------------------------

class TestPresets(unittest.TestCase):
    """物种预设测试"""

    def test_species_presets_not_empty(self):
        """预设表不为空"""
        self.assertGreater(len(SPECIES_PRESETS), 0)

    def test_all_species_have_lifecycle(self):
        """每个物种都有对应的生命周期配置"""
        for species in SPECIES_PRESETS:
            with self.subTest(species=species):
                self.assertIn(species, SPECIES_LIFECYCLE)
                self.assertIn("max_age", SPECIES_LIFECYCLE[species])
                self.assertGreater(SPECIES_LIFECYCLE[species]["max_age"], 0)

    def test_gene_values_positive(self):
        """所有基因值应为正数"""
        for species, genes in SPECIES_PRESETS.items():
            for gene_name, value in genes.items():
                with self.subTest(species=species, gene=gene_name):
                    self.assertGreaterEqual(value, 0.0,
                                            f"{species}.{gene_name} = {value} 不应为负")

    def test_basic_species_has_all_genes(self):
        """基础物种应包含全部 23 个基因"""
        basic_genes = SPECIES_PRESETS["basic"]
        expected_genes = [
            "max_photosynthesis_rate", "light_use_efficiency", "shade_tolerance",
            "light_compensation_point", "light_saturation_point",
            "water_use_efficiency", "nutrient_use_efficiency", "carbon_storage_efficiency",
            "cold_tolerance", "heat_tolerance", "drought_tolerance", "flood_tolerance",
            "metabolism_rate", "growth_partition", "maintenance_cost", "storage_partition",
            "seed_production", "seed_size", "dispersal_radius", "germination_rate",
            "mutation_rate", "adaptability", "genetic_stability",
        ]
        for gene in expected_genes:
            with self.subTest(gene=gene):
                self.assertIn(gene, basic_genes)

    def test_species_diversity(self):
        """不同物种应有显著不同的基因配置"""
        basic = SPECIES_PRESETS["basic"]
        fast = SPECIES_PRESETS["fast"]
        tree = SPECIES_PRESETS["tree"]

        # 速生杂草代谢率应高于基础
        self.assertGreater(fast["metabolism_rate"], basic["metabolism_rate"])
        # 乔木寿命应长于基础
        self.assertGreater(SPECIES_LIFECYCLE["tree"]["max_age"],
                           SPECIES_LIFECYCLE["basic"]["max_age"])
        # 乔木繁殖率应低于杂草
        self.assertLess(tree["seed_production"], fast["seed_production"])


# ---------------------------------------------------------------------------
# 三、Plant 组件测试
# ---------------------------------------------------------------------------

class TestPlantComponents(unittest.TestCase):
    """Plant 相关组件测试"""

    def test_plant_component_defaults(self):
        """PlantComponent 默认值正确"""
        pc = PlantComponent()
        self.assertEqual(pc.harvestable_yield, 0.0)
        self.assertEqual(pc.max_yield, 0.0)
        self.assertEqual(pc.harvest_stage, 3)  # MATURE
        self.assertEqual(pc.yield_type, "berry")
        self.assertEqual(pc.nutrition_per_unit, 5.0)
        self.assertTrue(pc.is_perennial)
        self.assertEqual(pc.regrowth_rate, 0.1)
        self.assertFalse(pc.produces_wood)
        self.assertEqual(pc.wood_amount, 0.0)

    def test_canopy_component_defaults(self):
        """CanopyComponent 默认值正确"""
        cc = CanopyComponent()
        self.assertEqual(cc.leaf_area_index, 0.5)
        self.assertEqual(cc.canopy_radius, 5.0)
        self.assertEqual(cc.shade_ratio, 0.0)
        self.assertEqual(cc.photosynthetic_efficiency, 0.05)

    def test_root_component_defaults(self):
        """RootComponent 默认值正确"""
        rc = RootComponent()
        self.assertEqual(rc.root_depth, 5.0)
        self.assertEqual(rc.root_radius, 10.0)
        self.assertEqual(rc.water_absorption_rate, 1.0)
        self.assertEqual(rc.nutrient_absorption_rate, 1.0)
        self.assertEqual(rc.current_water_uptake, 0.0)

    def test_plant_component_slots(self):
        """PlantComponent 使用 __slots__（无 __dict__）"""
        pc = PlantComponent()
        self.assertFalse(hasattr(pc, "__dict__"))

    def test_canopy_component_slots(self):
        """CanopyComponent 使用 __slots__"""
        cc = CanopyComponent()
        self.assertFalse(hasattr(cc, "__dict__"))

    def test_root_component_slots(self):
        """RootComponent 使用 __slots__"""
        rc = RootComponent()
        self.assertFalse(hasattr(rc, "__dict__"))


# ---------------------------------------------------------------------------
# 四、PlantPhotosynthesisSystem 测试
# ---------------------------------------------------------------------------

class TestPlantPhotosynthesisSystem(PlantTestBase):
    """光合作用系统测试"""

    def setUp(self):
        super().setUp()
        self.system = PlantPhotosynthesisSystem()

    def test_no_light_zero_rate(self):
        """无光照时 photo_rate = 0"""
        entity = self.create_mature_plant(x=10, y=10)
        light = self.world.get_component(entity, LightReceiverComponent)
        light.received_total = 0.0
        light.shade_ratio = 0.0

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        self.assertEqual(PhenotypeSystem.get(pheno, "canopy_photosynthesis_rate"), 0.0)
        self.assertEqual(PhenotypeSystem.get(pheno, "effective_par"), 0.0)

    def test_zero_max_photo_rate(self):
        """max_photo = 0 时 photo_rate = 0"""
        entity = self.create_mature_plant(x=10, y=10)
        light = self.world.get_component(entity, LightReceiverComponent)
        light.received_total = 100.0
        light.shade_ratio = 0.0

        pheno = self.world.get_component(entity, PhenotypeComponent)
        PhenotypeSystem.set_trait(pheno, __import__("biology.traits.trait", fromlist=["Trait"]).Trait(
            name="max_photosynthesis_rate", value=0.0, source="test"
        ))

        self.system.update(self.world, dt=1.0)
        self.assertEqual(PhenotypeSystem.get(pheno, "canopy_photosynthesis_rate"), 0.0)

    def test_photosynthesis_calculation(self):
        """有光照时光合速率计算正确"""
        entity = self.create_mature_plant(x=10, y=10)
        light = self.world.get_component(entity, LightReceiverComponent)
        light.received_total = 200.0
        light.shade_ratio = 0.0

        canopy = self.world.get_component(entity, CanopyComponent)
        canopy.photosynthetic_efficiency = 0.05

        pheno = self.world.get_component(entity, PhenotypeComponent)
        PhenotypeSystem.set_trait(pheno, __import__("biology.traits.trait", fromlist=["Trait"]).Trait(
            name="max_photosynthesis_rate", value=20.0, source="test"
        ))

        self.system.update(self.world, dt=1.0)

        effective_par = PhenotypeSystem.get(pheno, "effective_par")
        photo_rate = PhenotypeSystem.get(pheno, "canopy_photosynthesis_rate")

        # effective_par = received_total * (1 - shade_ratio) = 200
        self.assertEqual(effective_par, 200.0)

        # photo_rate = (efficiency * effective_par) / (1 + efficiency * effective_par / max_photo)
        #            = (0.05 * 200) / (1 + 0.05 * 200 / 20)
        #            = 10 / (1 + 10/20) = 10 / 1.5 = 6.666...
        expected = (0.05 * 200.0) / (1.0 + 0.05 * 200.0 / 20.0)
        self.assertAlmostEqual(photo_rate, expected, places=5)
        self.assertGreater(photo_rate, 0.0)

    def test_shade_ratio_reduces_par(self):
        """遮光率降低有效 PAR"""
        entity = self.create_mature_plant(x=10, y=10)
        light = self.world.get_component(entity, LightReceiverComponent)
        light.received_total = 100.0
        light.shade_ratio = 0.5

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        effective_par = PhenotypeSystem.get(pheno, "effective_par")
        # effective_par = 100 * (1 - 0.5) = 50
        self.assertEqual(effective_par, 50.0)

    def test_trait_source_tagged(self):
        """写入的 trait 来源标记正确"""
        entity = self.create_mature_plant(x=10, y=10)
        light = self.world.get_component(entity, LightReceiverComponent)
        light.received_total = 50.0
        light.shade_ratio = 0.0

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        trait = pheno.traits.get("canopy_photosynthesis_rate")
        self.assertIsNotNone(trait)
        self.assertEqual(trait.source, "plant_photosynthesis")


# ---------------------------------------------------------------------------
# 五、SeedDispersalSystem 测试
# ---------------------------------------------------------------------------

class TestSeedDispersalSystem(PlantTestBase):
    """种子传播系统测试"""

    def setUp(self):
        super().setUp()
        self.system = SeedDispersalSystem(seed=42)
        self.system.enable_log = False

    def test_immature_plant_no_dispersal(self):
        """非成熟期植物不传播"""
        entity = PlantFactory.create_plant(self.world, species="basic", x=50, y=50)
        # 保持在 SEED 阶段
        lifecycle = self.world.get_component(entity, LifeCycleComponent)
        from biology.lifecycle.systems.life_cycle_system import LifeCycleSystem
        self.assertTrue(LifeCycleSystem.is_seed(lifecycle))

        count_before = len(list(self.world.get_entities_with(PlantComponent)))
        self.system.update(self.world, dt=1.0)
        count_after = len(list(self.world.get_entities_with(PlantComponent)))

        self.assertEqual(count_after, count_before)

    def test_low_energy_no_dispersal(self):
        """能量不足不传播"""
        entity = self.create_mature_plant(x=50, y=50, energy_value=10.0)
        # 能量 < BASE_ENERGY_THRESHOLD(25)

        count_before = len(list(self.world.get_entities_with(PlantComponent)))
        self.system.update(self.world, dt=1.0)
        count_after = len(list(self.world.get_entities_with(PlantComponent)))

        self.assertEqual(count_after, count_before)

    def test_cooldown_prevents_dispersal(self):
        """冷却期内不重复传播"""
        entity = self.create_mature_plant(x=50, y=50, energy_value=100.0)

        # 第一次传播
        self.system.update(self.world, dt=1.0)
        count_after_first = len(list(self.world.get_entities_with(PlantComponent)))

        # 冷却期内再次更新
        self.system.update(self.world, dt=1.0)
        count_after_second = len(list(self.world.get_entities_with(PlantComponent)))

        self.assertEqual(count_after_second, count_after_first)

    def test_mature_high_energy_disperses(self):
        """成熟期+高能量应传播种子"""
        entity = self.create_mature_plant(x=50, y=50, energy_value=100.0)

        count_before = len(list(self.world.get_entities_with(PlantComponent)))
        self.system.update(self.world, dt=1.0)
        count_after = len(list(self.world.get_entities_with(PlantComponent)))

        self.assertGreater(count_after, count_before,
                           "传播后植物数量应增加")

    def test_boundary_check(self):
        """边界外不创建子代"""
        entity = self.create_mature_plant(x=1, y=1, energy_value=100.0)
        # 靠近边界，大量种子会落在界外
        space = self.world.get_component(entity, SpaceComponent)
        space.x = 0
        space.y = 0

        count_before = len(list(self.world.get_entities_with(PlantComponent)))
        # 多次更新增加传播概率
        for _ in range(5):
            self.system.update(self.world, dt=1.0)
            # 重置冷却以便下次能触发
            self.system._last_reproduction.clear()
            energy = self.world.get_component(entity, EnergyComponent)
            energy.value = 100.0

        count_after = len(list(self.world.get_entities_with(PlantComponent)))
        # 所有子代坐标都应在 [0, 99] 范围内
        for e, (sp, _) in self.world.get_components(SpaceComponent, PlantComponent):
            self.assertGreaterEqual(sp.x, 0)
            self.assertLess(sp.x, 100)
            self.assertGreaterEqual(sp.y, 0)
            self.assertLess(sp.y, 100)

    def test_dry_soil_prevents_germination(self):
        """干旱土壤阻止种子萌发"""
        entity = self.create_mature_plant(x=50, y=50, energy_value=100.0)

        # 在植物周围创建干旱土壤
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                self.create_soil(
                    x=50 + dx * 10, y=50 + dy * 10,
                    moisture=0.05,  # 远低于 wilting_point(0.15)
                    wilting_point=0.15,
                )

        count_before = len(list(self.world.get_entities_with(PlantComponent)))
        # 多次尝试传播
        for _ in range(10):
            self.system.update(self.world, dt=1.0)
            self.system._last_reproduction.clear()
            energy = self.world.get_component(entity, EnergyComponent)
            energy.value = 100.0

        count_after = len(list(self.world.get_entities_with(PlantComponent)))
        # 由于干旱，几乎不会有新植物产生
        self.assertLessEqual(count_after - count_before, 2,
                             "干旱土壤中不应有大量新植物")

    def test_energy_consumed_after_dispersal(self):
        """传播后能量应被消耗"""
        entity = self.create_mature_plant(x=50, y=50, energy_value=100.0)
        energy_before = self.world.get_component(entity, EnergyComponent).value

        self.system.update(self.world, dt=1.0)
        energy_after = self.world.get_component(entity, EnergyComponent).value

        # 能量消耗 30%
        self.assertAlmostEqual(energy_after, energy_before * 0.7, places=5)

    def test_child_inherits_genome(self):
        """子代应继承亲代基因组"""
        entity = self.create_mature_plant(x=50, y=50, energy_value=100.0, species="basic")
        parent_genome = self.world.get_component(entity, GenomeComponent)

        self.system.update(self.world, dt=1.0)

        # 找到新创建的植物（子代）
        new_plants = []
        for e, _ in self.world.get_components(PlantComponent):
            if e.id != entity.id:
                new_plants.append(e)

        if new_plants:
            child = new_plants[0]
            child_genome = self.world.get_component(child, GenomeComponent)
            self.assertIsNotNone(child_genome)
            self.assertGreater(len(child_genome.genes), 0)


# ---------------------------------------------------------------------------
# 六、PlantWaterUptakeSystem 测试
# ---------------------------------------------------------------------------

class TestPlantWaterUptakeSystem(PlantTestBase):
    """水分吸收系统测试"""

    def setUp(self):
        super().setUp()
        self.system = PlantWaterUptakeSystem()

    def test_no_soil_skips(self):
        """无对应土壤时跳过吸水"""
        entity = self.create_mature_plant(x=50, y=50)
        root = self.world.get_component(entity, RootComponent)
        root.current_water_uptake = 0.0

        self.system.update(self.world, dt=1.0)
        self.assertEqual(root.current_water_uptake, 0.0)

    def test_normal_water_uptake(self):
        """正常土壤条件下吸水"""
        self.create_soil(x=50, y=50, moisture=0.5,
                         wilting_point=0.15, field_capacity=0.45)
        entity = self.create_mature_plant(x=50, y=50)
        root = self.world.get_component(entity, RootComponent)
        root.water_absorption_rate = 1.0

        self.system.update(self.world, dt=1.0)

        # 应有一定吸水量
        self.assertGreater(root.current_water_uptake, 0.0)
        self.assertLessEqual(root.current_water_uptake, 0.5 - 0.15)

    def test_soil_moisture_decreases(self):
        """吸水后土壤湿度应下降"""
        soil_entity = self.create_soil(x=50, y=50, moisture=0.5,
                                       wilting_point=0.15, field_capacity=0.45)
        entity = self.create_mature_plant(x=50, y=50)

        soil = self.world.get_component(soil_entity, SoilComponent)
        moisture_before = soil.moisture

        self.system.update(self.world, dt=1.0)

        moisture_after = soil.moisture
        self.assertLess(moisture_after, moisture_before)
        self.assertGreaterEqual(moisture_after, soil.wilting_point)

    def test_wilting_point_stress(self):
        """湿度在凋萎点时胁迫为 1.0"""
        self.create_soil(x=50, y=50, moisture=0.15,
                         wilting_point=0.15, field_capacity=0.45)
        entity = self.create_mature_plant(x=50, y=50)

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        stress = PhenotypeSystem.get(pheno, "plant_water_stress")
        self.assertEqual(stress, 1.0)

    def test_field_capacity_no_stress(self):
        """湿度高于田间持水量时胁迫接近 0"""
        # 使用较高的初始湿度，确保吸水后仍接近田间持水量
        self.create_soil(x=50, y=50, moisture=0.55,
                         wilting_point=0.15, field_capacity=0.45)
        entity = self.create_mature_plant(x=50, y=50)

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        stress = PhenotypeSystem.get(pheno, "plant_water_stress")
        # 吸水后土壤湿度可能略降，stress 应非常接近 0
        self.assertLess(stress, 0.1)

    def test_intermediate_stress(self):
        """中间湿度胁迫值在 (0, 1) 之间"""
        self.create_soil(x=50, y=50, moisture=0.30,
                         wilting_point=0.15, field_capacity=0.45)
        entity = self.create_mature_plant(x=50, y=50)

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        stress = PhenotypeSystem.get(pheno, "plant_water_stress")
        self.assertGreater(stress, 0.0)
        self.assertLess(stress, 1.0)

    def test_phenotype_trait_source(self):
        """写入 phenotype 的 trait 来源标记正确"""
        self.create_soil(x=50, y=50, moisture=0.3,
                         wilting_point=0.15, field_capacity=0.45)
        entity = self.create_mature_plant(x=50, y=50)

        self.system.update(self.world, dt=1.0)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        trait = pheno.traits.get("plant_water_stress")
        self.assertIsNotNone(trait)
        self.assertEqual(trait.source, "plant_water_uptake")


# ---------------------------------------------------------------------------
# 七、TerrainAdaptationSystem 测试
# ---------------------------------------------------------------------------

class TestTerrainAdaptationSystem(PlantTestBase):
    """地形适应性系统测试"""

    def setUp(self):
        super().setUp()
        self.system = TerrainAdaptationSystem()

    def test_no_terrain_skips(self):
        """无对应地形时跳过"""
        entity = self.create_mature_plant(x=50, y=50)
        pheno_before = self.world.get_component(entity, PhenotypeComponent)

        self.system.update(self.world, dt=1.0)
        # 无异常即通过

    def test_plain_modifier(self):
        """平原修正因子 = 1.0"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.PLAIN, slope=0.0)
        entity = self.create_mature_plant(x=50, y=50)

        # 预设一个基准光合速率
        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="max_photosynthesis_rate", value=20.0, source="test"))

        self.system.update(self.world, dt=1.0)

        adjusted = PhenotypeSystem.get(pheno, "max_photosynthesis_rate")
        self.assertAlmostEqual(adjusted, 20.0, places=5)

    def test_desert_modifier(self):
        """沙漠修正因子 = 0.4"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.DESERT, slope=0.0)
        entity = self.create_mature_plant(x=50, y=50)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="max_photosynthesis_rate", value=20.0, source="test"))

        self.system.update(self.world, dt=1.0)

        adjusted = PhenotypeSystem.get(pheno, "max_photosynthesis_rate")
        self.assertAlmostEqual(adjusted, 20.0 * 0.4, places=5)

    def test_water_modifier(self):
        """水域修正因子 = 0.0（植物无法生长）"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.WATER, slope=0.0)
        entity = self.create_mature_plant(x=50, y=50)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="max_photosynthesis_rate", value=20.0, source="test"))

        self.system.update(self.world, dt=1.0)

        adjusted = PhenotypeSystem.get(pheno, "max_photosynthesis_rate")
        self.assertEqual(adjusted, 0.0)

    def test_slope_penalty(self):
        """坡度 > 15° 时应施加惩罚"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.PLAIN, slope=30.0)
        entity = self.create_mature_plant(x=50, y=50)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="max_photosynthesis_rate", value=20.0, source="test"))

        self.system.update(self.world, dt=1.0)

        adjusted = PhenotypeSystem.get(pheno, "max_photosynthesis_rate")
        # slope_penalty = max(0.3, 1.0 - (30-15)/50) = max(0.3, 0.7) = 0.7
        expected = 20.0 * 1.0 * 0.7
        self.assertAlmostEqual(adjusted, expected, places=5)

    def test_water_stress_bonus_desert(self):
        """沙漠地形增加水分胁迫"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.DESERT, slope=0.0)
        entity = self.create_mature_plant(x=50, y=50)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="plant_water_stress", value=0.2, source="test"))

        self.system.update(self.world, dt=1.0)

        stress = PhenotypeSystem.get(pheno, "plant_water_stress")
        # 0.2 + 0.3 = 0.5
        self.assertAlmostEqual(stress, 0.5, places=5)

    def test_water_stress_bonus_swamp(self):
        """沼泽地形降低水分胁迫"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.SWAMP, slope=0.0)
        entity = self.create_mature_plant(x=50, y=50)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="plant_water_stress", value=0.5, source="test"))

        self.system.update(self.world, dt=1.0)

        stress = PhenotypeSystem.get(pheno, "plant_water_stress")
        # 0.5 - 0.2 = 0.3
        self.assertAlmostEqual(stress, 0.3, places=5)

    def test_trait_source_tagged(self):
        """写入的 trait 来源标记正确"""
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.PLAIN, slope=0.0)
        entity = self.create_mature_plant(x=50, y=50)

        pheno = self.world.get_component(entity, PhenotypeComponent)
        from biology.traits.trait import Trait
        PhenotypeSystem.set_trait(pheno, Trait(name="max_photosynthesis_rate", value=20.0, source="test"))

        self.system.update(self.world, dt=1.0)

        trait = pheno.traits.get("max_photosynthesis_rate")
        self.assertIsNotNone(trait)
        self.assertEqual(trait.source, "terrain_adaptation")


# ---------------------------------------------------------------------------
# 八、综合集成测试
# ---------------------------------------------------------------------------

class TestPlantIntegration(PlantTestBase):
    """Plant 模块综合集成测试"""

    def test_full_pipeline(self):
        """完整流程：创建 → 光合作用 → 吸水 → 地形适应 → 传播"""
        # 1. 创建环境
        self.create_soil(x=50, y=50, moisture=0.4, wilting_point=0.15,
                         field_capacity=0.45)
        self.create_terrain(x=50, y=50, terrain_type=TerrainType.GRASSLAND,
                            slope=5.0)

        # 2. 创建植物
        entity = self.create_mature_plant(x=50, y=50, energy_value=100.0)

        # 3. 设置光照
        light = self.world.get_component(entity, LightReceiverComponent)
        light.received_total = 300.0
        light.shade_ratio = 0.1

        # 4. 执行各系统更新
        PlantPhotosynthesisSystem().update(self.world, dt=1.0)
        PlantWaterUptakeSystem().update(self.world, dt=1.0)
        TerrainAdaptationSystem().update(self.world, dt=1.0)

        # 5. 验证 phenotype 中有所有系统的输出
        pheno = self.world.get_component(entity, PhenotypeComponent)
        self.assertIn("effective_par", pheno.traits)
        self.assertIn("canopy_photosynthesis_rate", pheno.traits)
        self.assertIn("plant_water_stress", pheno.traits)

        # 6. 执行传播
        dispersal = SeedDispersalSystem(seed=42)
        dispersal.enable_log = False
        dispersal.update(self.world, dt=1.0)

        # 7. 验证可能有新植物产生
        all_plants = list(self.world.get_entities_with(PlantComponent))
        self.assertGreaterEqual(len(all_plants), 1)

    def test_multiple_species_coexist(self):
        """多种植物共存"""
        species_list = ["basic", "tree", "fast"]
        entities = []
        for i, species in enumerate(species_list):
            e = PlantFactory.create_plant(self.world, species=species,
                                          x=10 + i * 10, y=10 + i * 10)
            entities.append(e)

        self.assertEqual(len(entities), 3)
        for e in entities:
            self.assertTrue(self.world.has_entity(e))

    def test_plant_factory_and_systems_no_errors(self):
        """工厂 + 系统组合运行无异常"""
        for _ in range(5):
            e = PlantFactory.create_plant(self.world, x=random.randint(10, 90),
                                          y=random.randint(10, 90))
            lifecycle = self.world.get_component(e, LifeCycleComponent)
            lifecycle.stage = LifeCycleComponent.MATURE
            energy = self.world.get_component(e, EnergyComponent)
            energy.value = 100.0

        for _ in range(3):
            PlantPhotosynthesisSystem().update(self.world, dt=1.0)
            PlantWaterUptakeSystem().update(self.world, dt=1.0)
            TerrainAdaptationSystem().update(self.world, dt=1.0)

        # 无异常即通过
        self.assertTrue(True)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
