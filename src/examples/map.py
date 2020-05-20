
import enum

from genme.nodes import *
from genme.drawer2d import *
from genme.filters import *
from genme.aggregators import *
from genme.topologies import *
from genme.colors import *
from genme.space import *
from genme.d2 import *


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

topology = Topology(coordinates=cells_square(width=WIDTH, height=HEIGHT))

space = Space(topology, store_history=True)
space.initialize(node_fabric.Node(GRASS))


with space.step():
    for node in space.base(Fraction(0.01)):
        node <<= WATER

with space.step():
    for node in space.base(Fraction(0.80), GRASS):
        if Euclidean(node, 1, 3).base(WATER) | Exists():
            node <<= WATER

with space.step():
    for node in space.base(GRASS):
        if SquareRadius(node).base(WATER) | Exists():
            node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(Fraction(0.1), GRASS):
            if SquareRadius(node).base(SAND) | Exists():
                node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(SAND):
            if SquareRadius(node).base(WATER) | Between(6, 10):
                node <<= WATER

with space.step():
    for node in space.base(Fraction(0.05), GRASS):
        node <<= FOREST

with space.step():
    for node in space.base(Fraction(0.2), GRASS):
        if (SquareRadius(node, 2).base(FOREST) and
            SquareRadius(node).actual(FOREST) | ~Exists()):
            node <<= FOREST


############
# visualizer
############

drawer = Drawer2D(cell_size=10)

drawer.add_biome(Biome(checker=GRASS, sprite=Sprite(RGBA(0, 1, 0))))
drawer.add_biome(Biome(checker=WATER, sprite=Sprite(RGBA(0, 0, 1))))
drawer.add_biome(Biome(checker=SAND, sprite=Sprite(RGBA(1, 1, 0))))
drawer.add_biome(Biome(checker=FOREST, sprite=Sprite(RGBA(0, 0.5, 0))))
drawer.add_biome(Biome(checker=All(), sprite=Sprite(RGBA(0, 0, 0))))

# canvas = drawer.draw(space.base(), width=WIDTH, height=HEIGHT)
# canvas.show()

drawer.save_history('./example.webp', space, width=WIDTH, height=HEIGHT)
