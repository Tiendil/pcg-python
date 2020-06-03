import math
import dataclasses

from PIL import Image

from genme import colors
from genme import drawer
from genme.topologies import BaseArea
from genme.geometry import Point


@dataclasses.dataclass(frozen=True, order=True)
class Cell:
    __slots__ = ('x', 'y')

    x: int
    y: int

    def __add__(self, cell: 'Cell'):
        return Cell(self.x + cell.x,
                    self.y + cell.y)

    def __sub__(self, cell: 'Cell'):
        return Cell(self.x - cell.y,
                    self.y - cell.y)

    def scale(self, scale: float):
        return Cell(self.x * scale,
                    self.y * scale)

    # def neighbour(self, i):
    #     return self + DIRECTIONS[i % 6]

    # def neighbours(self):
    #     return [self + DIRECTIONS[i] for i in range(6)]


def cells_rectangle(width, height):
    for y in range(height):
        for x in range(width):
            yield Cell(x, y)


def cell_center(cell):
    return Point(cell.x + 0.5, cell.y + 0.5)


def area_template(min_distance, max_distance, distance):
    area = []

    for dx in range(-max_distance, max_distance + 1):
        for dy in range(-max_distance, max_distance + 1):

            cell = Cell(dx, dy)

            if min_distance <= distance(cell) <= max_distance:
                area.append(cell)

    return area


def area(topology, distance, min_distance, max_distance):
    cache = [None] * topology.size()

    template = area_template(min_distance, max_distance, distance)

    for center, index in topology.indexes.items():
        points = [center + point for point in template]
        cache[index] = topology.area_indexes(points)

    return cache


class Euclidean(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=Cell(0, 0)):
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)


class Manhattan(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=Cell(0, 0)):
        return abs(a.x-b.x) + abs(a.y-b.y)


class SquareRadius(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=Cell(0, 0)):
        return max(abs(a.x-b.x), abs(a.y-b.y))


################################
# drawers
################################

@dataclasses.dataclass
class Sprite:
    color: colors.Color = colors.BLACK
    image: Image = dataclasses.field(default=None, init=False, compare=False)

    def prepair(self, cell_size):
        self.image = Image.new('RGBA', cell_size.xy, self.color.ints)


class Drawer(drawer.Drawer):
    __slots__ = ('cell_size',)

    def __init__(self, cell_size, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = cell_size

    def prepair_sprite(self, sprite):
        sprite.prepair(self.cell_size)

    def node_position(self, node):
        return cell_center(node.coordinates) * self.cell_size - self.cell_size / 2
