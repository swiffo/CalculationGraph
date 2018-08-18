import unittest

import graph as G
import nodes


class CustomNode:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def name(self):
        return self._name

    def calc(self, graph):
        return self._value

class CorrectEvaluation(unittest.TestCase):
    def setUp(self):
        g = G.Graph()
        g.register(CustomNode("custom", 5))
        g.register(nodes.ConstantNode("constant", 17))
        g.register(nodes.CalcNode("calc", lambda g: g("custom") + g("constant")))

        self.graph = g

    def test_value(self):
        self.assertEqual(self.graph("custom"), 5)
        self.assertEqual(self.graph("constant"), 17)
        self.assertEqual(self.graph("calc"), 22)


if __name__ == "__main__":
    unittest.main()
