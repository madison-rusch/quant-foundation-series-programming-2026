"""Present value of a single future cash flow (time value of money).

Conventions:
    - rate: annual discount rate, expressed as a decimal (0.05 == 5%)
    - compounding: discrete annual by default; pass continuous=True for
      continuously-compounded discounting (exp(-rate * years))
    - amounts: float64 analytics regime — this is a modelling quantity, NOT an
      exact settlement amount. Use decimal.Decimal at the money boundary if you
      need cash-exact rounding.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def present_value(
    future_value: ArrayLike,
    rate: ArrayLike,
    years: ArrayLike,
    *,
    continuous: bool = False,
) -> np.ndarray | float:
    """Discount a future cash flow back to today.

    Args:
        future_value: cash amount received at ``years`` from now (float regime).
        rate: annual discount rate as a decimal, e.g. 0.05 for 5%. Must be > -1
            for discrete compounding (a rate <= -100% has no valid discount
            factor).
        years: time to the cash flow in years; must be >= 0.
        continuous: if True use ``FV * exp(-rate * years)``; else the discrete
            ``FV / (1 + rate) ** years``.

    Returns:
        Present value, same shape as the broadcast of the inputs (a float for
        all-scalar inputs).

    Raises:
        ValueError: on NaN inputs, negative ``years``, or ``rate <= -1`` under
            discrete compounding.
    """
    fv = np.asarray(future_value, dtype=np.float64)
    r = np.asarray(rate, dtype=np.float64)
    t = np.asarray(years, dtype=np.float64)

    # No silent NaN: fail loud rather than propagate a corrupt discount factor.
    if np.isnan(fv).any() or np.isnan(r).any() or np.isnan(t).any():
        raise ValueError("present_value received NaN in future_value/rate/years")
    if np.any(t < 0):
        raise ValueError("years must be >= 0")

    if continuous:
        pv = fv * np.exp(-r * t)
    else:
        if np.any(r <= -1.0):
            raise ValueError("rate must be > -1 for discrete compounding")
        pv = fv / (1.0 + r) ** t

    # Return a plain float when every input was scalar, else the array.
    return float(pv) if pv.ndim == 0 else pv


if __name__ == "__main__":
    # $1,000 in 10 years, discounted at 5% annual.
    print(f"discrete:   {present_value(1000.0, 0.05, 10):.4f}")
    print(f"continuous: {present_value(1000.0, 0.05, 10, continuous=True):.4f}")

    # Vectorized over several horizons at once.
    horizons = np.array([1, 5, 10, 30])
    print("by horizon:", np.round(present_value(1000.0, 0.05, horizons), 2))
