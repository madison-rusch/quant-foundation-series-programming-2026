"""
Lesson 3 — Demo 1: Python data types, read through the finance way.

Recognition, not mastery. Each core type is shown as the finance thing it
models: a price series, a bond record, a fixed bar, a set of tickers.
Run it, then read it out loud with the class.
"""

import math


def main() -> None:
    # --- scalars ---------------------------------------------------------
    ticker = "AAPL"          # str  — text, immutable
    shares = 100             # int  — whole number
    price = 101.5            # float — decimal number (analytics, not money you settle)
    is_open = True           # bool — True / False

    print("str  ticker:", ticker)
    print("int  shares:", shares)
    print("float price:", price)
    print("bool is_open:", is_open)

    # --- list: an ordered, changeable price series -----------------------
    prices = [101.5, 99.2, 100.0, 101.5]
    prices.append(102.3)                 # lists can grow — they are mutable
    print("\nlist prices (ordered, mutable):", prices)
    print("  first price:", prices[0])   # index from 0
    
    for px in prices:
        if px > 100:
            tag = "rich"
        elif math.isclose(100, px, rel_tol=1e-15):
            tag = "at the money"
        else:
            tag = "cheap"
        print(px, tag)

    # --- dict: a labelled record, looked up by key -----------------------
    bond = {"face": 1000, "coupon": 0.05, "years": 5}
    print("\ndict bond (lookup by key):", bond)
    print("  coupon rate:", bond["coupon"])

    # --- tuple: a fixed grouping that cannot change ----------------------
    ohlc = (100.0, 103.2, 99.5, 102.1)   # open, high, low, close
    print("\ntuple ohlc (fixed, immutable):", ohlc)

    # --- set: unique membership, no duplicates ---------------------------
    sectors = {"tech", "energy", "tech"}  # the duplicate "tech" collapses
    print("\nset sectors (unique only):", sectors)

def present_value(cf: dict[str, int], r: list[float], t: list[int]) -> float:
    return cf / (1+r) ** t

if __name__ == "__main__":
    v1 = present_value(100, 0.05, 2)
    v2 = present_value(100, 0.05, 3)
    v3 = present_value(100, 0.05, 4)
    print("Year 2", v1)
    print("Year 3", v2)
    print("Year 4", v3)
