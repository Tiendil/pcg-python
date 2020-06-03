
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
    __slots__ = ('biomes', 'canvas_size', 'duration', 'frames', 'filename')

    def __init__(self, canvas_size, duration, filename):
        self.biomes = []
        self.canvas_size = canvas_size
        self.duration = duration
        self.frames = []
        self.filename = filename

    def node_position(self, node):
        raise NotImplementedError()

    def prepair_sprite(self, sprite):
        raise NotImplementedError()

    def add_biome(self, biome):
        self.prepair_sprite(biome.sprite)
        self.biomes.append(biome)

    def choose_biome(self, node):
        for biome in self.biomes:
            if biome.checker(node):
                return biome

    def draw(self, nodes):
        canvas = Image.new('RGBA',
                           self.canvas_size.xy,
                           colors.BLACK.ints)

        for node in nodes:
            biome = self.choose_biome(node)

            position = self.node_position(node).xy

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
                            append_images=self.frames[1:])
