
import random


class Filter:
    __slots__ = ()

    def __invert__(self):
        return Inverter(self)

    def __ror__(self, nodes):
        return Stream(nodes, self)


class Stream:
    __slots__ = ('nodes', 'filter')

    def __init__(self, nodes, filter):
        self.nodes = nodes
        self.filter = filter

    def __iter__(self):
        for node in self.nodes:
            if self.filter(node):
                yield node

    def __bool__(self):
        try:
            self.__iter__().__next__()
        except StopIteration:
            return False

        return True


class Inverter(Filter):
    __slots__ = ('base',)

    def __init__(self, base):
        self.base = base

    def __call__(self, *argv, **kwargs):
        return not self.base.__call__(*argv, **kwargs)


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
        return self.marker(node)
