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

class DiddlingOneNode(unittest.TestCase):
    def test_diddle_then_eval(self):
        g = G.Graph()
        g.register(nodes.ConstantNode("const", 1))

        g.diddle("const", value=2)
        self.assertEqual(g("const"), 2)
        g.remove_diddle("const")
        self.assertEqual(g("const"), 1)

    def test_eval_then_diddle(self):
        g = G.Graph()
        g.register(nodes.ConstantNode("const", 1))

        self.assertEqual(g("const"), 1)
        g.diddle("const", value=2)
        self.assertEqual(g("const"), 2)
        g.remove_diddle("const")
        self.assertEqual(g("const"), 1)


class DiddlingFixedNodes(unittest.TestCase):
    def setUp(self):
        g = G.Graph()
        g.register(nodes.ConstantNode("base1", 2))
        g.register(nodes.ConstantNode("base2", 3))
        g.register(nodes.CalcNode("add", lambda g: g("base1") + g("base2")))
        g.register(nodes.CalcNode("mul", lambda g: g("base1") * g("base2")))
        g.register(nodes.CalcNode("final", lambda g: g("add") - g("mul")))

        self.g = g

    def test_diddling(self):
        self.assertEqual(self.g("add"), 5)
        self.g.diddle("base1", value=20)
        self.assertEqual(self.g("base1"), 20)
        self.assertEqual(self.g("add"), 23)
        self.assertEqual(self.g("mul"), 60)

        self.g.diddle("mul", value=11)
        self.assertEqual(self.g("final"), 23 - 11)

        self.g.remove_diddle("base1")
        self.assertEqual(self.g("final"), 5 - 11)
        self.assertEqual(self.g("add"), 5)
        self.assertEqual(self.g("mul"), 11)

        self.g.diddle("base2", value=7)
        self.assertEqual(self.g("mul"), 11)
        self.g.remove_diddle("mul")
        self.assertEqual(self.g("final"), 9 - 14)


if __name__ == "__main__":
    unittest.main()
