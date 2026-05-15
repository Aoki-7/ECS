#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件:reproduction_system.py
@说明:暂时不使用，需优化。
@时间:2026/03/09 18:04:34
@作者:Sherry
@版本:1.0
'''





import random

from core.system import System
from core.world import World

from biology.components.energy_component import EnergyComponent
from biology.components.genome_component import GenomeComponent
from biology.factories.plant_factory import PlantFactory

class ReproductionSystem(System):
    """
        植物繁殖系统
    """
    def update(self, world: World, dt):

        new_entities = []

        for entity, (genome, energy, pos) in \
                world.get_components(GenomeComponent, EnergyComponent, PositionComponent):

            genome: GenomeComponent
            energy: EnergyComponent
            pos: PositionComponent

            if energy.value > 8:

                energy.value *= 0.5

                child_genome = genome.mutate(0.2)

                dx = random.randint(-1, 1)
                dy = random.randint(-1, 1)

                new_entities.append(
                    (pos.x+dx, pos.y+dy, child_genome)
                )

        for x, y, genome in new_entities:
            create_plant(world, x, y, genome)