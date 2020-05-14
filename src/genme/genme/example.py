
import enum
import math
import random
import contextlib


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
    __slots__ = ('coordinates', 'tags', 'counters', 'markers', 'operations')

    def __init__(self):
        self.coordinates = None
        self.tags = set()
        self.counters = {}
        self.markers = {}
        self.operations = []

    def clone(self):
        clone = Node()
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


class XY:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def euclidean_distance(self, xy):
        return math.sqrt((self.x-xy.x)**2 + (self.y-xy.y)**2)

    def manhattan_distance(self, xy):
        return abs(self.x-xy.x) + abs(self.y-xy.y)


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


class Distance:
    __slots__ = ('method', 'min_distance', 'max_distance')

    def __init__(self, method, point, min_distance, max_distance=None):
        if max_distance is None:
            max_distance = min_distance

        self.method = getattr(point, f'{method}_distance')
        self.min_distance = min_distance
        self.max_distance = max_distance

    def __call__(self, node):
        return self.min_distance <= self.method(node.coordinates) <= self.max_distance


class Count:
    __slots__ = ('number',)

    def __init__(self, number):
        self.number = number

    def __rrshift__(self, other):
        return len(list(other)) == self.number


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
                node.coordinates = XY(x, y)
                row.append(node)

            self.map.append(row)

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


base_node = Node()
base_node.mark(TERRAIN.GRASS)
base_node.apply_changes()


world = World2D(width=80, height=20, base_node=base_node)


with world.step() as nodes:
    for node in nodes(Fraction(0.02)):
        node.mark(TERRAIN.WATER)

with world.step() as nodes:
    for node in nodes(Marked(TERRAIN.GRASS)):
        if nodes(Distance('euclidean', node.coordinates, 2), Marked(TERRAIN.WATER)) >> Count(1):
            node.mark(TERRAIN.WATER)


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

    print(''.join(line))
