"""
Lesson 4 — Demo 1: NumPy basics, and why it exists.

NumPy arrays are typed and fixed-size, so operations run in fast compiled code
instead of a Python loop. That's the whole reason Pandas (built on NumPy) is
quick enough for real financial data. Keep this brief — it motivates Pandas.

Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/01-numpy-foundation/numpy_basics.py
"""

import numpy as np


def main() -> None:
    # --- list vs array: vectorized math, no loop ------------------------
    prices_list = [100.0, 101.0, 102.0, 103.0]
    prices = np.array(prices_list)           # a typed, fixed array of float64

    # With a plain list you'd loop; with an array you just write the math.
    returns = prices[1:] / prices[:-1] - 1   # simple returns, vectorized (slicing!)
    print("prices:", prices)
    print("simple returns:", np.round(returns, 4))

    # --- broadcasting: one scalar applied across the whole array --------
    bumped = prices * 1.01                    # every element * 1.01, no loop
    print("all prices +1%:", bumped)

    # --- basic array math the class should recognize --------------------
    print("mean price:", prices.mean())
    print("max price: ", prices.max())
    print("std of returns:", round(returns.std(), 5))

    # --- array creation helpers -----------------------------------------
    print("zeros(3):", np.zeros(3))
    print("arange(5):", np.arange(5))


if __name__ == "__main__":
    main()
