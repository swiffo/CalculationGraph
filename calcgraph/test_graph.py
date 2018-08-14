import unittest

import graph as G


class BaseNode:
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
        g.register(BaseNode("base", 5))

        self.graph = g

    def test_value(self):
        self.assertEquals(self.graph("base"), 5)


if __name__ == "__main__":
    unittest.main()
