---
name: finmath-code-style
description: House style for FinMath scripts in this course — naming, docstrings, and units.
---

# FinMath Code Style

Apply this style to any Python script that does financial calculations (pricing, yield,
duration, present/future value, etc.).

## Rates are always decimals, and say so

- Function parameters for rates must be decimals (`0.05`, not `5`), and the docstring must say
  "as a decimal" next to every rate parameter.
- Never silently accept a percentage — if a caller might pass `5` meaning `5%`, that's a bug
  waiting to happen, not a feature.

## Every financial function gets a docstring with units

- State the unit of every input and the output: dollars, years, decimal rate, count.
- Example: `years: Years to maturity (integer or float, not months).`

## Naming

- Use full finance terms, not abbreviations a first-year student wouldn't recognize:
  `face_value` not `fv`, `coupon_rate` not `cr`. Exception: `pv`/`fv` are fine *inside* a function
  body once the docstring has already spelled them out.

## Always include a runnable example

- Every script ends with a `__main__` block showing one concrete, realistic example with real
  numbers — not `x = 1, y = 2`. A reader should be able to run the file and see a sane number.

## Sanity-check the output in words

- Where practical, add a one-line comment near the return statement stating what a
  reasonable range looks like, e.g. `# price should be below face_value when coupon < market rate`.
