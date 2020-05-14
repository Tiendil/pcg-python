
import enum

from .nodes import *
from .world2d import *
from .filters import *
from .topologies import *


class TERRAIN(enum.Enum):
    GRASS = 1
    WATER = 2
    SAND = 3
    FOREST = 4


base_node = Node()
base_node.mark(TERRAIN.GRASS)
base_node.apply_changes()


world = World2D(width=80, height=20, base_node=base_node)


with world.step() as nodes:
    for node in nodes(Fraction(0.02)):
        node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Fraction(0.70), Marked(TERRAIN.GRASS)):
        if Euclidean(node, 1, 2).nodes(Marked(TERRAIN.WATER)) >> Count(1):
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

with world.step() as nodes:
    for node in nodes(Fraction(0.25), Marked(TERRAIN.GRASS)):
        node.mark(TERRAIN.FOREST)


############
# visualizer
############


for row in world.map:
    line = []
    for node in row:
        if node.has_mark(TERRAIN.GRASS):
            line.append(' ')
        elif node.has_mark(TERRAIN.WATER):
            line.append('~')
        elif node.has_mark(TERRAIN.SAND):
            line.append('.')
        elif node.has_mark(TERRAIN.FOREST):
            line.append('f')

    print(''.join(line))
