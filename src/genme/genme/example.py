
import enum

from .nodes import *
from .world2d import *
from .drawer2d import *
from .filters import *
from .topologies import *
from .colors import *


class TERRAIN(enum.Enum):
    TEST = 0
    GRASS = 1
    WATER = 2
    SAND = 3
    FOREST = 4


base_node = Node()
base_node.mark(TERRAIN.GRASS)
base_node.apply_changes()


world = World2D(width=80, height=80, base_node=base_node)


with world.step() as nodes:
    for node in nodes(Fraction(0.01)):
        node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Fraction(0.80), Marked(TERRAIN.GRASS)):
        if Euclidean(node, 1, 3).nodes(Marked(TERRAIN.WATER)) >> Exist():
            node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Marked(TERRAIN.GRASS)):
        if SquareRadius(node, 1).nodes(Marked(TERRAIN.WATER)) >> Exist():
            node.mark(TERRAIN.SAND)

for _ in range(3):
    with world.step() as nodes:
        for node in nodes(Fraction(0.1), Marked(TERRAIN.GRASS)):
            if SquareRadius(node, 1).nodes(Marked(TERRAIN.SAND)) >> Exist():
                node.mark(TERRAIN.SAND)

for _ in range(3):
    with world.step() as nodes:
        for node in nodes(Marked(TERRAIN.SAND)):
            if SquareRadius(node, 1).nodes(Marked(TERRAIN.WATER)) >> Between(6, 10):
                node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Fraction(0.05), Marked(TERRAIN.GRASS)):
        node.mark(TERRAIN.FOREST)

with world.step() as nodes:
    for _ in range(4):
        for node in nodes(Fraction(0.1), Marked(TERRAIN.GRASS)):
            if (SquareRadius(node, 2).nodes(Marked(TERRAIN.FOREST)) >> Exist() and
                SquareRadius(node, 1).nodes(Marked(TERRAIN.FOREST)) >> NotExist()):
                node.mark(TERRAIN.FOREST)


############
# visualizer
############

drawer = Drawer2D(cell_size=10)

drawer.add_biome(Biome(checker=Marked(TERRAIN.GRASS), sprite=Sprite(RGBA(0, 1, 0))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.WATER), sprite=Sprite(RGBA(0, 0, 1))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.SAND), sprite=Sprite(RGBA(1, 1, 0))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.FOREST), sprite=Sprite(RGBA(0, 0.5, 0))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.TEST), sprite=Sprite(RGBA(0, 0, 0))))

canvas = drawer.draw(world)

canvas.show()
