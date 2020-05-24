
import random
import fractions
import dataclasses


@dataclasses.dataclass(frozen=True)
class Color:
    pass


@dataclasses.dataclass(frozen=True)
class RGBA(Color):
    __slots__ = ('r', 'g', 'b', 'a')

    r: fractions.Fraction
    g: fractions.Fraction
    b: fractions.Fraction
    a: fractions.Fraction

    def __init__(self, r, g, b, a=1.0):
        object.__setattr__(self, 'r', fractions.Fraction(r))
        object.__setattr__(self, 'g', fractions.Fraction(g))
        object.__setattr__(self, 'b', fractions.Fraction(b))
        object.__setattr__(self, 'a', fractions.Fraction(a))

    @property
    def floats(self):
        return (float(self.r),
                float(self.g),
                float(self.b),
                float(self.a))

    @property
    def ints(self):
        return (int(round(255 * self.r)),
                int(round(255 * self.g)),
                int(round(255 * self.b)),
                int(round(255 * self.a)))

    @classmethod
    def random(cls, a=1.0):
        return cls(r=random.random(),
                   g=random.random(),
                   b=random.random(),
                   a=a)
