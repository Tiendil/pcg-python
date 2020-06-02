
import math
import dataclasses

from .topologies import BaseArea


# https://www.redblobgames.com/grids/hexagons/implementation.html


@dataclasses.dataclass(frozen=True, order=True)
class Cell:
    __slots__ = ('q', 'r', 's')

    q: int
    r: int
    s: int

    def __init__(self, q: int, r: int, s: int):
        if q + r + s != 0:
            raise ValueError('wrong cell')

        object.__setattr__(self, 'q', q)
        object.__setattr__(self, 'r', r)
        object.__setattr__(self, 's', s)

    @classmethod
    def from_qr(cls, q:int, r: int):
        return cls(q=q, r=r, s=-q-r)

    @classmethod
    def from_qs(cls, q:int, s: int):
        return cls(q=q, r=-q-s, s=s)

    @classmethod
    def from_qs(cls, r:int, s: int):
        return cls(q=-r-s, r=r, s=s)

    def __add__(self, cell: 'Cell'):
        return Cell(self.q + cell.q,
                    self.r + cell.r,
                    self.s + cell.s)

    def __sub__(self, cell: 'Cell'):
        return Cell(self.q - cell.q,
                    self.r - cell.r,
                    self.s - cell.s)

    def scale(self, scale: float):
        return Cell(self.q * scale,
                    self.r * scale,
                    self.s * scale)

    def neighbour(self, i):
        return self + DIRECTIONS[i % 6]

    def neighbours(self):
        return [self + DIRECTIONS[i] for i in range(6)]


DIRECTIONS = {0: Cell(1, 0, -1),
              1: Cell(1, -1, 0),
              2: Cell(0, -1, 1),
              3: Cell(-1, 0, 1),
              4: Cell(-1, 1, 0),
              5: Cell(0, 1, -1)}


def manhattan_length(cell: Cell):
    return int((abs(cell.q) + abs(cell.r) + abs(cell.s)) / 2)


def manhattan_distance(a: Cell, b: Cell):
    return manhattan_length(a - b)


@dataclasses.dataclass(frozen=True)
class Orientation:
    __slots__ = ('f0', 'f1', 'f2', 'f3',
                 'b0', 'b1', 'b2', 'b3',
                 'start_angle')
    f0: float
    f1: float
    f2: float
    f3: float

    b0: float
    b1: float
    b2: float
    b3: float

    start_angle: float


layout_pointy = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0,
                            math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0,
                            0.5)


layout_flat = Orientation(3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0),
                          2.0 / 3.0, 0.0, -1.0 / 3.0, math.sqrt(3.0) / 3.0,
                          0.0)


@dataclasses.dataclass(frozen=True, order=True)
class Point:
    __slots__ = ('x', 'y')

    x: float
    y: float

    @property
    def xy(self):
        return self.x, self.y

    def __truediv__(self, other):
        return Point(self.x / 2, self.y / 2)

    def __add__(self, point: 'Point'):
        return Point(self.x + point.x,
                     self.y + point.y)

    def __sub__(self, point: 'Point'):
        return Point(self.x - point.x,
                     self.y - point.y)

    def scale(self, scale: float):
        return Point(self.x * scale,
                     self.y * scale)

    def round_up(self):
        return Point(int(math.ceil(self.x)),
                     int(math.ceil(self.y)))

@dataclasses.dataclass
class Layout:
    orientation: Orientation
    size: Point
    origin: Point

    def __init__(self, orientation, size, origin):
        self.orientation = orientation
        self.size = size
        self.origin = origin

        self.cell_corners_offsets = [self._cell_corner_offset(i) for i in range(6)]
        self.cell_size = self._cell_size()

    def cell_to_pixel(self, cell: Cell):
        m = self.orientation

        x = (m.f0 * cell.q + m.f1 * cell.r) * self.size.x;
        y = (m.f2 * cell.q + m.f3 * cell.r) * self.size.y;

        return Point(x + self.origin.x, y + self.origin.y)

    def _cell_corner_offset(self, corner: int):
        size = self.size

        angle = 2.0 * math.pi * (self.orientation.start_angle + corner) / 6

        return Point(size.x * math.cos(angle),
                     size.y * math.sin(angle))

    def _cell_size(self):
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0

        for corner in self.cell_corners_offsets:
            min_x = min(min_x, corner.x)
            max_x = max(max_x, corner.x)
            min_y = min(min_y, corner.y)
            max_y = max(max_y, corner.y)

        return Point(max_x - min_x, max_y - min_y)

    def cell_corners(self, cell: Cell):
        center = self.cell_to_pixel(cell)
        return [center + offset for offset in self.cell_corners_offsets]


def cells_parallelogram(q=None, r=None, s=None):
    if q is None:
        max_k = r
        max_l = s
        constructor = Cell.from_rs
    elif r is None:
        max_k = q
        max_l = s
        constructor = Cell.from_qs
    elif s is None:
        max_k = q
        max_l = r
        constructor = Cell.from_qr
    else:
        raise NotImplementedError('wrong call args')

    for k in range(max_k):
        for l in range(max_l):
            yield constructor(k, l)


# https://www.redblobgames.com/grids/hexagons/implementation.html#shape-triangle
def cells_triangle():
    raise NotImplementedError


def cells_hexagon(radius):
    for q in range(-radius, radius + 1):
        r_min = max(-radius, -q - radius)
        r_max = min(radius, -q + radius)

        for r in range(r_min, r_max + 1):
            yield Cell.from_qr(q, r)


# https://www.redblobgames.com/grids/hexagons/implementation.html#shape-rectangle
def cells_rectangle():
    raise NotImplementedError


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
