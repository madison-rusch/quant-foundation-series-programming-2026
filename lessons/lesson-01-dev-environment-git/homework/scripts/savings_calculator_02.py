"""
Lesson 1 Homework — student 02

A small savings-account calculator. It has exactly ONE bug.

Your job:
  1. Run it. Read what happens (or what it prints).
  2. Find the bug and fix it.
  3. Commit the fix to your branch and open a Pull Request.

The script is correct when it prints:
    Future value:    1,628.89
    Present value:   1,000.00
    Interest earned:   628.89

Do not rewrite the script. Change as little as possible.
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
    print(f"Future value:    {fv:>10,.2f}"
    print(f"Present value:   {pv:>10,.2f}")
    print(f"Interest earned: {interest:>10,.2f}")


if __name__ == "__main__":
    main()
