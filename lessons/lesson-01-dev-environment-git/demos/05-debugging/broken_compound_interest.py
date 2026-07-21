"""
Lesson 1 — Demo 5a: SYNTAX ERROR (slide 33).

Do not fix this file before class — fixing it live is the demo.
The error is caught before a single line runs. Read the caret in the message.
"""


def compound_interest(principal, rate, periods):
    total = principal
    for i in range(periods)
        total = total * (1 + rate)
    return total


print(compound_interest(1000, 0.05, 10))
