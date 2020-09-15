
import contextlib


class Space:
    __slots__ = ('_base_nodes', '_new_nodes', 'topology', 'recorders')

    def __init__(self, topology, recorders=()):
        self._base_nodes = []
        self._new_nodes = []

        self.topology = topology

        self.recorders = recorders

    def size(self):
        return len(self._base_nodes)

    def initialize(self, base_node):
        base_node.space = self

        self._base_nodes = [None] * self.topology.size()
        self._new_nodes = [None] * self.topology.size()

        for i, coordinates in enumerate(self.topology.coordinates()):
            node = base_node.clone()
            node.coordinates = coordinates
            node.index = i

            self._base_nodes[i] = node

            self.topology.register_index(coordinates, i)

        self.record_state()

    def register_new_node(self, node):
        self._new_nodes[node.index] = node

    def base(self, *filters, indexes=None):
        if indexes is None:
            indexes = range(self.size())

        for i in indexes:
            node = self._base_nodes[i]

            for filter in filters:
                if not filter(node):
                    break
            else:
                yield node

    def new(self, *filters, indexes=None):
        if indexes is None:
            indexes = range(self.size())

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
            indexes = range(self.size())

        for i in indexes:
            node = self._new_nodes[i] or self._base_nodes[i]

            for filter in filters:
                if not filter(node):
                    break
            else:
                yield node

    def record_state(self):
        for recorder in self.recorders:
            recorder.record(self)

    @contextlib.contextmanager
    def step(self):

        yield

        for i, node in enumerate(self._new_nodes):
            if node is not None:
                self._base_nodes[i] = node
                self._new_nodes[i] = None


        self.record_state()
