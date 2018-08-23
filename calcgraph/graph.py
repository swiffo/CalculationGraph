import collections
import nodes

class Graph:
    def __init__(self):
        """"Instantiate graph."""
        self._node_dict = dict()  # node name to node object
        self._node_values = dict()  # node ID to value
        self._node_children = collections.defaultdict(list)  # node ID to list of 'child' node IDs of nodes calculated
                                                             # using node ID value as input. Basically, which nodes
                                                             # should be notified of changes?
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
            node: Node object.

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

        # When we evaluate a node, we register which nodes it depends on.from
        # To be precise for each node it depends on, we register the node being
        # evaluated as a child.

        node_id = self._node_id(node_name, *args)
        # If the call stack is empty, it means the node is called directly by the user.
        # Hence, there is no child to register.
        if self._call_stack:
            self._node_children[node_id].append(self._call_stack[-1])

        # Evaluate the node itself.
        self._call_stack.append(node_id) # Add current node to call stack
        if node_id in self._diddles:
            return_val = self._diddles[node_id]
        elif node_id in self._node_values:
            return_val = self._node_values[node_id]
        else:
            return_val = self._node_dict[node_name].calc(self, *args)
            self._node_values[node_id] = return_val

        self._call_stack.pop()  # Remove current node from call stack.
                                # By induction, call stack is an invariant.
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

    def set_value(self, node_name, value):
        """Sets the value of the specified node.

        Args:
            node_name: The name of a settable node on the graph.
            value: The new value of the node.
        """
        self.invalidate(node_name)
        self._node_dict[node_name].set_value(value)


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
            raise ValueError('Value must be supplied. Cannot be None.')

        node_id = self._node_id(node_name, *args)
        self.invalidate(node_name, *args)
        self._diddles[node_id] = value

    def invalidate(self, node_name, *args):
        """Invalidate the cached value of the node.

        Args:
            node_name: Name of node.
            *args: Optional extra arguments for a dynamic node.
        """
        # Note: If user diddles a node and calculates something based on it,
        # then invalidates said node, we really shouldn't invalidate the calculations.

        node_id = self._node_id(node_name, *args)
        self._node_values.pop(node_id, None)
        to_invalidate = self._node_children[node_id]

        while to_invalidate:
            current_node_id = to_invalidate.pop()

            self._node_values.pop(current_node_id, None)

            # If the node is diddled, its value will not change and so children do not
            # need to be invalidated. Also, the node children remain the same (they still
            # need to be invalidated when the diddle is removed or changed).
            if current_node_id not in self._diddles:
                to_invalidate.extend(self._node_children[current_node_id])
                self._node_children.pop(current_node_id, None)

    def remove_diddle(self, node_name, *args):
        """Removes diddle from node.

        Args:
            node_name: Name of the node.
            *args: Optional. Any arguments to identify a dynamic node.
        """
        node_id = self._node_id(node_name, *args)
        diddled_value = self._diddles.pop(node_id, None)

        # Nodes should never have value None so we use this as a test of whether the node was diddled at all.
        if diddled_value is not None:
            self.invalidate(node_name, *args)
