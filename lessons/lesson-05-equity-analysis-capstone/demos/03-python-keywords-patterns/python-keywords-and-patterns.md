# Python Keywords & Patterns — Reference

The runnable companion is [python_patterns.py](python_patterns.py):

```bash
python lessons/lesson-05-equity-analysis-capstone/demos/03-python-keywords-patterns/python_patterns.py
```

These are the Python features that separate "I can write a loop" from "I write Python." They
come up constantly in code review and in interviews. Each section: what it is, when to use it,
and a short annotated example.

## `lambda` — anonymous inline functions

A `lambda` is a small function with no name, written in one expression. Use it when you need a
throwaway function to *pass as an argument* — most often a `key=`.

```python
tickers = [{"symbol": "AAPL", "weight": 0.07}, {"symbol": "NVDA", "weight": 0.09}]
heaviest_first = sorted(tickers, key=lambda t: t["weight"], reverse=True)
bps = list(map(lambda w: w * 10_000, [0.07, 0.06]))     # -> [700.0, 600.0]
```

**Rule of thumb:** if the lambda needs a comment, or you use it twice, give it a real name with
`def`. Lambdas are for the trivial one-liner, not for hiding logic.

## Comprehensions — build a collection in one expression

The Pythonic replacement for a `result = []; for ...: result.append(...)` loop. Reads as "the
list of X for each Y where Z."

```python
returns   = [p[i] / p[i-1] - 1 for i in range(1, len(p))]        # list
up_days   = [r for r in returns if r > 0]                        # list + filter
book      = {sym: px for sym, px in zip(symbols, prices)}        # dict
sectors   = {row["sector"] for row in rows}                      # set (auto-dedupes)
flat_pnl  = [x for row in grid for x in row]                     # nested / flatten
```

**When *not* to:** if it spans multiple lines or nests three deep, it's now write-only. Use a
plain loop — readability beats cleverness.

## Generators & `yield` — lazy, one-at-a-time values

A generator produces values on demand instead of building the whole list in memory. Any function
with `yield` in it is a generator: calling it returns an iterator that runs the body up to each
`yield`, hands back that value, and *pauses* there until asked for the next one.

```python
def rolling_windows(values, size):
    for i in range(len(values) - size + 1):
        yield values[i : i + size]      # produce one window, then pause here

for window in rolling_windows(prices, 3):
    ...                                 # only one window exists in memory at a time
```

A **generator expression** is the lazy sibling of a list comprehension — parentheses, not brackets:

```python
total = sum(abs(p[i] - p[i-1]) for i in range(1, len(p)))   # never builds the full list
```

**Why it matters in finance:** streaming a multi-gigabyte tick file you can't fit in RAM, or a
pipeline that processes rows as they arrive. Lazy = low memory.

## Decorators — wrap a function to add behaviour

A decorator is a function that takes a function and returns a new one wrapping it — adding
behaviour (timing, logging, caching, auth) *without editing the original body*. `@name` above a
`def` is just sugar for `func = name(func)`.

```python
import functools, time

def timed(func):
    @functools.wraps(func)              # keep func's name/docstring on the wrapper
    def wrapper(*args, **kwargs):       # *args/**kwargs forward any arguments through
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] {(time.perf_counter()-start)*1000:.2f} ms")
        return result
    return wrapper

@timed                                  # slow_sum = timed(slow_sum)
def slow_sum(n): return sum(range(n))
```

You use decorators far more than you write them: `@functools.lru_cache` (memoize — free speed on
pure functions), `@property`, `@staticmethod`, `@pytest.fixture`, framework routes. Knowing the
`*args, **kwargs` + `functools.wraps` shape is the standard interview question.

## Keywords that trip people up

| Keyword | What it does | Gotcha |
|---|---|---|
| `with` | Context manager — guarantees cleanup (file close, lock release) even if the body raises | Prefer it over manual `.close()`; the file is closed the instant you leave the block |
| `yield` | Makes a function a generator (see above) | The function doesn't run until you iterate it |
| `is` vs `==` | `is` = same object identity; `==` = equal value | Use `==` for values; `is` only for `None`/`True`/`False` |
| `*args`, `**kwargs` | Capture extra positional / keyword arguments | `*` = tuple of positionals, `**` = dict of keywords |
| `global` / `nonlocal` | Rebind a name in an outer scope | A code smell — usually means state should be passed in, not mutated globally |
| `assert` | Sanity-check an assumption; raises `AssertionError` if false | Stripped out when Python runs with `-O`; never use for real validation |

## Common interview questions (with model answers)

**Q: What's the difference between a list comprehension and a generator expression?**
A list comprehension (`[...]`) builds and returns the whole list in memory immediately. A generator
expression (`(...)`) is lazy — it yields items one at a time as you iterate, using near-constant
memory. Use a list when you need the whole thing (indexing, reuse, `len`); use a generator when you
only pass through once, or the data is too big to hold at once.

**Q: What is a decorator and when would you use one?**
A function that wraps another to add behaviour without changing its body — `@timed`, `@lru_cache`,
`@property`. I'd use one for cross-cutting concerns I want on many functions: timing, logging,
caching, access checks. The wrapper takes `*args, **kwargs` and forwards them, and `functools.wraps`
preserves the original's name and docstring.

**Q: When would you use a generator instead of a list?**
When the data is large or streamed and I don't need it all at once — e.g. reading a huge tick file
line by line, or a pipeline stage that processes rows as they come. It keeps memory flat. If I need
random access, `len`, or to iterate more than once, I'd use a list.

**Q: Explain `*args` and `**kwargs`.**
They collect *extra* arguments. `*args` gathers positional arguments into a tuple; `**kwargs` gathers
keyword arguments into a dict. They're what lets a decorator's wrapper accept and forward whatever
arguments the wrapped function takes.

**Q: `is` vs `==`?**
`==` compares *values* (calls `__eq__`); `is` compares *identity* (same object in memory). Use `==`
for almost everything; reserve `is` for singletons like `None` (`if x is None`). `a == b` can be
`True` while `a is b` is `False`.

**Q: What does `with open(...) as f:` give you over `f = open(...)`?**
The `with` block is a context manager: it guarantees the file is closed when you leave the block,
*even if an exception is raised inside it*. No leaked file handles, no forgotten `.close()`.

## Further reading

- *Fluent Python* by Luciano Ramalho — the definitive book on idiomatic, Pythonic code.
- Real Python: comprehensions <https://realpython.com/list-comprehension-python/>,
  generators <https://realpython.com/introduction-to-python-generators/>,
  decorators <https://realpython.com/primer-on-python-decorators/>.
- **Practice with Claude:** *"Show me a piece of code using a plain loop, then ask me to rewrite it
  as a comprehension / generator, and tell me if mine is idiomatic."*
