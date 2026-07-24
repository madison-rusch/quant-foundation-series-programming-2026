# Common quant Python pitfalls

## Money
- **Never sum `float` currency in a loop** — errors accumulate. Use `Decimal`.
- Round money only at settlement/display with an explicit rounding mode
  (`ROUND_HALF_EVEN`), never mid-calc.
- Don't mix `Decimal` and `float` in arithmetic — it raises or coerces silently.

## Returns & compounding
- Averaging simple returns then compounding ≠ compounding then averaging.
- Geometric mean for time-series growth; arithmetic mean for expected single-
  period return. Using the wrong one misstates CAGR.
- Annualizing a Sharpe: multiply by `sqrt(periods)`, not `periods`.

## Time & calendars
- Business days ≠ calendar days. Use an exchange calendar; don't assume 5-day
  weeks (holidays exist).
- Beware lookahead bias: shift signals by one period (`signal.shift(1)`) before
  multiplying by returns, or you trade on data you couldn't have known.
- Timezone-naive timestamps silently misalign intraday data across venues.

## Data hygiene
- Survivorship bias: universes that exclude delisted names inflate backtests.
- Forward-fill prices carefully — filling a halted stock's price fabricates
  liquidity. Prefer explicit NaN and drop.
- Corporate actions (splits/dividends): use adjusted prices for returns,
  unadjusted for actual traded prices/notional.

## Numerics
- Covariance matrices from short samples aren't positive-definite — shrink
  (Ledoit-Wolf) before inverting for optimization.
- `float` equality on prices/rates → use `np.isclose`.
- Large-then-small summation loses precision; prefer `np.sum` (pairwise) or
  `math.fsum` for exact float sums.

## Performance
- `df.apply(axis=1)` is a disguised Python loop — avoid on hot paths.
- `object`-dtype columns silently kill vectorization; enforce numeric dtypes.
- Reading CSV repeatedly in a loop dominates runtime; load once, cache Parquet.
