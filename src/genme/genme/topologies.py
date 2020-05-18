import math
import dataclasses


@dataclasses.dataclass(frozen=True, order=True)
class XY:
    __slots__ = ('x', 'y')

    x: int
    y: int

    def xy(self):
        return self.x, self.y

    def move(self, dx, dy):
        return XY(self.x + dx, self.y + dy)


def cells_square(width, height):
    for y in range(height):
        for x in range(width):
            yield XY(x, y)


class BaseArea:
    __slots__ = ('space', 'center', 'min_distance', 'max_distance', 'include')

    _TEMPLATE_CACHE = NotImplemented
    _CACHE = NotImplemented

    def __init__(self, node, min_distance=1, max_distance=None, include=False):
        if max_distance is None:
            max_distance = min_distance

        self.space = node.space
        self.center = node.coordinates
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.include = include

    def base(self):
        for point in self.coordinates():
            yield self.space.base_node(point)

    def new(self):
        for point in self.coordinates():
            yield self.space.new_node(point)

    def actual(self):
        for point in self.coordinates():
            yield self.space.actual_node(point)

    def coordinates(self):
        key = (self.center, self.min_distance, self.max_distance, self.include)

        if key in self._CACHE:
            return self._CACHE[key]

        coordinates = []

        for point in self._template(self.min_distance, self.max_distance):
            if point == self.center and not self.include:
                continue

            real_point = self.center.move(*point.xy)

            if not self.space.has_node(real_point):
                continue

            coordinates.append(real_point)

        self._CACHE[key] = coordinates

        return coordinates

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
