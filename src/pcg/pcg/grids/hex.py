import math
import dataclasses

from PIL import Image
from PIL import ImageDraw

from pcg import colors
from pcg import drawer
from pcg.topologies import BaseArea
from pcg.geometry import Point, BoundingBox


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
                 'b0', 'b1', 'b2', 'b3')
    f0: float
    f1: float
    f2: float
    f3: float

    b0: float
    b1: float
    b2: float
    b3: float


layout_pointy = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0,
                            math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0)


def cell_corner_offset(corner: int):
    angle = 2.0 * math.pi * (0.5 + corner) / 6
    return Point(math.cos(angle), math.sin(angle))


CELL_CORNERS_OFFSETS = [cell_corner_offset(i) for i in range(6)]


def normal_cell_size():
    min_x, max_x = 0, 0
    min_y, max_y = 0, 0

    for corner in CELL_CORNERS_OFFSETS:
        min_x = min(min_x, corner.x)
        max_x = max(max_x, corner.x)
        min_y = min(min_y, corner.y)
        max_y = max(max_y, corner.y)

    return Point(max_x - min_x, max_y - min_y)


CELL_SIZE = normal_cell_size()


def cell_center(cell: Cell):
    x = (layout_pointy.f0 * cell.q + layout_pointy.f1 * cell.r);
    y = (layout_pointy.f2 * cell.q + layout_pointy.f3 * cell.r);
    return Point(x, y)


def cell_corners(cell: Cell):
    center = cell_center(cell)
    return [center + offset for offset in CELL_CORNERS_OFFSETS]


def cell_bounding_box(cell):
    corners = cell_corners(cell)

    box = BoundingBox.from_point(corners[0])

    for corner in corners[1:]:
        box += corner

    return box


def cells_bounding_box(cells):
    box = cell_bounding_box(cells[0])

    for cell in cells[1:]:
        box += cell_bounding_box(cell)

    return box


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


def cells_ring(center, radius):

    if radius == 0:
        return [center]

    if radius == 1:
        return center.neighbours()

    results = []

    cell_pointer = center + DIRECTIONS[4].scale(radius)

    for i in range(6):
        for j in range(radius):
            results.append(cell_pointer)
            cell_pointer = cell_pointer.neighbour(i)

    return results


def area_template(min_distance, max_distance, distance):
    area = []

    radius = 0
    max_distance_exceed = False

    center = Cell(0, 0, 0)

    while not max_distance_exceed:

        max_distance_exceed = True

        for cell in cells_ring(center, radius):
            cell_distance = distance(center, cell)

            if cell_distance <= max_distance:
                max_distance_exceed = False

                if min_distance <= cell_distance:
                    area.append(cell)

        radius += 1

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

    def distance(self, a, b=Cell(0, 0, 0)):
        a = cell_center(a)
        b = cell_center(b)
        return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)


class Manhattan(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=Cell(0, 0, 0)):
        return manhattan_distance(a, b)


class Ring(BaseArea):
    __slots__ = ()

    def connectome(self, topology, min_distance, max_distance):
        return area(topology, self.distance, min_distance, max_distance)

    def distance(self, a, b=Cell(0, 0, 0)):
        return max(abs(a.q-b.q), abs(a.r-b.r))


################################
# drawers
################################

@dataclasses.dataclass
class Sprite:
    color: colors.Color = colors.BLACK
    image: Image = dataclasses.field(default=None, init=False, compare=False)

    def prepair(self, cell_size):
        sprite_size = CELL_SIZE * cell_size

        self.image = Image.new('RGBA', sprite_size.round_up().xy, colors.ALPHA.ints)

        center = sprite_size / 2

        cell = Cell(0, 0, 0)

        draw = ImageDraw.Draw(self.image)

        draw.polygon([(center + point * cell_size).xy for point in cell_corners(cell)],
                      fill=self.color.ints)


class Drawer(drawer.Drawer):
    __slots__ = ('cell_size',)

    def __init__(self, cell_size, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = cell_size

    def prepair_sprite(self, sprite):
        sprite.prepair(self.cell_size)

    def node_position(self, node, canvas_size):
        return canvas_size / 2 + cell_center(node.coordinates) * self.cell_size - self.cell_size

    def calculate_canvas_size(self, nodes):
        coordinates = [node.coordinates for node in nodes]
        return (cells_bounding_box(coordinates).size * self.cell_size).round_up()
