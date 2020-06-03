
import math
import dataclasses


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

    def __mul__(self, point: 'Point'):
        return Point(self.x * point.x,
                     self.y * point.y)

    def scale(self, scale: float):
        return Point(self.x * scale,
                     self.y * scale)

    def round_up(self):
        return Point(int(math.ceil(self.x)),
                     int(math.ceil(self.y)))


@dataclasses.dataclass
class BoundingBox:
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    @classmethod
    def from_point(self, point:Point):
        return BoundingBox(x_min=point.x,
                           y_min=point.y,
                           x_max=point.x,
                           y_max=point.y)

    @property
    def size(self):
        return Point(self.x_max - self.x_min,
                     self.y_max - self.y_min)

    def __add__(self, figure):
        if isinstance(figure, BoundingBox):
            return BoundingBox(x_min=min(self.x_min, figure.x_min),
                               y_min=min(self.y_min, figure.y_min),
                               x_max=max(self.x_max, figure.x_max),
                               y_max=max(self.y_max, figure.y_max))

        if isinstance(figure, Point):
            return BoundingBox(x_min=min(self.x_min, figure.x),
                               y_min=min(self.y_min, figure.y),
                               x_max=max(self.x_max, figure.x),
                               y_max=max(self.y_max, figure.y))

        raise NotImplementedError()
