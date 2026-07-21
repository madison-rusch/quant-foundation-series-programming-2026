# Demo 4 — Python Orientation (slide 27)

10 minutes. Goal is **recognition, not mastery** — just enough that the homework script isn't intimidating.
Full fundamentals arrive in Lesson 3.

Open `future_value.py` and point at four landmarks, in this order:

| Landmark | In the file | Say this |
|---|---|---|
| **imports** | `import math` | "Tools the script borrows. `math.exp` only exists because of this line." |
| **variables** | `principal`, `rate`, `years` | "Named values. The name is documentation — `principal`, not `p`." |
| **functions** | `def future_value(p, r, t):` | "Inputs go in the parentheses, the answer comes back via `return`." |
| **output** | `print(f"...")` | "`return` hands a value to the code; `print` shows it to a human. Not the same thing." |

## Trace it out loud

Walk `future_value(1000, 0.05, 3)` through by hand: `1000 * 1.05 ** 3` → `1157.63`.
Narrating a trace is exactly the interview skill on slides 28–30 — model it here so the connection lands.

## Two things worth flagging

- **`return` vs `print`** — the most common early confusion, and an actual interview question (slide 28).
- **f-strings** — `f"{result:.2f}"` means "insert `result`, two decimal places." They'll see these everywhere.

Run it to close:

```bash
python lessons/lesson-01-dev-environment-git/demos/04-python-orientation/future_value.py
```
