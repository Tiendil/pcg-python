
import math
import dataclasses

from .topologies import BaseArea


@dataclasses.dataclass(frozen=True, order=True)
class XY:
    __slots__ = ('x', 'y')

    x: int
    y: int

    @property
    def xy(self):
        return self.x, self.y

    def move(self, dx, dy):
        return XY(self.x + dx, self.y + dy)


def cells_square(width, height):
    for y in range(height):
        for x in range(width):
            yield XY(x, y)


def area_template(min_distance, max_distance, distance):
    area = []

    for dx in range(-max_distance, max_distance + 1):
        for dy in range(-max_distance, max_distance + 1):

            point = XY(dx, dy)

            if min_distance <= distance(point) <= max_distance:
                area.append(point)

    return area


def area(topology, distance, min_distance, max_distance):
    cache = [None] * topology.size()

    template = area_template(min_distance, max_distance, distance)

    for center, index in topology.indexes.items():
        points = [center.move(*point.xy) for point in template]
        cache[index] = topology.area_indexes(points)

    return cache



class Euclidean(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=XY(0, 0)):
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)


class Manhattan(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=XY(0, 0)):
        return abs(a.x-b.x) + abs(a.y-b.y)


class SquareRadius(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=XY(0, 0)):
        return max(abs(a.x-b.x), abs(a.y-b.y))
