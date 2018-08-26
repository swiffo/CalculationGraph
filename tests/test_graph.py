import unittest

import calcgraph as cg

class CustomNode:
    """An example of how to set up a custom calculated node."""

    def __init__(self, name, value):
        """Instantiates CustomNode()."""
        self._name = name
        self._value = value

    def name(self):
        """Returns name of node."""
        return self._name

    def calc(self, graph):
        """Returns value of node."""
        return self._value

class CorrectDefaultEvaluation(unittest.TestCase):
    """Test for whether default values are correctly returned."""

    def setUp(self):
        """Sets up test."""
        g = cg.Graph()
        g.register(CustomNode('custom', 5))
        g.register(cg.ConstantNode('constant', 17))
        g.register(cg.VariableNode('variable', 25))
        g.register(cg.CalcNode('calc', lambda g: g('custom') + g('constant')))

        self.graph = g

    def test_value(self):
        """Runs value test.

        Asserts that the default values of untouched nodes are returned when
        evaluated.
        """
        self.assertEqual(self.graph('custom'), 5)
        self.assertEqual(self.graph('constant'), 17)
        self.assertEqual(self.graph('variable', 25))
        self.assertEqual(self.graph('calc'), 22)


class OverridingOneNode(unittest.TestCase):
    """Test for whether overrides can be set and removed."""

    def test_override_then_eval(self):
        """Runs test.

        Tests that overriding and only then evaluating
        returns the override value.
        """
        g = cg.Graph()
        g.register(cg.ConstantNode('const', 1))

        g.override('const', value=2)
        self.assertEqual(g('const'), 2)
        g.remove_override('const')
        self.assertEqual(g('const'), 1)

    def test_eval_then_override(self):
        """Runs test.

        Tests that overriding an already evaluated node and then
        evaluating again returns the override value.
        """
        g = cg.Graph()
        g.register(cg.ConstantNode('const', 1))

        self.assertEqual(g('const'), 1)
        g.override('const', value=2)
        self.assertEqual(g('const'), 2)
        g.remove_override('const')
        self.assertEqual(g('const'), 1)


class OverridingFixedNodes(unittest.TestCase):

    def setUp(self):
        """Sets up test."""
        g = cg.Graph()
        g.register(cg.ConstantNode('base1', 2))
        g.register(cg.ConstantNode('base2', 3))
        g.register(cg.CalcNode('add', lambda g: g('base1') + g('base2')))
        g.register(cg.CalcNode('mul', lambda g: g('base1') * g('base2')))
        g.register(cg.CalcNode('final', lambda g: g('add') - g('mul')))

        self.g = g

    def test_overriding(self):
        self.assertEqual(self.g('add'), 5)
        self.g.override('base1', value=20)
        self.assertEqual(self.g('base1'), 20)
        self.assertEqual(self.g('add'), 23)
        self.assertEqual(self.g('mul'), 60)

        self.g.override('mul', value=11)
        self.assertEqual(self.g('final'), 23 - 11)

        self.g.remove_override('base1')
        self.assertEqual(self.g('final'), 5 - 11)
        self.assertEqual(self.g('add'), 5)
        self.assertEqual(self.g('mul'), 11)

        self.g.override('base2', value=7)
        self.assertEqual(self.g('mul'), 11)
        self.g.remove_override('mul')
        self.assertEqual(self.g('final'), 9 - 14)


if __name__ == '__main__':
    unittest.main()
