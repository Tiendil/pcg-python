
import random


class Inverter:
    __slots__ = ('base',)

    def __init__(self, base):
        self.base = base

    def __call__(self, *argv, **kwargs):
        return not self.base.__call__(*argv, **kwargs)

    def __rrshift__(self, other):
        return not self.base.__rrshift__(other)


class Filter:
    __slots__ = ()

    def __invert__(self):
        return Inverter(self)


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


class Marked(Filter):
    __slots__ = ('marker',)

    def __init__(self, marker):
        self.marker = marker

    def __call__(self, node):
        return node.has_mark(self.marker)


class Count(Filter):
    __slots__ = ('number',)

    def __init__(self, number):
        self.number = number

    def __rrshift__(self, other):
        return len(list(other)) == self.number


class Between(Filter):
    __slots__ = ('min', 'max')

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __rrshift__(self, other):
        return self.min <= len(list(other)) <= self.max


class Exist(Filter):
    __slots__ = ()

    def __rrshift__(self, other):
        return 0 < len(list(other))
