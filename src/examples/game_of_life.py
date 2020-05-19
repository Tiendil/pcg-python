
import enum

from genme.nodes import *
from genme.drawer2d import *
from genme.filters import *
from genme.aggregators import *
from genme.topologies import *
from genme.colors import *
from genme.space import *


STEPS = 100
DURATION = 100
WIDTH = 80
HEIGHT = 80


class PROPERTY_GROUP(enum.Enum):
    STATE = 1


node_fabric = Fabric()

DEAD = node_fabric.Property(PROPERTY_GROUP.STATE)
ALIVE = node_fabric.Property(PROPERTY_GROUP.STATE)

base_node = node_fabric.Node(DEAD)

space = Space(store_history=True)
space.initialize(base_node, cells_square(width=WIDTH, height=HEIGHT))


with space.step():
    for node in space.base(Fraction(0.2)):
        node <<= ALIVE

#########################################
# warm up for better performance analisis
# for node in space.base(ALIVE):
#     list(SquareRadius(node).base(ALIVE))
#########################################

for i in range(STEPS):
    print(f'step {i+1}/{STEPS}')

    with space.step():
        for node in space.base(ALIVE):
            if SquareRadius(node).base(ALIVE) | ~Between(2, 3):
                node <<= DEAD

        for node in space.base(DEAD):
            if SquareRadius(node).base(ALIVE) | Count(3):
                node <<= ALIVE

############
# visualizer
############

drawer = Drawer2D(cell_size=5)

drawer.add_biome(Biome(checker=ALIVE, sprite=Sprite(RGBA(1, 1, 1))))
drawer.add_biome(Biome(checker=DEAD, sprite=Sprite(RGBA(0, 0, 0))))
drawer.add_biome(Biome(checker=All(), sprite=Sprite(RGBA(0, 0, 0))))

drawer.save_history('./example.webp', space, width=WIDTH, height=HEIGHT, duration=DURATION)
