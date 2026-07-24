---
name: quant-python
description: >-
  Conventions for writing finance and quantitative Python code. Use whenever
  writing, refactoring, or reviewing Python for pricing, risk, backtesting,
  time-series, portfolio, or market-data work. Enforces fast, vectorized,
  clean, script-based code (no Jupyter notebooks) with correct money and
  numerical handling.
---

# Quant Python

Write finance/quant Python that is fast, numerically correct, and clean. We are
coders first: prefer plain `.py` scripts over notebooks, vectorized code over
loops, and small well-named functions over clever one-liners.

## Non-negotiables

1. **Scripts, not notebooks.** Deliver `.py` files runnable from the CLI. Never
   create or edit `.ipynb` unless the user explicitly asks. Put runnable entry
   points behind `if __name__ == "__main__":`.
2. **Money is never `float` for exact amounts.** Use `decimal.Decimal` for
   currency, ledger, and settlement amounts. `float` is fine for statistical /
   model quantities (returns, vols, prices in analytics) where rounding error is
   acceptable and speed matters — but say which regime you're in.
3. **Vectorize.** Prefer NumPy/pandas array ops over Python `for` loops over
   rows. A loop over a DataFrame's rows is a code smell — reach for `.groupby`,
   broadcasting, `np.where`, `rolling`, or `numba` before writing one.
4. **Type hints everywhere**, plus docstrings that state units and conventions
   (e.g. "rate: annual, continuously compounded", "returns: simple, not log").
5. **No silent NaN.** Decide explicitly: drop, fill, or fail. Financial NaNs
   (missing prices, non-trading days) corrupt results silently.

## Workflow

- Start from a script skeleton (see `references/script_template.py`).
- Pull shared helpers (day-count, annualization, rounding) into a module rather
  than copy-pasting.
- Add a `pytest` test for any pricing/risk formula — assert against a known
  closed-form or textbook value. Numerical code without a reference test is a
  liability.
- Keep dependencies lean: `numpy`, `pandas`, `scipy` cover most needs. Reach for
  `polars` when data size or speed demands it.

## Numerical correctness

- **Annualization:** always state the periods-per-year factor. Vol scales with
  `sqrt(periods)`, returns scale linearly. Don't hardcode 252/12/365 — name it.
- **Log vs simple returns:** log returns are additive across time, simple
  returns are additive across assets. Pick deliberately and document it.
- **Compounding:** be explicit about discrete vs continuous. `exp(-r*t)` vs
  `(1+r)**-t` are different answers.
- **Comparisons:** never `==` on floats. Use `math.isclose` / `np.isclose`.
- **Rounding:** round only at the boundary (display/settlement), never mid-
  computation. For money use `Decimal.quantize` with an explicit
  `ROUND_HALF_EVEN` (banker's rounding) unless a venue requires otherwise.

## Performance

- Profile before optimizing (`cProfile`, `%timeit`-equivalent in a script, or
  `time.perf_counter`). Don't guess.
- Vectorized NumPy first; `numba.njit` for genuinely scalar-recursive kernels
  (e.g. path-dependent Monte Carlo, some tree methods) that can't vectorize.
- Prefer `np.float64` arrays; avoid `object`-dtype pandas columns (they kill
  speed and hide bugs).
- For large data, prefer columnar formats (Parquet) over CSV; `polars` lazy
  frames for out-of-core work.

## Clean code

- Small pure functions; side effects (I/O, plotting) at the edges.
- Name things in domain terms: `discount_factor`, `notional`, `ytm`, not `x`.
- No magic numbers — name constants (`TRADING_DAYS = 252`).
- One responsibility per function; if a docstring needs "and", split it.
- Fail loud on bad input (assert shapes, validate rate/price signs).

See `references/` for a script template, a vectorization cheat-sheet, and
common quant pitfalls before writing new code.
