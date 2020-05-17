
import contextlib


class Space:
    __slots__ = ('_base_nodes', '_new_nodes', '_fixed_order')

    def __init__(self):
        self._base_nodes = {}
        self._new_nodes = {}
        self._fixed_order = []

    def initialize(self, base_node, nodes_coordinates):
        for coordinates in nodes_coordinates:
            node = base_node.clone()
            node.coordinates = coordinates
            node.space = self
            self._base_nodes[node.coordinates] = node

        self._fixed_order = sorted(self._base_nodes)

    def register_new_node(self, node):
        self._new_nodes[node.coordinates] = node

    def base_node(self, coordinates):
        return self._base_nodes.get(coordinates)

    def new_node(self, coordinates):
        return self._new_nodes.get(coordinates)

    def actual_node(self, coordinates):
        node = self.new_node(coordinates)

        if node is None:
            node = self.base_node(coordinates)

        return node

    def _nodes(self, node_getter, *filters):
        for coordinates in self._fixed_order:
            node = node_getter(coordinates)

            if all(filter(node) for filter in filters):
                yield node

    def base(self, *filters):
        yield from self._nodes(self.base_node, *filters)

    def new(self, *filters):
        yield from self._nodes(self.new_node, *filters)

    def actual(self, *filters):
        yield from self._nodes(self.actual_node, *filters)

    @contextlib.contextmanager
    def step(self):

        yield

        self._base_nodes.update(self._new_nodes)
        self._new_nodes.clear()
