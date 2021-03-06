
import enum

from pcg.nodes import *
from pcg.filters import *
from pcg.aggregators import *
from pcg.topologies import *
from pcg.colors import *
from pcg.space import *

from pcg import drawer as base_drawer
from pcg.grids import square as square_grid
from pcg import geometry


STEPS = 100
WIDTH = 80
HEIGHT = 80


class PROPERTY_GROUP(enum.Enum):
    STATE = 1


node_fabric = Fabric()

DEAD = node_fabric.Property(PROPERTY_GROUP.STATE)
ALIVE = node_fabric.Property(PROPERTY_GROUP.STATE)


############
# visualizer
############

drawer = square_grid.Drawer(cell_size=geometry.Point(5, 5),
                            duration=100,
                            filename='./example.webp')

drawer.add_biome(base_drawer.Biome(checker=ALIVE, sprite=square_grid.Sprite(RGBA(1, 1, 1))))
drawer.add_biome(base_drawer.Biome(checker=DEAD, sprite=square_grid.Sprite(RGBA(0, 0, 0))))
drawer.add_biome(base_drawer.Biome(checker=All(), sprite=square_grid.Sprite(RGBA(0, 0, 0))))


###########
# generator
###########

topology = Topology(coordinates=square_grid.cells_rectangle(width=WIDTH, height=HEIGHT))

space = Space(topology, recorders=[drawer])
space.initialize(node_fabric.Node(DEAD))


#########################################
# warm up for better performance analisis
# for node in space.base(ALIVE):
#     list(SquareRadius(node).base(ALIVE))
#########################################

with space.step():
    for node in space.base(Fraction(0.2)):
        node <<= ALIVE

for i in range(STEPS):
    print(f'step {i+1}/{STEPS}')

    with space.step():
        for node in space.base(ALIVE):
            if square_grid.Ring(node).base(ALIVE) | ~Between(2, 3):
                node <<= DEAD

        for node in space.base(DEAD):
            if square_grid.Ring(node).base(ALIVE) | Count(3):
                node <<= ALIVE


drawer.finish()
