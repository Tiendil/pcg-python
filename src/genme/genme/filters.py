
import random


class Filter:
    __slots__ = ()

    def __invert__(self):
        return Inverter(self)


class Inverter(Filter):
    __slots__ = ('base',)

    def __init__(self, base):
        self.base = base

    def __call__(self, node):
        return not self.base(node)


class All(Filter):
    __slots__ = ()

    def __call__(self, node):
        return True


class Fraction(Filter):
    __slots__ = ('fraction',)

    def __init__(self, fraction):
        self.fraction = fraction

    def __call__(self, node):
        return (random.random() < self.fraction)
