# Vectorization cheat-sheet

Replace Python row-loops with array ops. Rule of thumb: if you're writing
`for i in range(len(df))`, stop and find the vectorized form.

## Returns

```python
# simple returns
rets = prices.pct_change()
# log returns (additive over time)
log_rets = np.log(prices).diff()
```

## Rolling / windowed

```python
vol_20d = rets.rolling(20).std(ddof=1) * np.sqrt(252)
sma = prices.rolling(50).mean()
ewma = rets.ewm(span=20).std()          # exponentially weighted
```

## Conditional assignment (no loop)

```python
signal = np.where(sma_fast > sma_slow, 1, -1)      # long/short flag
weights = np.clip(raw_weights, 0.0, 0.10)          # cap at 10%
```

## Grouped aggregation

```python
# sector-level mean return without looping over sectors
sector_ret = rets.groupby(sector_map, axis=1).mean()
# per-symbol stats
stats = trades.groupby("symbol")["pnl"].agg(["sum", "mean", "count"])
```

## Broadcasting (portfolio math)

```python
port_ret = rets @ weights                 # matrix-vector, all dates at once
cov = np.cov(rets.to_numpy(), rowvar=False)
port_var = weights @ cov @ weights
```

## When a loop is genuinely required

Path-dependent Monte Carlo, some tree/lattice methods, and recursive filters
can't always vectorize. Isolate the scalar kernel and JIT it:

```python
from numba import njit

@njit(cache=True)
def price_path(s0, mu, sigma, dt, z):
    s = s0
    for t in range(z.shape[0]):
        s *= np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z[t])
    return s
```

Generate the random draws with NumPy in bulk, JIT only the recursion.
