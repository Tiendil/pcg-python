
import random


class Aggregator:
    __slots__ = ()

    def __invert__(self):
        return Inverter(self)


class Inverter(Aggregator):
    __slots__ = ('base',)

    def __init__(self, base):
        self.base = base

    def __ror__(self, other):
        return not self.base.__ror__(other)


class Count(Aggregator):
    __slots__ = ('number',)

    def __init__(self, number):
        self.number = number

    def __ror__(self, other):
        return len(list(other)) == self.number


class Between(Aggregator):
    __slots__ = ('min', 'max')

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __ror__(self, other):
        return self.min <= len(list(other)) <= self.max


class Exist(Aggregator):
    __slots__ = ()

    def __ror__(self, other):
        return 0 < len(list(other))
