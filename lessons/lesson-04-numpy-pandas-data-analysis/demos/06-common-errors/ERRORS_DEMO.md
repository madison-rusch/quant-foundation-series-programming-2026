# Demo 6 — Common NumPy/Pandas errors (debugging)

Optional / overflow demo, roughly 15 minutes. Every one of these will show up in the class's homework.
The goal is **recognition**: when AI generates a transformation, these are the failure shapes Review has
to catch. Each function shows the wrong way (the error or silent bug) then the fix.

`common_errors.py` is the artifact. Nothing crashes — real exceptions are caught and printed so you can
walk all five live.

## Run it

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/06-common-errors/common_errors.py
```

Expected output:

```
--- 1. Comparing floats with == ---
0.1 + 0.2 == 0.3  ->  False   (surprise: not equal)
the actual value is 0.30000000000000004
np.isclose(a, b)  ->  True   (the right check)

--- 2. Silent NaN propagation ---
series.mean() skips the NaN:      4.4233
diff() propagates NaN to two rows:
0     NaN
1    0.03
2     NaN
3     NaN

after ffill() then diff() — gap handled on purpose:
0     NaN
1    0.03
2    0.00
3   -0.05

--- 3. Chained assignment (silent no-op under Copy-on-Write) ---
pandas warns: ChainedAssignmentError: A value is being set on a copy of a DataFrame or Series ...
...and 'flagged' never landed: columns = ['symbol', 'sector']
with a single .loc[rows, col] the update sticks:
symbol sector flagged
  AAPL   Tech    True
  MSFT   Tech    True
   XOM Energy     NaN

--- 4. .loc (label) vs .iloc (position) ---
df.loc[0] -> KeyError: 0 isn't a date label in the index
df.iloc[0]['us_10y']            -> 4.42   (first row by position)
df.loc['2026-06-01']['us_10y'] -> 4.42   (row by label)

--- 5. NumPy shape mismatch ---
prices * weights -> ValueError: operands could not be broadcast together with shapes (4,) (2,)
weighted prices -> [25.   25.25 25.5  25.75]
portfolio value -> 101.5
```

## The five errors

| # | Error | Why it bites | The fix |
|---|---|---|---|
| 1 | `==` on floats returns `False` for "equal" numbers | Binary floating point can't represent `0.1` exactly; rounding error accumulates | `np.isclose` / `math.isclose` with a tolerance |
| 2 | A single `NaN` silently spreads | Reductions (`mean`) skip NaN so it *looks* fine, but elementwise math (`diff`, `+`) propagates it | Decide the missing-data policy first (`ffill`/`dropna`/fail) |
| 3 | Chained assignment updates nothing | `df[mask]["col"] = x` sets a value on a throwaway copy — pandas 3.0 warns and the original is unchanged | One `df.loc[rows, col] = x` in a single step |
| 4 | `.loc` vs `.iloc` mix-up → `KeyError` | `.loc` is **label**-based, `.iloc` is **position**-based; after `set_index` the labels aren't `0,1,2` | Use `.iloc` for position, `.loc` for the actual label |
| 5 | NumPy `ValueError` on mismatched shapes | Vectorized math needs compatible shapes; NumPy refuses to guess | Align the arrays (one weight per price) |

## Talking points

- Errors 1 and 2 are the **float-precision and silent-NaN** themes from Lessons 3–4, shown as the bugs
  they actually cause. This is why "round late" and "no silent NaN" are rules, not style preferences.
- Error 3 is modern pandas: Copy-on-Write means chained assignment fails *loudly with a warning but
  silently in effect* — the column just never appears. Skimming the code, you'd swear it worked.
- Error 4 is the single most common Pandas `KeyError`. The mnemonic: **l**oc = **l**abel.
- Error 5 ties back to Demo 1 — broadcasting is powerful *because* NumPy is strict about shapes rather
  than guessing.
- The meta-point for Review: AI writes code that runs but is subtly wrong (a propagated NaN, a no-op
  assignment). Reading and running it is how you catch that. Question every number.
