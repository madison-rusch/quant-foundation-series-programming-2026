# Demo 1 — NumPy, the Foundation

Roughly 20 minutes. Keep it brief — the point is to explain *why* Pandas works the way it does, not
to teach NumPy exhaustively. Students will meet NumPy again in their degree.

## The one idea

A Python list can hold anything and can grow; a **NumPy array is typed and fixed-size**. That
constraint is what lets NumPy run math in fast compiled code instead of a Python loop. Pandas is
built on NumPy — so this is why Pandas is fast enough for real data.

## Run it

```bash
python lessons/lesson-04-numpy-pandas-data-analysis/demos/01-numpy-foundation/numpy_basics.py
```

Expected output:

```
prices: [100. 101. 102. 103.]
simple returns: [0.01   0.0099 0.0098]
all prices +1%: [101.   102.01 103.02 104.03]
mean price: 101.5
max price:  103.0
std of returns: 8e-05
zeros(3): [0. 0. 0.]
arange(5): [0 1 2 3 4]
```

## Review

| Line | Question to ask the class |
|---|---|
| `prices[1:] / prices[:-1] - 1` | This computes every daily return at once — where's the loop? (there isn't one) |
| `prices * 1.01` | One number times a whole array — what is "broadcasting" doing here? |
| `prices.mean()` | Why is calling `.mean()` on an array faster than summing a list in a `for` loop? |

Ask: *"What did we NOT write?"* — no loop over prices. That's vectorization, and it's the habit
Pandas will let us keep.

## Talking points

- Typed + fixed-size = fast. That trade (you give up flexibility) is the whole deal.
- Vectorized code is also *shorter and clearer* — `prices * 1.01` reads better than a loop.
- This is a 20-minute on-ramp. Don't rabbit-hole on NumPy internals — get to Pandas.
