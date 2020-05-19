
import contextlib


class Space:
    __slots__ = ('_base_nodes', '_new_nodes', 'indexes', 'store_history', '_history')

    def __init__(self, store_history=False):
        self._base_nodes = []
        self._new_nodes = []

        self.indexes = {}

        self.store_history = store_history
        self._history = []

    def initialize(self, base_node, nodes_coordinates):
        base_node.space = self

        for i, coordinates in enumerate(nodes_coordinates):
            self.indexes[coordinates] = i

        self._base_nodes = [None] * len(self.indexes)
        self._new_nodes = [None] * len(self.indexes)

        for coordinates, i in self.indexes.items():
            node = base_node.clone()
            node.coordinates = coordinates
            node.index = i

            self._base_nodes[i] = node

    def register_new_node(self, node):
        self._new_nodes[node.index] = node

    def base_node(self, index):
        return self._base_nodes[index]

    def new_node(self, index):
        return self._new_nodes[index]

    def actual_node(self, index):
        return self._new_nodes[index] or self._base_nodes[index]

    def base(self, *filters):
        for node in self._base_nodes:
            for filter in filters:
                if not filter(node):
                    break
            else:
                yield node

    # def new(self, *filters):
    #     for node in self._new_nodes:
    #         if node is not None and all(filter(node) for filter in filters):
    #             yield node

    # def actual(self, *filters):
    #     for new_node, base_node in zip(self._new_nodes, self._base_nodes):
    #         node = new_node or base_node

    #         if all(filter(node) for filter in filters):
    #             yield node

    @contextlib.contextmanager
    def step(self):

        yield

        if self.store_history:
            self._history.append(list(self._base_nodes))

        for i, node in enumerate(self._new_nodes):
            if node is not None:
                self._base_nodes[i] = node
                self._new_nodes[i] = None
