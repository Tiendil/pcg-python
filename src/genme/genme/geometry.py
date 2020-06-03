
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
