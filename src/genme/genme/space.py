
import contextlib


class Space:
    __slots__ = ('_base_nodes', '_new_nodes', 'coordinates_to_indexes', 'store_history', '_history', '_indexes')

    def __init__(self, store_history=False):
        self._base_nodes = []
        self._new_nodes = []

        self.coordinates_to_indexes = {}

        self.store_history = store_history
        self._history = []

        self._indexes = []

    def size(self):
        return len(self.coordinates_to_indexes)

    def initialize(self, base_node, nodes_coordinates):
        base_node.space = self

        for i, coordinates in enumerate(nodes_coordinates):
            self.coordinates_to_indexes[coordinates] = i

        self._base_nodes = [None] * self.size()
        self._new_nodes = [None] * self.size()

        for coordinates, i in self.coordinates_to_indexes.items():
            node = base_node.clone()
            node.coordinates = coordinates
            node.index = i

            self._base_nodes[i] = node

        self._indexes = list(range(0, self.size()))

    def register_new_node(self, node):
        self._new_nodes[node.index] = node

    def base(self, *filters, indexes=None):
        if indexes is None:
            indexes = self._indexes

        for i in indexes:
            node = self._base_nodes[i]

            for filter in filters:
                if not filter(node):
                    break
            else:
                yield node

    def new(self, *filters, indexes=None):
        if indexes is None:
            indexes = self._indexes

        for i in indexes:
            node = self._new_nodes[i]

            if node is None:
                continue

            for filter in filters:
                if not filter(node):
                    break
            else:
                yield node

    def actual(self, *filters, indexes=None):
        if indexes is None:
            indexes = self._indexes

        for i in indexes:
            node = self._new_nodes[i] or self._base_nodes[i]

            for filter in filters:
                if not filter(node):
                    break
            else:
                yield node

    @contextlib.contextmanager
    def step(self):

        yield

        if self.store_history:
            self._history.append(list(self._base_nodes))

        for i, node in enumerate(self._new_nodes):
            if node is not None:
                self._base_nodes[i] = node
                self._new_nodes[i] = None
