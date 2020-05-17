
import enum

from genme.nodes import *
from genme.drawer2d import *
from genme.filters import *
from genme.topologies import *
from genme.colors import *
from genme.space import *


class TERRAIN(enum.Enum):
    TEST = 0
    GRASS = 1
    WATER = 2
    SAND = 3
    FOREST = 4


WIDTH = 80
HEIGHT = 80

space = Space(store_history=True)
space.initialize(Node(), cells_square(width=WIDTH, height=HEIGHT))


with space.step():
    for node in space.base():
        node.mark(TERRAIN.GRASS)

with space.step():
    for node in space.base(Fraction(0.01)):
        node.mark(TERRAIN.WATER)

with space.step():
    for node in space.base(Fraction(0.80), Marked(TERRAIN.GRASS)):
        if Euclidean(node, 1, 3).base(Marked(TERRAIN.WATER)) >> Exist():
            node.mark(TERRAIN.WATER)

with space.step():
    for node in space.base(Marked(TERRAIN.GRASS)):
        if SquareRadius(node, 1).base(Marked(TERRAIN.WATER)) >> Exist():
            node.mark(TERRAIN.SAND)

for _ in range(3):
    with space.step():
        for node in space.base(Fraction(0.1), Marked(TERRAIN.GRASS)):
            if SquareRadius(node, 1).base(Marked(TERRAIN.SAND)) >> Exist():
                node.mark(TERRAIN.SAND)

for _ in range(3):
    with space.step():
        for node in space.base(Marked(TERRAIN.SAND)):
            if SquareRadius(node, 1).base(Marked(TERRAIN.WATER)) >> Between(6, 10):
                node.mark(TERRAIN.WATER)

with space.step():
    for node in space.base(Fraction(0.05), Marked(TERRAIN.GRASS)):
        node.mark(TERRAIN.FOREST)

with space.step():
    for node in space.base(Fraction(0.4), Marked(TERRAIN.GRASS)):
        if (SquareRadius(node, 2).base(Marked(TERRAIN.FOREST)) >> Exist() and
            SquareRadius(node, 1).actual(Marked(TERRAIN.FOREST)) >> ~Exist()):
            node.mark(TERRAIN.FOREST)


############
# visualizer
############

drawer = Drawer2D(cell_size=10)

drawer.add_biome(Biome(checker=Marked(TERRAIN.GRASS), sprite=Sprite(RGBA(0, 1, 0))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.WATER), sprite=Sprite(RGBA(0, 0, 1))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.SAND), sprite=Sprite(RGBA(1, 1, 0))))
drawer.add_biome(Biome(checker=Marked(TERRAIN.FOREST), sprite=Sprite(RGBA(0, 0.5, 0))))
drawer.add_biome(Biome(checker=All(), sprite=Sprite(RGBA(0, 0, 0))))

# canvas = drawer.draw(space.base(), width=WIDTH, height=HEIGHT)
# canvas.show()

drawer.save_history('./example.webp', space, width=WIDTH, height=HEIGHT)
