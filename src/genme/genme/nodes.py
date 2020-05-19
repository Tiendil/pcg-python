

from .filters import Inverter


class Property:
    __slots__ = ('index',)

    def __init__(self, index):
        self.index = index

    def apply_to(self, node):
        node.properties[self.index] = self

    def __call__(self, node):
        return node.properties[self.index] is self

    def __invert__(self):
        return Inverter(self)


class Fabric:
    __slots__ = ('property_groups',)

    def __init__(self):
        self.property_groups = {}

    def properties_size(self):
        return len(self.property_groups)

    def Property(self, group):
        index = self.property_groups.get(group)

        if index is None:
            index = self.properties_size()
            self.property_groups[group] = index

        return Property(index)

    def Node(self, *properties):
        node = Node(properties=[None] * self.properties_size())
        for property in properties:
            property.apply_to(node)
        return node


class Node:
    __slots__ = ('index', 'coordinates', 'space', 'properties', '_new_node')

    def __init__(self, properties):
        self.index = None
        self.coordinates = None
        self._new_node = None
        self.space = None
        self.properties = properties

    def clone(self):
        clone = Node(properties=list(self.properties))
        clone.index = self.index
        clone.coordinates = self.coordinates
        clone.space = self.space
        clone._new_node = None
        return clone

    def new_node(self):
        if self._new_node is not None:
            return self._new_node

        self._new_node = self.clone()
        self.space.register_new_node(self._new_node)

        return self._new_node

    def __ilshift__(self, other):
        new_node = self.new_node()

        if hasattr(other, '__iter__'):
            for property in other:
                property.apply_to(new_node)
        else:
            other.apply_to(new_node)
