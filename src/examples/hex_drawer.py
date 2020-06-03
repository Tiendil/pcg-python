
import enum
import typing
import dataclasses

from PIL import Image
from PIL import ImageDraw

from genme import colors
from genme import map_hex
from genme import nodes
from genme import topologies

from genme.space import *
from genme.filters import *
from genme.aggregators import *


ALPHA = colors.RGBA(0, 0, 0, 0)
BLACK = colors.RGBA(0, 0, 0)


@dataclasses.dataclass
class Sprite:
    color: colors.Color = BLACK
    image: Image = dataclasses.field(default=None, init=False, compare=False)

    def prepair(self):
        sprite_size = map_hex.CELL_SIZE * cell_size

        self.image = Image.new('RGBA', sprite_size.round_up().xy, ALPHA.ints)

        center = sprite_size / 2

        cell = map_hex.Cell(0, 0, 0)

        draw = ImageDraw.Draw(self.image)

        draw.polygon([(center + point * cell_size).xy for point in map_hex.cell_corners(cell)],
                      fill=self.color.ints)


@dataclasses.dataclass
class Biome:
    __slots__ = ('checker', 'sprite')
    checker: typing.Callable
    sprite: Sprite


class DrawerHex:
    __slots__ = ('biomes', 'canvas_size', 'duration', 'frames', 'filename')

    def __init__(self, canvas_size, duration, filename):
        self.biomes = []
        self.canvas_size = canvas_size
        self.duration = duration
        self.frames = []
        self.filename = filename

    def add_biome(self, biome):
        biome.sprite.prepair()
        self.biomes.append(biome)

    def choose_biome(self, node):
        for biome in self.biomes:
            if biome.checker(node):
                return biome

    def draw(self, nodes):
        canvas = Image.new('RGBA',
                           self.canvas_size.xy,
                           BLACK.ints)

        center = self.canvas_size / 2

        for node in nodes:
            biome = self.choose_biome(node)

            position = (center + map_hex.cell_center(node.coordinates) * cell_size - cell_size / 2).xy

            # TODO: round position correctly
            canvas.paste(biome.sprite.image,
                         (int(position[0]), int(position[1])),
                         biome.sprite.image)

        return canvas

    def record(self, space):
        canvas = self.draw(space.base())
        self.frames.append(canvas)

    def finish(self):
        self.frames[0].save(self.filename,
                            lossles=True,
                            quality=100,
                            duration=self.duration,
                            save_all=True,
                            append_images=self.frames[1:] )


##############################
# map
##############################


cell_size = map_hex.Point(10, 10)

canvas_size = map_hex.Point(90 * cell_size.x,
                            90 * cell_size.y)


class PROPERTY_GROUP(enum.Enum):
    TERRAIN = 1


node_fabric = nodes.Fabric()

TEST = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
GRASS = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
WATER = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
SAND = node_fabric.Property(PROPERTY_GROUP.TERRAIN)
FOREST = node_fabric.Property(PROPERTY_GROUP.TERRAIN)

############
# visualizer
############

drawer = DrawerHex(canvas_size=canvas_size,
                   duration=1000,
                   filename='./example.webp')

drawer.add_biome(Biome(checker=GRASS, sprite=Sprite(colors.RGBA(0, 1, 0))))
drawer.add_biome(Biome(checker=WATER, sprite=Sprite(colors.RGBA(0, 0, 1))))
drawer.add_biome(Biome(checker=SAND, sprite=Sprite(colors.RGBA(1, 1, 0))))
drawer.add_biome(Biome(checker=FOREST, sprite=Sprite(colors.RGBA(0, 0.5, 0))))
drawer.add_biome(Biome(checker=All(), sprite=Sprite(colors.RGBA(0, 0, 0))))


###########
# generator
###########

topology = topologies.Topology(coordinates=map_hex.cells_hexagon(25))

space = Space(topology, recorders=[drawer])
space.initialize(node_fabric.Node(GRASS))


with space.step():
    for node in space.base(Fraction(0.01)):
        node <<= WATER

with space.step():
    for node in space.base(Fraction(0.80), GRASS):
        if map_hex.Euclidean(node, 1, 3).base(WATER) | Exists():
            node <<= WATER

with space.step():
    for node in space.base(GRASS):
        if map_hex.SquareRadius(node).base(WATER) | Exists():
            node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(Fraction(0.1), GRASS):
            if map_hex.SquareRadius(node).base(SAND) | Exists():
                node <<= SAND

for _ in range(3):
    with space.step():
        for node in space.base(SAND):
            if map_hex.SquareRadius(node).base(WATER) | Between(6, 10):
                node <<= WATER

with space.step():
    for node in space.base(Fraction(0.03), GRASS):
        node <<= FOREST

with space.step():
    for node in space.base(Fraction(0.1), GRASS):
        if (map_hex.SquareRadius(node, 2).base(FOREST) and
            map_hex.SquareRadius(node).actual(FOREST) | ~Exists()):
            node <<= FOREST


drawer.finish()
