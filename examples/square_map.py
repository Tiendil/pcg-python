
import enum

from pcg import nodes
from pcg import colors
from pcg import geometry
from pcg import topologies
from pcg.space import Space
from pcg import drawer as base_drawer
from pcg.grids import square as square_grid

from pcg.filters import *
from pcg.aggregators import *


############
# properties
############

class PROPERTY_GROUP(enum.Enum):
    TERRAIN = 1


node_fabric = nodes.Fabric()

TEST = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
GRASS = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
WATER = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
SAND = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
FOREST = node_fabric.Property(PROPERTY_GROUP.TERRAIN)


############
# visualizer
############

drawer = square_grid.Drawer(cell_size=geometry.Point(10, 10),
                            duration=1000,
                            filename='./example.webp')

drawer.add_biome(base_drawer.Biome(checker=GRASS, sprite=square_grid.Sprite(colors.RGBA(0, 1, 0))))
drawer.add_biome(base_drawer.Biome(checker=WATER, sprite=square_grid.Sprite(colors.RGBA(0, 0, 1))))
drawer.add_biome(base_drawer.Biome(checker=SAND, sprite=square_grid.Sprite(colors.RGBA(1, 1, 0))))
drawer.add_biome(base_drawer.Biome(checker=FOREST, sprite=square_grid.Sprite(colors.RGBA(0, 0.5, 0))))
drawer.add_biome(base_drawer.Biome(checker=All(), sprite=square_grid.Sprite(colors.RGBA(0, 0, 0))))


###########
# generator
###########

topology = topologies.Topology(coordinates=square_grid.cells_rectangle(width=80, height=80))

space = Space(topology, recorders=[drawer])
space.initialize(node_fabric.Node(GRASS))


with space.step():
    for node in space.base(Fraction(0.01)):
        node <<= WATER

with space.step():
    for node in space.base(Fraction(0.80), GRASS):
        if square_grid.Euclidean(node, 1, 3).base(WATER) | Exists():
            node <<= WATER

with space.step():
    for node in space.base(GRASS):
        if square_grid.Ring(node).base(WATER) | Exists():
            node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(Fraction(0.1), GRASS):
            if square_grid.Ring(node).base(SAND) | Exists():
                node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(SAND):
            if square_grid.Ring(node).base(WATER) | Between(6, 10):
                node <<= WATER

with space.step():
    for node in space.base(Fraction(0.03), GRASS):
        node <<= FOREST

with space.step():
    for node in space.base(Fraction(0.1), GRASS):
        if (square_grid.Ring(node, 2).base(FOREST) and
            square_grid.Ring(node).actual(FOREST) | ~Exists()):
            node <<= FOREST


drawer.finish()
