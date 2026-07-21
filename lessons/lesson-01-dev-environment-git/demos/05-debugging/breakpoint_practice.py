"""
Lesson 1 — Demo 5b: LOGIC ERROR — the kind print statements hide and breakpoints expose.

This script runs cleanly and prints a confident, wrong answer.
$1,000 at 5% for 10 years should be 1,628.89. It reports something else.

Set a breakpoint on the `total = total * (1 + rate)` line, press F5, and watch
the `year` and `total` variables in the debugger's VARIABLES pane.
"""


def compound_interest(principal, rate, years):
    """Value of `principal` after `years` of annual compounding."""
    total = principal
    for year in range(1, years):  # <-- inspect `year` on the last pass
        total = total * (1 + rate)
    return total


def main():
    principal = 1000.0
    rate = 0.05
    years = 10

    total = compound_interest(principal, rate, years)
    expected = 1628.89

    print(f"{principal:,.2f} at {rate:.2%} for {years} years")
    print(f"  computed: {total:,.2f}")
    print(f"  expected: {expected:,.2f}")


if __name__ == "__main__":
    main()
