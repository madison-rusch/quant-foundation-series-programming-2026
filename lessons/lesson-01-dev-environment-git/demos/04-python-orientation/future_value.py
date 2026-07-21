"""
Lesson 1 — Demo 4: reading a script (slide 27).

Goal is recognition, not mastery. Four landmarks: imports, variables,
functions, output. Full Python fundamentals come in Lesson 3.
"""

import math  # imports — bring in extra tools the script needs

principal = 1000  # variables — named values the script works with
rate = 0.05
years = 3


def future_value(p, r, t):  # functions — take inputs, return outputs
    """Value of p after t years compounding annually at rate r."""
    return p * (1 + r) ** t


def continuous_future_value(p, r, t):
    """Same idea, compounded continuously — this is where `math` earns its import."""
    return p * math.exp(r * t)


result = future_value(principal, rate, years)
continuous = continuous_future_value(principal, rate, years)

print(f"Future value (annual):     {result:.2f}")  # output — print() shows results
print(f"Future value (continuous): {continuous:.2f}")
