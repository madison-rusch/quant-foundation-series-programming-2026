# Demo 5 — Debugging in VS Code (slides 32–33, bonus 42)

Roughly 30 minutes, the longest live block of the session. Walk the full loop end to end.

## Order to run them

### 1. `broken_compound_interest.py` — syntax error

```bash
python lessons/lesson-01-dev-environment-git/demos/05-debugging/broken_compound_interest.py
```

Nothing runs. Python refuses the file before executing a single line — that's what makes it a *syntax* error.
Fix the missing colon live, re-run, get `1628.89`.

### 2. `pricing.py` — runtime error

Runs, then breaks mid-execution with a `TypeError`. Read the traceback **bottom-up** on screen:

| Line | What it tells you |
|---|---|
| `TypeError: unsupported operand type(s) for **: 'str' and 'int'` | The actual error — start here |
| `File "pricing.py", line …, in future_value` | Where execution stopped |
| `File "pricing.py", line …, in main` | How it got there — and where the real bug lives |

The error is reported inside `future_value`, but the fix belongs in `main` (`years = 10`, or `int(years)`).
That distinction — *where it surfaced* vs *where it came from* — is the point.

### 3. `breakpoint_practice.py` — logic error, the breakpoint demo

Runs fine. Prints a wrong number confidently. No traceback will ever help you here.

Full debugger loop:

1. **Set a breakpoint** — click the gutter left of `total = total * (1 + rate)`; a red dot appears.
2. **Run the debugger** — `F5` (uses the `Python: Current File` config in `.vscode/launch.json`).
3. **Step through** — `F10` step over, `F11` step into, `F5` continue.
4. **Inspect variables** — the VARIABLES pane, hovering over a name, or the DEBUG CONSOLE (type `year`, `total`, or even `range(1, years)`).

Ask the class to predict `total` before each step, then reveal it. That prediction-then-check loop *is* debugging.

**The bug:** `range(1, years)` runs 9 times, not 10. Change it to `range(years)`. Output becomes `1,628.89`.

## Talking points

- Three error classes, three detection points: syntax = before it runs, runtime = during, logic = never (only you catch it).
- Breakpoints beat `print()` because you see *every* variable at that moment, not just the one you guessed to print.
- The DEBUG CONSOLE evaluates arbitrary Python in the paused frame — it's a live REPL inside your bug.
- Diagnosis is the work; the fix is usually one character.
