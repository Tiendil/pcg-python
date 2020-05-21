
import typing
import dataclasses

from PIL import Image

from . import colors

BLACK = colors.RGBA(0, 0, 0)


@dataclasses.dataclass
class Sprite:
    color: colors.Color = BLACK
    image: Image = dataclasses.field(default=None, init=False, compare=False)

    def prepair(self, size):
        self.image = Image.new('RGBA', (size, size), self.color.ints)


@dataclasses.dataclass
class Biome:
    __slots__ = ('checker', 'sprite')
    checker: typing.Callable
    sprite: Sprite


class Drawer2D:
    __slots__ = ('biomes', 'cell_size', 'width', 'height', 'duration', 'frames', 'filename')

    def __init__(self, cell_size, width, height, duration, filename):
        self.biomes = []
        self.cell_size = cell_size
        self.width = width
        self.height = height
        self.duration = duration
        self.frames = []
        self.filename = filename

    def add_biome(self, biome):
        biome.sprite.prepair(self.cell_size)
        self.biomes.append(biome)

    def choose_biome(self, node):
        for biome in self.biomes:
            if biome.checker(node):
                return biome

    def draw(self, nodes, width, height):
        canvas = Image.new('RGBA',
                           (width * self.cell_size,
                            height * self.cell_size),
                           BLACK.ints)

        for node in nodes:
            biome = self.choose_biome(node)

            x, y = node.coordinates.xy

            canvas.paste(biome.sprite.image,
                         (x * self.cell_size, y * self.cell_size))

        return canvas

    def record(self, space):
        canvas = self.draw(space.base(), width=self.width, height=self.height)
        self.frames.append(canvas)

    def finish(self):
        self.frames[0].save(self.filename,
                            lossles=True,
                            quality=100,
                            duration=self.duration,
                            save_all=True,
                            append_images=self.frames[1:] )
