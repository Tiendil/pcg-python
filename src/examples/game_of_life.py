
import enum

from genme.nodes import *
from genme.drawer2d import *
from genme.filters import *
from genme.topologies import *
from genme.colors import *
from genme.space import *


class CELL_STATE(enum.Enum):
    DEAD = 0
    ALIVE = 1


STEPS = 1000
DURATION = 100
WIDTH = 80
HEIGHT = 80

space = Space(store_history=True)
space.initialize(Node(), cells_square(width=WIDTH, height=HEIGHT))


with space.step():
    for node in space.base():
        node.mark(CELL_STATE.DEAD)

with space.step():
    for node in space.base(Fraction(0.2)):
        node.mark(CELL_STATE.ALIVE)

for i in range(STEPS):
    print(f'step {i}/{STEPS}')

    with space.step():
        for node in space.base(Marked(CELL_STATE.ALIVE)):
            if SquareRadius(node, 1).base(Marked(CELL_STATE.ALIVE)) >> Between(0, 1):
                node.mark(CELL_STATE.DEAD)
            if SquareRadius(node, 1).base(Marked(CELL_STATE.ALIVE)) >> Between(4, 100):
                node.mark(CELL_STATE.DEAD)

        for node in space.base(Marked(CELL_STATE.DEAD)):
            if SquareRadius(node, 1).base(Marked(CELL_STATE.ALIVE)) >> Count(3):
                node.mark(CELL_STATE.ALIVE)

############
# visualizer
############

drawer = Drawer2D(cell_size=10)

drawer.add_biome(Biome(checker=Marked(CELL_STATE.ALIVE), sprite=Sprite(RGBA(1, 1, 1))))
drawer.add_biome(Biome(checker=Marked(CELL_STATE.DEAD), sprite=Sprite(RGBA(0, 0, 0))))
drawer.add_biome(Biome(checker=All(), sprite=Sprite(RGBA(0, 0, 0))))

drawer.save_history('./example.webp', space, width=WIDTH, height=HEIGHT, duration=DURATION)
