
import enum
import math
import random
import contextlib
import dataclasses


##############
# Base classes
##############

class OPERATION(enum.Enum):
    ADD_TAG = 1
    REMOVE_TAG = 2
    COUNT = 3
    SET_MARKER = 4
    UNSET_MARKER = 5


class Node:
    __slots__ = ('world', 'coordinates', 'tags', 'counters', 'markers', 'operations')

    def __init__(self):
        self.world = None
        self.coordinates = None
        self.tags = set()
        self.counters = {}
        self.markers = {}
        self.operations = []

    def clone(self):
        clone = Node()
        clone.world = self.world
        clone.coordinates = self.coordinates
        clone.tags |= set(self.tags)
        clone.counters.update(self.counters)
        clone.markers.update(self.markers)

        return clone

    def apply_changes(self):
        for operation, key in self.operations:
            if operation == OPERATION.ADD_TAG:
                self.tags.add(key)
            elif operation == OPERATION.REMOVE_TAG:
                if key in self.tags:
                    self.tags.remove(key)
            elif operation == OPERATION.COUNT:
                self.counters[key[0]] += key[1]
            elif operation == OPERATION.SET_MARKER:
                self.markers[key.__class__] = key
            else:
                raise NotImplementedError(f'unknown operation {operation}: {key}, {value}')

        self.operations[:] = ()

    def mark(self, marker):
        self.operations.append((OPERATION.SET_MARKER, marker))

    def tag(self, tag):
        self.operations.append((OPERATION.ADD_TAG, tag))

    def untag(self, tag):
        self.operations.append((OPERATION.REMOVE_TAG, tag))

    def count(self, counter, value):
        self.operations.append((OPERATION.COUNT, (counter, value)))

    def has_mark(self, marker):
        return self.markers.get(marker.__class__) == marker


@dataclasses.dataclass(frozen=True)
class XY:
    __slots__ = ('x', 'y')

    x: int
    y: int

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


class Fraction:
    __slots__ = ('fraction',)

    def __init__(self, fraction):
        self.fraction = fraction

    def __call__(self, node):
        return (random.random() < self.fraction)


class Marked:
    __slots__ = ('marker',)

    def __init__(self, marker):
        self.marker = marker

    def __call__(self, node):
        return node.has_mark(self.marker)


class Count:
    __slots__ = ('number',)

    def __init__(self, number):
        self.number = number

    def __rrshift__(self, other):
        return len(list(other)) == self.number


class Exist:
    __slots__ = ()

    def __rrshift__(self, other):
        return 0 < len(list(other))


class World2D:
    __slots__ = ('width', 'height', 'map')

    def __init__(self, width, height, base_node):
        self.width = width
        self.height = height
        self.map = []

        self._fill_map()

    def _fill_map(self):

        for y in range(self.height):
            row = []

            for x in range(self.width):
                node = base_node.clone()
                node.world = self
                node.coordinates = XY(x, y)
                row.append(node)

            self.map.append(row)

    def __getitem__(self, point):
        if (0 <= point.x < self.width) and (0 <= point.y < self.height):
            return self.map[point.y][point.x]

        return None

    def nodes(self, *filters):
        for row in self.map:
            for node in row:
                if all(filter(node) for filter in filters):
                    yield node

    @contextlib.contextmanager
    def step(self):

        yield self.nodes

        for node in self.nodes():
            node.apply_changes()


###########
# generator
###########

class TERRAIN(enum.Enum):
    GRASS = 1
    WATER = 2
    SAND = 3
    FOREST = 4


base_node = Node()
base_node.mark(TERRAIN.GRASS)
base_node.apply_changes()


world = World2D(width=80, height=20, base_node=base_node)


with world.step() as nodes:
    for node in nodes(Fraction(0.02)):
        node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Fraction(0.70), Marked(TERRAIN.GRASS)):
        if Euclidean(node, 1, 2).nodes(Marked(TERRAIN.WATER)) >> Count(1):
            node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Marked(TERRAIN.GRASS)):
        if SquareRadius(node, 1).nodes(Marked(TERRAIN.WATER)) >> Exist():
            node.mark(TERRAIN.SAND)

for _ in range(3):
    with world.step() as nodes:
        for node in nodes(Fraction(0.1), Marked(TERRAIN.GRASS)):
            if SquareRadius(node, 1).nodes(Marked(TERRAIN.SAND)) >> Exist():
                node.mark(TERRAIN.SAND)

with world.step() as nodes:
    for node in nodes(Fraction(0.25), Marked(TERRAIN.GRASS)):
        node.mark(TERRAIN.FOREST)


############
# visualizer
############


for row in world.map:
    line = []
    for node in row:
        if node.has_mark(TERRAIN.GRASS):
            line.append(' ')
        elif node.has_mark(TERRAIN.WATER):
            line.append('~')
        elif node.has_mark(TERRAIN.SAND):
            line.append('.')
        elif node.has_mark(TERRAIN.FOREST):
            line.append('f')

    print(''.join(line))
