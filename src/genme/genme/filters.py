
import random


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


class Between:
    __slots__ = ('min', 'max')

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __rrshift__(self, other):
        return self.min <= len(list(other)) <= self.max


class Exist:
    __slots__ = ()

    def __rrshift__(self, other):
        return 0 < len(list(other))


class NotExist(Exist):
    __slots__ = ()

    def __rrshift__(self, other):
        return not super().__rrshift__(other)
