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


class BaseArea:
    __slots__ = ('space', 'indexes', 'min_distance', 'max_distance')

    _TEMPLATE_CACHE = NotImplemented
    _CACHE = NotImplemented

    def __init__(self, node, min_distance=1, max_distance=None):
        if max_distance is None:
            max_distance = min_distance

        self.space = node.space
        self.min_distance = min_distance
        self.max_distance = max_distance

        self.indexes = self.get_cache()[node.index]

    def get_cache(self):
        key = (self.min_distance, self.max_distance)

        if key in self._CACHE:
            return self._CACHE[key]

        cache = [None] * self.space.size()

        for coordinates, index in self.space.coordinates_to_indexes.items():
            cache[index] = self._get_indexes(coordinates)

        self._CACHE[key] = cache

        return cache

    def _get_indexes(self, center):
        indexes = []

        for point in self._template(self.min_distance, self.max_distance):
            real_point = center.move(*point.xy)

            index = self.space.coordinates_to_indexes.get(real_point)

            if index is None:
                continue

            indexes.append(index)

        return tuple(indexes)

    @classmethod
    def _template(cls, min_distance, max_distance):
        key = (min_distance, max_distance)

        if key in cls._TEMPLATE_CACHE:
            return cls._TEMPLATE_CACHE[key]

        area = set()

        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):

                point = XY(dx, dy)

                if min_distance <= cls.distance(point) <= max_distance:
                    area.add(point)

        cls._TEMPLATE_CACHE[key] = area

        return area

    def base(self, *filters):
        return self.space.base(*filters, indexes=self.indexes)

    def new(self, *filters):
        return self.space.new(*filters, indexes=self.indexes)

    def actual(self, *filters):
        return self.space.actual(*filters, indexes=self.indexes)


class Euclidean(BaseArea):
    __slots__ = ()
    _TEMPLATE_CACHE = {}
    _CACHE = {}

    @classmethod
    def distance(self, a, b=XY(0, 0)):
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)


class Manhattan(BaseArea):
    __slots__ = ()
    _TEMPLATE_CACHE = {}
    _CACHE = {}

    @classmethod
    def distance(self, a, b=XY(0, 0)):
        return abs(a.x-b.x) + abs(a.y-b.y)


class SquareRadius(BaseArea):
    __slots__ = ()
    _TEMPLATE_CACHE = {}
    _CACHE = {}

    @classmethod
    def distance(self, a, b=XY(0, 0)):
        return max(abs(a.x-b.x), abs(a.y-b.y))
