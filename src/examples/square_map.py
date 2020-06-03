
import enum

from genme.nodes import *
from genme.filters import *
from genme.aggregators import *
from genme.topologies import *
from genme.colors import *
from genme.space import *

from genme import drawer as base_drawer
from genme.grids import square as square_grid
from genme import geometry


WIDTH = 80
HEIGHT = 80


class PROPERTY_GROUP(enum.Enum):
    TERRAIN = 1


node_fabric = Fabric()

TEST = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
GRASS = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
WATER = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
SAND = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
FOREST = node_fabric.Property(PROPERTY_GROUP.TERRAIN)

############
# visualizer
############

cell_size = geometry.Point(10, 10)

canvas_size = geometry.Point(WIDTH * cell_size.x,
                             HEIGHT * cell_size.y)

drawer = square_grid.Drawer(canvas_size=canvas_size,
                            cell_size=cell_size,
                            duration=1000,
                            filename='./example.webp')

drawer.add_biome(base_drawer.Biome(checker=GRASS, sprite=square_grid.Sprite(RGBA(0, 1, 0))))
drawer.add_biome(base_drawer.Biome(checker=WATER, sprite=square_grid.Sprite(RGBA(0, 0, 1))))
drawer.add_biome(base_drawer.Biome(checker=SAND, sprite=square_grid.Sprite(RGBA(1, 1, 0))))
drawer.add_biome(base_drawer.Biome(checker=FOREST, sprite=square_grid.Sprite(RGBA(0, 0.5, 0))))
drawer.add_biome(base_drawer.Biome(checker=All(), sprite=square_grid.Sprite(RGBA(0, 0, 0))))


###########
# generator
###########

topology = Topology(coordinates=square_grid.cells_rectangle(width=WIDTH, height=HEIGHT))

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
        if square_grid.SquareRadius(node).base(WATER) | Exists():
            node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(Fraction(0.1), GRASS):
            if square_grid.SquareRadius(node).base(SAND) | Exists():
                node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(SAND):
            if square_grid.SquareRadius(node).base(WATER) | Between(6, 10):
                node <<= WATER

with space.step():
    for node in space.base(Fraction(0.03), GRASS):
        node <<= FOREST

with space.step():
    for node in space.base(Fraction(0.1), GRASS):
        if (square_grid.SquareRadius(node, 2).base(FOREST) and
            square_grid.SquareRadius(node).actual(FOREST) | ~Exists()):
            node <<= FOREST


drawer.finish()
