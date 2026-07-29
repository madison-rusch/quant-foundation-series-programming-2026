"""
Lesson 4 — Demo 6: common NumPy/Pandas errors, and how to fix them.

Every one of these will bite the class in their homework. Each function shows
the WRONG way (the error or silent bug), then the RIGHT way. The point isn't to
memorize fixes — it's to recognize the *shape* of these errors when AI-generated
code produces them, so Review catches them before they corrupt an analysis.

Nothing here crashes the program: the genuine exceptions are caught and printed
so we can walk through all five live.

Run from the repo root:
    python lessons/lesson-04-numpy-pandas-data-analysis/demos/06-common-errors/common_errors.py
"""

import warnings

import numpy as np
import pandas as pd


def error_1_float_equality() -> None:
    """`==` on floats lies. Rounding error means 'equal' numbers aren't."""
    print("--- 1. Comparing floats with == ---")
    a = 0.1 + 0.2
    b = 0.3
    print(f"0.1 + 0.2 == 0.3  ->  {a == b}   (surprise: not equal)")
    print(f"the actual value is {a!r}")
    # Fix: compare within a tolerance.
    print(f"np.isclose(a, b)  ->  {np.isclose(a, b)}   (the right check)\n")


def error_2_silent_nan() -> None:
    """A single NaN silently poisons whole-array arithmetic but not reductions."""
    print("--- 2. Silent NaN propagation ---")
    yields = pd.Series([4.42, 4.45, np.nan, 4.40])
    # A reduction like .mean() skips NaN — looks fine, hides the gap.
    print(f"series.mean() skips the NaN:      {yields.mean():.4f}")
    # But elementwise math propagates it — the NaN spreads to a neighbor.
    daily_change = yields.diff()
    print("diff() propagates NaN to two rows:")
    print(daily_change.to_string(), "\n")
    # Fix: decide explicitly what a missing value means before you compute.
    fixed = yields.ffill().diff()
    print("after ffill() then diff() — gap handled on purpose:")
    print(fixed.to_string(), "\n")


def error_3_chained_assignment() -> None:
    """Chained assignment on a filtered frame silently updates nothing."""
    print("--- 3. Chained assignment (silent no-op under Copy-on-Write) ---")
    df = pd.DataFrame({"symbol": ["AAPL", "MSFT", "XOM"],
                       "sector": ["Tech", "Tech", "Energy"]})
    with warnings.catch_warnings():
        warnings.simplefilter("error")     # turn the warning into a catchable error
        try:
            # df[mask] is a temporary copy; assigning into it is thrown away.
            df[df["sector"] == "Tech"]["flagged"] = True
        except Warning as w:
            print(f"pandas warns: {type(w).__name__}: {str(w).splitlines()[0]}")
    print(f"...and 'flagged' never landed: columns = {list(df.columns)}")
    # Fix: select rows and column together in ONE .loc call, no chaining.
    df.loc[df["sector"] == "Tech", "flagged"] = True
    print("with a single .loc[rows, col] the update sticks:")
    print(df.to_string(index=False), "\n")


def error_4_loc_vs_iloc() -> None:
    """.loc is label-based, .iloc is position-based — mixing them KeyErrors."""
    print("--- 4. .loc (label) vs .iloc (position) ---")
    df = pd.DataFrame({"us_10y": [4.42, 4.45, 4.47]},
                      index=pd.to_datetime(["2026-06-01", "2026-06-02", "2026-06-03"]))
    try:
        df.loc[0]                          # 0 is a position, but .loc wants a label
    except KeyError:
        print("df.loc[0] -> KeyError: 0 isn't a date label in the index")
    # Fix: .iloc for position, .loc for the actual label.
    print(f"df.iloc[0]['us_10y']            -> {df.iloc[0]['us_10y']}   (first row by position)")
    print(f"df.loc['2026-06-01']['us_10y'] -> {df.loc['2026-06-01']['us_10y']}   (row by label)\n")


def error_5_broadcast_shape() -> None:
    """Vectorized math needs compatible shapes, or NumPy refuses to guess."""
    print("--- 5. NumPy shape mismatch ---")
    prices = np.array([100.0, 101.0, 102.0, 103.0])
    weights = np.array([0.5, 0.5])         # wrong length on purpose
    try:
        prices * weights                   # 4 vs 2 — NumPy won't broadcast this
    except ValueError as e:
        print(f"prices * weights -> ValueError: {e}")
    # Fix: align the shapes (here, one weight per price).
    weights = np.array([0.25, 0.25, 0.25, 0.25])
    print(f"weighted prices -> {prices * weights}")
    print(f"portfolio value -> {(prices * weights).sum()}\n")


def main() -> None:
    error_1_float_equality()
    error_2_silent_nan()
    error_3_chained_assignment()
    error_4_loc_vs_iloc()
    error_5_broadcast_shape()


if __name__ == "__main__":
    main()
