
import enum

from genme.nodes import *
from genme.filters import *
from genme.aggregators import *
from genme.topologies import *
from genme.colors import *
from genme.space import *

from genme import drawer as base_drawer
from genme.grids import hex as hex_grid
from genme import geometry


STEPS = 100
WIDTH = 25
HEIGHT = 25


class PROPERTY_GROUP(enum.Enum):
    STATE = 1


node_fabric = Fabric()

DEAD = node_fabric.Property(PROPERTY_GROUP.STATE)
ALIVE = node_fabric.Property(PROPERTY_GROUP.STATE)


############
# visualizer
############

cell_size = geometry.Point(10, 10)

canvas_size = geometry.Point(90 * cell_size.x,
                             90 * cell_size.y)

drawer = hex_grid.Drawer(cell_size=cell_size,
                         canvas_size=canvas_size,
                         duration=100,
                         filename='./example.webp')

drawer.add_biome(base_drawer.Biome(checker=ALIVE, sprite=hex_grid.Sprite(RGBA(1, 1, 1))))
drawer.add_biome(base_drawer.Biome(checker=DEAD, sprite=hex_grid.Sprite(RGBA(0, 0, 0))))
drawer.add_biome(base_drawer.Biome(checker=All(), sprite=hex_grid.Sprite(RGBA(0, 0, 0))))


###########
# generator
###########

topology = Topology(coordinates=hex_grid.cells_hexagon(25))

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
            if hex_grid.SquareRadius(node).base(ALIVE) | ~Between(2, 3):
                node <<= DEAD

        for node in space.base(DEAD):
            if hex_grid.SquareRadius(node).base(ALIVE) | Count(3):
                node <<= ALIVE


drawer.finish()
