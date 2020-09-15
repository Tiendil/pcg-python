
import random
import itertools


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
        count = 0

        for item in other:
            count += 1

            if self.number < count:
                return False

        return self.number == count


class Between(Aggregator):
    __slots__ = ('min', 'max')

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __ror__(self, other):
        count = 0

        for item in other:
            count += 1

            if self.max < count:
                return False

        return self.min <= count <= self.max


class Exists(Aggregator):
    __slots__ = ()

    def __ror__(self, other):
        for item in other:
            return True

        return False
