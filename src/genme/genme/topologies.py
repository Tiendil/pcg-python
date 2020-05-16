import math
import dataclasses


@dataclasses.dataclass(frozen=True)
class XY:
    __slots__ = ('x', 'y')

    x: int
    y: int

    def xy(self):
        return self.x, self.y

    def move(self, dx, dy):
        return XY(self.x + dx, self.y + dy)


class BaseArea:
    __slots__ = ('world', 'center', 'min_distance', 'max_distance')

    _CACHE = {}

    def __init__(self, node, min_distance, max_distance=None):
        if max_distance is None:
            max_distance = min_distance

        self.world = node.world
        self.center = node.coordinates
        self.min_distance = min_distance
        self.max_distance = max_distance

    def nodes(self, *filters, include=False):
        for point in self._template(self.min_distance, self.max_distance):
            if point == self.center and not include:
                continue

            coordinates = self.center.move(point.x, point.y)

            node = self.world[coordinates]

            if node is None:
                continue

            if all(filter(node) for filter in filters):
                yield node

    @classmethod
    def _template(cls, min_distance, max_distance):
        key = (min_distance, max_distance)

        if key in cls._CACHE:
            return cls._CACHE[key]

        area = set()

        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):

                point = XY(dx, dy)

                if min_distance <= cls.distance(point) <= max_distance:
                    area.add(point)

        cls._CACHE[key] = area

        return area


class Euclidean(BaseArea):
    __slots__ = ()

    @classmethod
    def distance(self, a, b=XY(0, 0)):
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)



class Manhattan(BaseArea):
    __slots__ = ()

    @classmethod
    def distance(self, a, b=XY(0, 0)):
        return abs(a.x-b.x) + abs(a.y-b.y)


class SquareRadius(BaseArea):
    __slots__ = ()

    _CACHE = {}

    @classmethod
    def distance(self, a, b=XY(0, 0)):
        return max(abs(a.x-b.x), abs(a.y-b.y))
