from Graph import *

class CentralBankRate:
    def name(self):
        return 'Central Bank Rate'

    def calc(self, graph):
        return 0.05

class InflationRate:
    def name(self):
        return 'Inflation Rate'

    def calc(self, graph):
        return 0.02

class RealRate:
    def name(self):
        return 'Real Rate'

    def calc(self, graph):
        return graph('Central Bank Rate') - graph('Inflation Rate')

class MultiYearRate:
    def name(self):
        return 'Multiyear Rate'

    def calc(self, graph, years):
        return (1 + graph('Real Rate'))**years - 1

if __name__ == '__main__':
    G = Graph()
    G.register(CentralBankRate())
    G.register(InflationRate())
    G.register(RealRate())
    G.register(MultiYearRate())

    print(G('Real Rate'))
    print(G('Multiyear Rate', 5))
    print(G('Multiyear Rate', 10))