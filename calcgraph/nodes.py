class ConstantNode:
    """A node with an unchangeable value set a initialisation."""

    def __init__(self, node_name, value):
        """Create constant node."""
        self._name = node_name
        self._value = value

    def name(self):
        """Returns node name."""
        return self._name

    def calc(self, _graph):
        """Returns value of node."""
        return self._value


class CalcNode:
    def __init__(self, node_name, calc_func):
        self._name = node_name
        self._calc_func = calc_func

    def name(self):
        return self._name

    def calc(self, graph, *args):
        return self._calc_func(graph, *args)
