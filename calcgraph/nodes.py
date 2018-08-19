class ConstantNode:
    """A node with an unchangeable value set a initialisation."""

    def __init__(self, node_name, value):
        """Creates constant node.

        Args:
            node_name: Name of the node.
            value: Value which the node will return on request.
        """
        self._name = node_name
        self._value = value

    def name(self):
        """Returns node name."""
        return self._name

    def calc(self, _graph):
        """Returns value of node.

        Args:
            _graph: A calculation graph, nodes.Graph(), which is ignored.
        """
        return self._value


class CalcNode:
    """A node whose value is calculated from those of other nodes."""

    def __init__(self, node_name, calc_func):
        """Creates calculated node.

        Args:
            node_name: Name of the node.
            calc_func: A function with signature f(graph, *args).
                Must return something other than none.
        """
        self._name = node_name
        self._calc_func = calc_func

    def name(self):
        """Returns node name."""
        return self._name

    def calc(self, graph, *args):
        """Returns node value.

        Args:
            graph: A calculation, nodes.Graph().
            *args: Optional further arguments specifying a dynamic node.
        """
        return self._calc_func(graph, *args)
