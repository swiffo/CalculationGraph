"""A simple graph to calculate the output of the Black-Scholes formula.

The Black-Scholes formula calculates the value of a European option under
some simple assumptions. An introduction to the Black-Scholes formula can be found on Wikipedia:
https://en.wikipedia.org/wiki/Black–Scholes_model

A graph is constructed with 3 variable nodes ('option type', 'time to expiry'
and 'strike price'), an output node, 'option price,' and several intermediary
nodes for sub-calculations.

Setting values on the variable nodes is demonstrated as well as overriding
what in practise would be externally determined data.
"""

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

