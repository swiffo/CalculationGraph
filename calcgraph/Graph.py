import collections

class Graph:
    def __init__(self):
        """"Instantiate graph."""
        self._node_dict = dict()  # node name to node object
        self._node_values = dict()  # node ID to value
        self._node_children = collections.defaultdict(list)  # node ID to list of 'child' node IDs of nodes calculated
                                                             # using node ID value as input.
        self._diddles = dict()  # Node ID to value override
        self._call_stack = []  # Node ID call stack (populated and depopulated while evaluating nodes).


    def register(self, node):
        """"Add node to graph.

        A node is an object with the following signature:

        class Node:
            def name(self):
                pass

            def calc(self, graph, *args):
                pass

        The argument, graph, is an instance of the present class.

        Args:
            Node: Node object.

        Raises:
            ValueError: A node by the same name has been previously registered.
        """
        node_name = node.name()
        if node_name in self._node_dict:
            raise ValueError('A node by that name is already registered')
        self._node_dict[node_name] = node

    def __call__(self, node_name, *args, **kargs):
        """"Evaluate node value.

        Args:
            node_name: String giving the name of the node to be evaluated.
            *args: Any further arguments allowed by the dynamic node.

        Returns:
            The type depends on the evaluated node and the arguments.

        Raises:
            ValueError: The node was evaluated with named parameters.
        """
        if kargs:
            raise ValueError('Named parameters are not supported')

        node_id = self._node_id(node_name, *args)
        if self._call_stack:
            self._node_children[node_id].append(self._call_stack[-1])

        self._call_stack.append(node_id)
        if node_id not in self._node_values:
            return_val = self._node_dict[node_name].calc(self, *args)
            self._node_values[node_id] = return_val
        else:
            return_val = self._node_values[node_id]

        self._call_stack.pop()

        return return_val

    def _node_id(self, node_name, *args):
        """Creates unique identifier of the node and argument combination.

        Args:
            node_name: The name of a node on the graph.
            *args: Optional extra parameters for the node.

        Returns:
            Unique identifier. The type happens to be an integer now but may change.
        """
        return hash((node_name, args))

    def diddle(self, node_name, *args, value=None):
        """Override value of specified node.

        Args:
            node_name: Name of node.
            *args: Optional extra arguments for a dynamic node.
            value: The override value.

        Raises:
            ValueError: The value was not specified or was set to None.
        """
        if value is None:
            raise ValueError('value must be supplied')

        node_id = self._node_id(node_name, *args)
        self.invalidate(node_name, *args)
        self._diddles[node_id] = value


    def invalidate(self, node_name, *args):
        """Invalidate the cached value of the node.

        Args:
            node_name: Name of node.
            *args: Optional extra arguments for a dynamic node.
        """
        node_id = self._node_id(node_name, *args)
        del self._node_values[node_id]
        to_invalidate = self._node_children[node_id]

        while to_invalidate:
            current_node_id = to_invalidate.pop()
            if current_node_id not in self._diddles:
                to_invalidate.extend(self._node_children[current_node_id])

            del self._node_children[node_id]
            del self._node_values[current_node_id]


    def remove_diddle(self, node_name, *args):
        pass
