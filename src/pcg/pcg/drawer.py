
import typing
import dataclasses

from PIL import Image

from . import colors


@dataclasses.dataclass
class Biome:
    __slots__ = ('checker', 'sprite')
    checker: typing.Callable
    sprite: typing.Any


class Drawer:
    __slots__ = ('biomes', 'duration', 'frames', 'filename')

    def __init__(self, duration, filename):
        self.biomes = []
        self.duration = duration
        self.frames = []
        self.filename = filename

    def node_position(self, node, canvas_size):
        raise NotImplementedError()

    def prepair_sprite(self, sprite):
        raise NotImplementedError()

    def calculate_canvas_size(self, nodes):
        raise NotImplementedError()

    def add_biome(self, biome):
        self.prepair_sprite(biome.sprite)
        self.biomes.append(biome)

    def choose_biome(self, node):
        for biome in self.biomes:
            if biome.checker(node):
                return biome

    def draw(self, nodes):
        canvas_size = self.calculate_canvas_size(nodes)

        canvas = Image.new('RGBA',
                           canvas_size.xy,
                           colors.BLACK.ints)

        for node in nodes:
            biome = self.choose_biome(node)

            position = self.node_position(node, canvas_size).xy

            # TODO: round position correctly
            canvas.paste(biome.sprite.image,
                         (int(position[0]), int(position[1])),
                         biome.sprite.image)

        return canvas

    def record(self, space):
        canvas = self.draw(list(space.base()))
        self.frames.append(canvas)

    def finish(self):
        self.frames[0].save(self.filename,
                            lossles=True,
                            quality=100,
                            duration=self.duration,
                            save_all=True,
                            append_images=self.frames[1:])
