

class Topology:
    __slots__ = ('connectomes', 'indexes')

    def __init__(self, coordinates):
        self.connectomes = {}
        self.indexes = {xy: None for xy in coordinates}

    def size(self):
        return len(self.indexes)

    def coordinates(self):
        return self.indexes.keys()

    def register_index(self, coordinates, index):
        self.indexes[coordinates] = index

    def area_indexes(self, coordinates):
        area = []

        for point in coordinates:
            index = self.indexes.get(point)

            if index is None:
                continue

            area.append(index)

        return tuple(area)


class BaseArea:
    __slots__ = ('space', 'indexes')

    def __init__(self, node, min_distance=1, max_distance=None):
        if max_distance is None:
            max_distance = min_distance

        self.space = node.space

        connectome_uid = (self.__class__.__name__, min_distance, max_distance)

        if connectome_uid not in self.space.topology.connectomes:
            connectome = self.connectome(self.space.topology, min_distance, max_distance)
            self.space.topology.connectomes[connectome_uid] = connectome
        else:
            connectome = self.space.topology.connectomes[connectome_uid]

        self.indexes = connectome[node.index]

    def connectome(self, topology, min_distance, max_distance):
        raise NotImplementedError('must be overriden in child classes')

    def base(self, *filters):
        return self.space.base(*filters, indexes=self.indexes)

    def new(self, *filters):
        return self.space.new(*filters, indexes=self.indexes)

    def actual(self, *filters):
        return self.space.actual(*filters, indexes=self.indexes)
