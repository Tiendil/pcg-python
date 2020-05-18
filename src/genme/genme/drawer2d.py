
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
    __slots__ = ('biomes', 'cell_size')

    def __init__(self, cell_size):
        self.biomes = []
        self.cell_size = cell_size

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

    def save_history(self, filename, space, width, height, duration=1000):
        images = []

        for history in space._history:
            canvas = self.draw(history, width=width, height=height)
            images.append(canvas)

        images[0].save(filename,
                       lossles=True,
                       quality=100,
                       duration=duration,
                       save_all=True,
                       append_images=images[1:])
