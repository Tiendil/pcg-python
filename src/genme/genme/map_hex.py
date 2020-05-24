
import math
import dataclasses


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


@dataclasses.dataclass
class Orientation:
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


@dataclasses.dataclass
class Point:
    x: float
    y: float

    def xy(self):
        return self.x, self.y

    def __truediv__(self, other):
        return Point(self.x / 2, self.y / 2)


@dataclasses.dataclass
class Layout:
    orientation: Orientation
    size: Point
    origin: Point


def cell_to_pixel(layout: Layout, cell: Cell):
    m = layout.orientation

    x = (m.f0 * cell.q + m.f1 * cell.r) * layout.size.x;
    y = (m.f2 * cell.q + m.f3 * cell.r) * layout.size.y;

    return Point(x + layout.origin.x, y + layout.origin.y)


def pixel_to_cell(layout: Layout, point: Point):
    m = layout.orientation

    pt = Point((point.x - layout.origin.x) / layout.size.x,
               (point.y - layout.origin.y) / layout.size.y)

    q = m.b0 * pt.x + m.b1 * pt.y
    r = m.b2 * pt.x + m.b3 * pt.y

    return FractionalCell(q, r, -q - r)


def cell_corner_offset(layout: Layout, corner: int):
    size = layout.size

    angle = 2.0 * math.pi * (layout.orientation.start_angle + corner) / 6

    return Point(size.x * math.cos(angle),
                 size.y * math.sin(angle))


def cell_corners(layout: Layout, cell):
    corners = []

    center = cell_to_pixel(layout, cell)

    for i in range(6):
        offset = cell_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x,
                             center.y + offset.y))

    return corners
