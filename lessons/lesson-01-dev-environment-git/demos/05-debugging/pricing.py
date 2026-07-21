"""
Lesson 1 — Bonus demo (slide 42): reading a full traceback, end to end.

Run this and read the traceback BOTTOM-UP with the class:
  - last line   -> the actual error: TypeError, ** on 'str' and 'int'
  - line above  -> the file and line where execution stopped (inside future_value)
  - line above  -> how we got there (the call in main)

The error surfaces in `future_value`, but the *cause* is upstream in `main`,
where `years` was read as text and never converted. That gap is the whole lesson.
"""


def future_value(p, r, t):
    return p * (1 + r) ** t


def main():
    principal = 1000
    rate = 0.05
    years = "10"  # e.g. a value read from a CSV or an input() prompt — still text

    result = future_value(principal, rate, years)
    print(f"Future value: {result:.2f}")


if __name__ == "__main__":
    main()
