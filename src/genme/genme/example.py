
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


world = World2D(width=80, height=80, base_node=base_node)


with world.step() as nodes:
    for node in nodes(Fraction(0.02)):
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
    for node in nodes(Fraction(0.25), Marked(TERRAIN.GRASS)):
        node.mark(TERRAIN.FOREST)


############
# visualizer
############


from PIL import Image, ImageDraw

CELL_SIZE = 10


canvas = Image.new('RGBA',
                   (world.width * CELL_SIZE, world.height * CELL_SIZE),
                   (255,255,255,0))

drawer = ImageDraw.Draw(canvas)

for node in world.nodes():
    color = None

    if node.has_mark(TERRAIN.GRASS):
        color = (0, 255, 0)
    elif node.has_mark(TERRAIN.WATER):
        color = (0, 0, 255)
    elif node.has_mark(TERRAIN.SAND):
        color = (0, 127, 127)
    elif node.has_mark(TERRAIN.FOREST):
        color = (127, 255, 127)

    x, y = node.coordinates.xy()

    drawer.rectangle(((x * CELL_SIZE, y * CELL_SIZE),
                      ((x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE)),
                     fill=color)


canvas.show()
