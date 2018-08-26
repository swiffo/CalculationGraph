# Calculation Graph

The package provides the tool for setting up a calculation graph with cached nodes. 

The graph tracks which nodes depend on which nodes for their values and invalidates 
the cache if a value a node depends on changes. That is, other than in resource consumption
and calculation time, the caching is transparent to the user.

There are two advantages of using calculation graphs:

1. There are families of non-trivial calculations that tend to use the same sub-calculations over and over again. 
E.g., in finance the treasury yield curve will appear in many calculations as will the derived discount curve. Caching
avoids repeated database access and the cost of fitting the curve.
2. Using a calculation graph rather than a family of functions makes it easier to build complex calculations and to 
change calculations of sub-problems. This comes from not having to pass parameters around. If a firm decides 
that it needs another parameter for its yield curve fitting, changing the calculation graph only involves changing
the yield curve node while using a family of functions in addition to changing the yield curve function, 
involves adding that parameter to every single function that 
relies on the yield curve function however deep down in the call stack.

Advantage no. 1 may be the most obvious but it is arguably advantage no. 2 that adds the most value. 

## Node Types
In theory there are only two node types:
1. Nodes whose values can be set by the user at any time.
2. Nodes whose values cannot be set by the user other than possibly at initialization.

In practise it can be convenient to think of nodes as one of the 3 included types:
1. Constant nodes (`ConstantNode()`) for which the value is set at initialization and never changes.
2. Variable nodes (`VariableNode()`) for which the value is set at initialization and can subsequently be changed by calling `set_value`.
3. Calculated nodes (`CalculatedNode()`) for which a function is supplied that calculates the value of the node from other nodes.

It is possible and practical to write a custom nodes class. Such a class must implement the following

```
def CustomNode:
    def name(self):
        """Returns name of the node.
        
        The name of the node along with the *args in the calc method uniquely identifies the node.
        Avoid conflicts.
        """
        pass
        
    def calc(self, graph, *args):
        """Returns value of the node.
        
        Including *args is optional. Note the named parameters are not supported. To access the values
        of other nodes on the graph, call graph('node_name', <optional parameters>).
        """
        pass
```

## Creating a Graph

A graph is created calling
```
import calcgraph as cg
graph = cg.Graph()
```

Nodes are subsequently added to the graph as follows.
```
node = ConstantNode('my_const', 27)
graph.register(node)
```

## Setting Values
It is possible to set the values of the variable nodes. These nodes are meant to be used to house parameters for the calculations. 
```
graph.set_value('my_variable_node', value=88)
```
Currently variable nodes cannot be parameterized. That is, unlike calculated nodes it is not possible to access variable nodes with arguments. 

## Overriding
Overriding provides the tool for what-if calculations. Setting an override means that the value of the node will be fixed with that override even if underlying data changes. Overrides can be set using the graph `override` method and removed using the graph `remove_override` method.
```
graph.override('my_const', value=26)
graph.remove_override('my_const')
```
It is possible to use parameters when overriding:
```
graph.override('my_parameterized_node', 'USD', 0.05, value=1.1)
```

## Example
We construct a simple graph to calculate the value of European options using the Black-Scholes formula.

An introduction to the Black-Scholes formula can be found on Wikipedia:
https://en.wikipedia.org/wiki/Black–Scholes_model

A graph is constructed with 3 variable nodes ('option type', 'time to expiry'
and 'strike price'), an output node, 'option price,' and several intermediary
nodes for sub-calculations.

Setting values on the variable nodes is demonstrated as well as overriding
what in practise would be externally determined data.

```
import math
import numpy as np
from scipy.stats import norm

import calcgraph as cg

graph = cg.Graph()

# We first add what we take as externally determined data (and therefore constant).
# In practise these nodes would be calculated based on market data (and volatility
# would not be a fixed number independent of strike price).
graph.register(cg.ConstantNode('vol', 0.1))  # Annual volatility of spot price (log-normal distribution)
graph.register(cg.ConstantNode('spot price', 250))  # USD
graph.register(cg.ConstantNode('risk free rate', 0.02))  # Per year

# We subsequently add the variable nodes. These are nodes whose values are meant
# to be chosen by the user.
graph.register(cg.VariableNode('option type', 'call'))  # 'call' or 'put'
graph.register(cg.VariableNode('time to expiry', np.nan))  # Measured in years
graph.register(cg.VariableNode('strike price', np.nan))  # USD (as 'spot price')

# We now register the calculated nodes. The order of registration follows the natural
# calculation path but has no effect on the graph.

def d1(g):
    """Calculates d1.

    d1 is a standard sub-calculation when calculating Black-Scholes and the naming
    too is standard.
    """
    S = g('spot price')
    K = g('strike price')
    r = g('risk free rate')
    vol = g('vol')
    T = g('time to expiry')

    return (math.log(S/K) + (r + vol**2 / 2) * T) / (vol * math.sqrt(T))

def d2(g):
    """Calculates d2.

    d2 is a standard sub-calculation when calculating Black-Scholes and the naming
    too is standard.
    """
    return g('d1') - g('vol') * math.sqrt(g('time to expiry'))


graph.register(cg.CalcNode('d1', d1))
graph.register(cg.CalcNode('d2', d2))

def call_price(g):
    """Calculates Black-Scholes call option price."""
    d1 = g('d1')
    d2 = g('d2')
    S = g('spot price')
    K = g('strike price')
    T = g('time to expiry')
    r = g('risk free rate')

    return norm.cdf(d1) * S - norm.cdf(d2) * K * math.exp(-r * T)

def put_price(g):
    """Calculates Black-Scholes put option price."""
    d1 = g('d1')
    d2 = g('d2')
    S = g('spot price')
    K = g('strike price')
    T = g('time to expiry')
    r = g('risk free rate')

    return norm.cdf(-d2) * K * math.exp(-r * T) - norm.cdf(-d1) * S

graph.register(cg.CalcNode('call price', call_price))
graph.register(cg.CalcNode('put price', put_price))

# Finally we add the node which the user is meant to access for the calculated price.

def option_price(g):
    """Calculates Black-Scholes option price."""
    opt_type = g("option type")

    if opt_type == 'call':
        return g('call price')
    elif opt_type == 'put':
        return g('put price')
    else:
        raise ValueError('Unknown option type', opt_type)

graph.register(cg.CalcNode('option price', option_price))


# Let's calculate some option prices!
# 1) An out of the money 2-year call option:
graph.set_value('option type', 'call')
graph.set_value('strike price', 275)
graph.set_value('time to expiry', 2)
print('1: Value of a call option is {:.2f}'.format(graph('option price')))

# 2) As 1 but this time at-the-money.
graph.set_value('strike price', graph('spot price'))
print('2: Value of a call option is {:.2f}'.format(graph('option price')))

# 3) External data is not settable but we can override it. Let's see what happens
# when we double the volatility.
graph.override('vol', value=2*graph('vol'))
print('3: Value of a call option is {:.2f}'.format(graph('option price')))
graph.remove_override('vol')
```
