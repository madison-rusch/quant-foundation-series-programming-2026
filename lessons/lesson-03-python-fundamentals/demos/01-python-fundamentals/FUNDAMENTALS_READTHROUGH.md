# Demo 1 — Python Fundamentals (read-through)

Roughly 40 minutes. This is the longest block in the course. The goal is **recognition and
intuition**, not writing code from scratch. Open each snippet, run it, and read it out loud with
the class — the "questions to ask" columns are where the learning happens.

Run everything from the repo root:

```bash
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/data_types.py
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/float_precision.py
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/mutable_vs_immutable.py
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/references_and_copies.py
```

## 1. Data types (10 min) — `data_types.py`

Strings, ints, floats, booleans, lists, dicts, tuples, sets. Walk the file top to bottom.

| Line / idea | Question to ask the class |
|---|---|
| `prices = [101.5, 99.2, 100.0]` (list) | Ordered? Can we change it? Can it hold duplicates? |
| `bond = {"face": 1000, "coupon": 0.05}` (dict) | What are we looking things up *by* here vs a list? |
| `ratings = ("AAA", "AA", "A")` (tuple) | How is this different from the list above? |
| `sectors = {"tech", "energy"}` (set) | What happens if we add "tech" twice? |

**FinMath framing:** a list is a price series, a dict is a labelled record (a bond's terms), a tuple
is a fixed grouping (an OHLC bar), a set is "the unique tickers we hold."

## 2. Float precision (10 min) — `float_precision.py`

The single most important snippet for finance people in this lesson.

```bash
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/float_precision.py
```

Expected output:

```
0.1 + 0.2 = 0.30000000000000004
0.1 + 0.2 == 0.3 ?  False
math.isclose(0.1 + 0.2, 0.3) ?  True
Naive sum of 10 dimes:   $0.99999999999999989
Naive == $1.00 ? False
Decimal sum of 10 dimes: $1.00
```

| Idea | Question to ask the class |
|---|---|
| `0.1 + 0.2` is not `0.3` | Where would this bite you in a pricing or settlement calc? |
| `==` on floats is `False` | So how *should* we compare two floats? (`math.isclose`) |
| `Decimal` sums to exactly `100.00` | When do we reach for `Decimal` instead of `float`? |

**The rule:** `float` is fine for analytics (returns, vols, model prices). For **money you settle**
— ledgers, cash amounts — use `Decimal`. Never compare floats with `==`.

## 3. Control flow & functions (10 min) — inside `mutable_vs_immutable.py`

The snippets use `for` loops, `if/else`, and functions with arguments and return values. Point them
out as you go — landmarks the class already saw in Lesson 1's `future_value.py`.

## 4. Mutable vs immutable & references (10 min) — `mutable_vs_immutable.py`, `references_and_copies.py`

The "aha" block. Run both:

```bash
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/mutable_vs_immutable.py
python lessons/lesson-03-python-fundamentals/demos/01-python-fundamentals/references_and_copies.py
```

`references_and_copies.py` expected output:

```
b = a (reference):     a is now [1, 2, 3, 99]
c = a.copy() (copy):   a is still [1, 2, 3]
tuple add returns new: (1, 2) -> (1, 2, 3), original unchanged
```

| Idea | Question to ask the class |
|---|---|
| Immutable: str, int, float, tuple | What does "cannot be changed in place" actually mean? |
| Mutable: list, dict, set | Why can a function change a list you passed into it? |
| `b = a` does **not** copy | What is `b` really, if not a copy? (another name for the same object) |
| `c = a.copy()` | When is a shallow copy enough, and when isn't it? |

**Memory intuition (keep it light):** a variable is a *name* pointing at an object, not a box holding
it. `b = a` makes a second name for the *same* object — mutate through one, you see it through the
other. This is the bug that surprises people when they pass a list into a function.

## Talking points

- Reading code is a skill on its own — you'll read far more code than you write, especially working
  with AI. This block is deliberate practice at it.
- Float precision is the one thing on this slide that will actually cost money if ignored. Say that.
- Mutable-vs-immutable and references aren't trivia — they're the root cause of a whole category of
  "why did my data change?" bugs. Interviewers probe exactly this (see Demo 3).
