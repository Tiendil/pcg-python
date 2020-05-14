
import contextlib

from .topologies import XY


class World2D:
    __slots__ = ('width', 'height', 'map')

    def __init__(self, width, height, base_node):
        self.width = width
        self.height = height
        self.map = []

        self._fill_map(base_node)

    def _fill_map(self, base_node):

        for y in range(self.height):
            row = []

            for x in range(self.width):
                node = base_node.clone()
                node.world = self
                node.coordinates = XY(x, y)
                row.append(node)

            self.map.append(row)

    def __getitem__(self, point):
        if (0 <= point.x < self.width) and (0 <= point.y < self.height):
            return self.map[point.y][point.x]

        return None

    def nodes(self, *filters):
        for row in self.map:
            for node in row:
                if all(filter(node) for filter in filters):
                    yield node

    @contextlib.contextmanager
    def step(self):

        yield self.nodes

        for node in self.nodes():
            node.apply_changes()
