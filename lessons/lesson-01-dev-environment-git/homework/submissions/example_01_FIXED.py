"""
EXAMPLE SOLUTION: Lesson 1 Homework — student 01

This is what a FIXED script looks like. Compare this to the original
to see what changed and why.

The original script had a syntax error on line 25 (missing colon).
Here's the corrected version.
"""


def future_value(principal, annual_rate, years):
    """Value of `principal` after `years` of annual compounding."""
    return principal * (1 + annual_rate) ** years


def present_value(future_amount, annual_rate, years):
    """Today's value of `future_amount` received `years` from now."""
    return future_amount / (1 + annual_rate) ** years


def total_interest_earned(principal, annual_rate, years):
    """The growth above the original principal."""
    return future_value(principal, annual_rate, years) - principal


def main():
    principal = 1000.0
    annual_rate = 0.05
    years = 10

    fv = future_value(principal, annual_rate, years)
    pv = present_value(fv, annual_rate, years)
    interest = total_interest_earned(principal, annual_rate, years)

    print(f"Principal:       {principal:>10,.2f}")
    print(f"Rate:            {annual_rate:>10.2%}")
    print(f"Years:           {years:>10}")
    print(f"Future value:    {fv:>10,.2f}")
    print(f"Present value:   {pv:>10,.2f}")
    print(f"Interest earned: {interest:>10,.2f}")


if __name__ == "__main__":
    main()
