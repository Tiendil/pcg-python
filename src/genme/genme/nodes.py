
import enum


class OPERATION(enum.Enum):
    ADD_TAG = 1
    REMOVE_TAG = 2
    COUNT = 3
    SET_MARKER = 4
    UNSET_MARKER = 5


class Node:
    __slots__ = ('world', 'coordinates', 'tags', 'counters', 'markers', 'operations')

    def __init__(self):
        self.world = None
        self.coordinates = None
        self.tags = set()
        self.counters = {}
        self.markers = {}
        self.operations = []

    def clone(self):
        clone = Node()
        clone.world = self.world
        clone.coordinates = self.coordinates
        clone.tags |= set(self.tags)
        clone.counters.update(self.counters)
        clone.markers.update(self.markers)

        return clone

    def apply_changes(self):
        for operation, key in self.operations:
            if operation == OPERATION.ADD_TAG:
                self.tags.add(key)
            elif operation == OPERATION.REMOVE_TAG:
                if key in self.tags:
                    self.tags.remove(key)
            elif operation == OPERATION.COUNT:
                self.counters[key[0]] += key[1]
            elif operation == OPERATION.SET_MARKER:
                self.markers[key.__class__] = key
            else:
                raise NotImplementedError(f'unknown operation {operation}: {key}, {value}')

        self.operations[:] = ()

    def mark(self, marker):
        self.operations.append((OPERATION.SET_MARKER, marker))

    def tag(self, tag):
        self.operations.append((OPERATION.ADD_TAG, tag))

    def untag(self, tag):
        self.operations.append((OPERATION.REMOVE_TAG, tag))

    def count(self, counter, value):
        self.operations.append((OPERATION.COUNT, (counter, value)))

    def has_mark(self, marker):
        return self.markers.get(marker.__class__) == marker
