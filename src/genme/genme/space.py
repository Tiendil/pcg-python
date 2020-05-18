
import contextlib


class Space:
    __slots__ = ('_base_nodes', '_new_nodes', '_fixed_order', 'store_history', '_history')

    def __init__(self, store_history=False):
        self._base_nodes = {}
        self._new_nodes = {}
        self._fixed_order = []

        self.store_history = store_history
        self._history = []

    def initialize(self, base_node, nodes_coordinates):
        for coordinates in nodes_coordinates:
            node = base_node.clone()
            node.coordinates = coordinates
            node.space = self
            self._base_nodes[node.coordinates] = node

        self._fixed_order = sorted(self._base_nodes)

    def register_new_node(self, node):
        self._new_nodes[node.coordinates] = node

    def has_node(self, coordinates):
        return coordinates in self._base_nodes

    def base_node(self, coordinates):
        return self._base_nodes.get(coordinates)

    def new_node(self, coordinates):
        return self._new_nodes.get(coordinates)

    def actual_node(self, coordinates):
        node = self.new_node(coordinates)

        if node is not None:
            return node

        return self.base_node(coordinates)

    def base(self):
        for coordinates in self._fixed_order:
            yield self.base_node(coordinates)

    def new(self):
        for coordinates in self._fixed_order:
            yield self.new_node(coordinates)

    def actual(self):
        for coordinates in self._fixed_order:
            yield self.actual_node(coordinates)

    @contextlib.contextmanager
    def step(self):

        yield

        if self.store_history:
            self._history.append(dict(self._base_nodes))

        self._base_nodes.update(self._new_nodes)

        self._new_nodes.clear()
