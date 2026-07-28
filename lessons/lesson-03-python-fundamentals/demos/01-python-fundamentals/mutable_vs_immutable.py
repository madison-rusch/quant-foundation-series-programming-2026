"""
Lesson 3 — Demo 1: mutable vs immutable, shown through control flow + functions.

Immutable (str, int, float, tuple): cannot be changed in place — operations
return a NEW object.
Mutable (list, dict, set): can be changed in place.

Why it matters: a function can quietly change a mutable object you passed in.
This snippet also doubles as the control-flow / functions landmark tour:
spot the for loop, the if/else, and the two functions.
"""


def bump_immutable(rate: float) -> float:
    """Return a new rate 1 percentage point higher. The caller's float is untouched."""
    rate = rate + 0.01          # rebinds the local name to a NEW float
    return rate


def bump_mutable(prices: list[float]) -> None:
    """Append in place. The caller's list IS changed — no return needed."""
    prices.append(prices[-1] * 1.01)  # mutates the SAME list the caller holds


def main() -> None:
    # immutable: the original is safe
    rate = 0.05
    new_rate = bump_immutable(rate)
    print("immutable float — original stays put:")
    print("  base_rate:", rate, " new_rate:", new_rate)

    # mutable: the original is modified by the function
    prices = [100.0, 101.0]
    bump_mutable(prices)
    print("\nmutable list — the function changed the caller's list:")
    print("  prices:", prices)

    # control flow landmark: for loop + if/else over the series
    print("\nup/down days:")
    for i in range(1, len(prices)):
        if prices[i] >= prices[i - 1]:
            print(f"  day {i}: up")
        else:
            print(f"  day {i}: down")


if __name__ == "__main__":
    main()
