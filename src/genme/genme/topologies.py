import math
import dataclasses


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


class Topology:
    __slots__ = ('_cache', 'distance')

    def __init__(self, distance):
        self._cache = {}
        self.distance = distance

    def cache(self, space, min_distance, max_distance):
        key = (min_distance, max_distance)

        if key in self._cache:
            return self._cache[key]

        cache = [None] * space.size()

        template = self.area_template(min_distance, max_distance)

        for center, index in space.coordinates_to_indexes.items():
            points = [center.move(*point.xy) for point in template]
            cache[index] = space.area_indexes(points)

        self._cache[key] = cache

        return cache

    def area_template(self, min_distance, max_distance):
        area = []

        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):

                point = XY(dx, dy)

                if min_distance <= self.distance(point) <= max_distance:
                    area.append(point)

        return area


class BaseArea:
    __slots__ = ('space', 'indexes')

    TOPOLOGY = NotImplemented

    def __init__(self, node, min_distance=1, max_distance=None):
        if max_distance is None:
            max_distance = min_distance

        self.space = node.space

        self.indexes = self.TOPOLOGY.cache(self.space, min_distance, max_distance)[node.index]

    def base(self, *filters):
        return self.space.base(*filters, indexes=self.indexes)

    def new(self, *filters):
        return self.space.new(*filters, indexes=self.indexes)

    def actual(self, *filters):
        return self.space.actual(*filters, indexes=self.indexes)


class Euclidean(BaseArea):
    __slots__ = ()
    TOPOLOGY = Topology(lambda a, b=XY(0, 0): math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2))


class Manhattan(BaseArea):
    __slots__ = ()
    TOPOLOGY = Topology(lambda a, b=XY(0, 0): (a.x-b.x) + abs(a.y-b.y))


class SquareRadius(BaseArea):
    __slots__ = ()
    TOPOLOGY = Topology(lambda a, b=XY(0, 0): max(abs(a.x-b.x), abs(a.y-b.y)))
