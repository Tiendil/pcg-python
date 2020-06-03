
import enum

from genme import nodes
from genme import colors
from genme import geometry
from genme import topologies
from genme.space import Space
from genme import drawer as base_drawer
from genme.grids import hex as hex_grid

from genme.filters import *
from genme.aggregators import *


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

drawer = hex_grid.Drawer(cell_size=geometry.Point(10, 10),
                         duration=1000,
                         filename='./example.webp')

drawer.add_biome(base_drawer.Biome(checker=GRASS, sprite=hex_grid.Sprite(colors.RGBA(0, 1, 0))))
drawer.add_biome(base_drawer.Biome(checker=WATER, sprite=hex_grid.Sprite(colors.RGBA(0, 0, 1))))
drawer.add_biome(base_drawer.Biome(checker=SAND, sprite=hex_grid.Sprite(colors.RGBA(1, 1, 0))))
drawer.add_biome(base_drawer.Biome(checker=FOREST, sprite=hex_grid.Sprite(colors.RGBA(0, 0.5, 0))))
drawer.add_biome(base_drawer.Biome(checker=All(), sprite=hex_grid.Sprite(colors.RGBA(0, 0, 0))))


###########
# generator
###########

topology = topologies.Topology(coordinates=hex_grid.cells_hexagon(25))

space = Space(topology, recorders=[drawer])
space.initialize(node_fabric.Node(GRASS))


with space.step():
    for node in space.base(Fraction(0.01)):
        node <<= WATER

with space.step():
    for node in space.base(Fraction(0.80), GRASS):
        if hex_grid.Euclidean(node, 1, 3).base(WATER) | Exists():
            node <<= WATER

with space.step():
    for node in space.base(GRASS):
        if hex_grid.Ring(node).base(WATER) | Exists():
            node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(Fraction(0.1), GRASS):
            if hex_grid.Ring(node).base(SAND) | Exists():
                node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(SAND):
            if hex_grid.Ring(node).base(WATER) | Between(6, 10):
                node <<= WATER

with space.step():
    for node in space.base(Fraction(0.03), GRASS):
        node <<= FOREST

with space.step():
    for node in space.base(Fraction(0.1), GRASS):
        if (hex_grid.Ring(node, 2).base(FOREST) and
            hex_grid.Ring(node).actual(FOREST) | ~Exists()):
            node <<= FOREST


drawer.finish()
