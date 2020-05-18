
import enum


class OPERATION(enum.Enum):
    ADD_TAG = 1
    REMOVE_TAG = 2
    COUNT = 3
    SET_MARKER = 4
    UNSET_MARKER = 5


class Node:
    __slots__ = ('space', 'coordinates', 'tags', 'counters', 'markers', '_new_node')

    def __init__(self):
        self.space = None
        self.coordinates = None
        self.tags = set()
        self.counters = {}
        self.markers = {}
        self._new_node = None

    def clone(self):
        clone = Node()
        clone.space = self.space
        clone.coordinates = self.coordinates
        clone.tags |= set(self.tags)
        clone.counters.update(self.counters)
        clone.markers.update(self.markers)

        return clone

    def new_node(self):
        if self._new_node is not None:
            return self._new_node

        self._new_node = self.clone()
        self.space.register_new_node(self._new_node)

        return self._new_node

    def mark(self, marker):
        self.new_node().markers[marker.__class__] = marker

    def tag(self, tag):
        self.new_node().tags.add(tag)

    def untag(self, tag):
        new_node = self.new_node()

        if tag in new_node.tags:
            new_node.tags.remove(tag)

    def count(self, counter, value):
        self.new_node().counters[counter] += value

    def has_mark(self, marker):
        return self.markers.get(marker.__class__) == marker

    def __iter__(self):
        yield self
