"""
Lesson 3 — Demo 1: float precision, and why finance people should care.

Computers store floats in binary, so many ordinary decimals (like 0.1) have
no exact representation. The errors are tiny, but they accumulate — and in a
settlement or ledger calculation, "tiny and wrong" is still wrong.

Rule of thumb:
  * float   -> analytics: returns, vols, model prices (rounding error OK)
  * Decimal -> money you actually settle: ledgers, cash amounts
Never compare two floats with ==. Use math.isclose.
"""

import math
from decimal import Decimal


def main() -> None:
    # The classic surprise: this is NOT 0.3.
    total = 0.1 + 0.2
    print("0.1 + 0.2 =", total)
    print("0.1 + 0.2 == 0.3 ? ", total == 0.3)               # False!
    print("math.isclose(0.1 + 0.2, 0.3) ? ", math.isclose(total, 0.3))  # the right check

    # Accumulation: add a dime ten times with floats vs Decimal.
    naive = 0.0
    exact = Decimal("0.00")
    for _ in range(10):
        naive += 0.1              # float drift creeps in
        exact += Decimal("0.10")  # stays exact
    print(f"Naive sum of 10 dimes:   ${naive:.17f}")
    print(f"Naive == $1.00 ? {naive == 1.0}")
    print(f"Decimal sum of 10 dimes: ${exact:.2f}")


if __name__ == "__main__":
    main()
