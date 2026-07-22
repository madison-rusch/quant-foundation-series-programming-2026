# Demo 4 — Making a Skill, Together

Roughly 25 minutes. Build `finmath-code-style.md` (already in this folder) live with the class, or use it as-is and walk through how it works.

## 1. What a skill is (2 min)

A skill is a reusable instruction set that shapes how the AI behaves — you write it once, and every future prompt in that project can draw on it without you re-explaining your preferences each time.

Contrast with a one-off prompt: a prompt shapes *one* response; a skill shapes *every* response that touches the topic it covers.

## 2. Decide what's worth turning into a skill (5 min)

Ask the class: *"What have we told Claude more than once today?"* Likely answers from Demos 2–3:

- Rates should be decimals, not percentages
- Docstrings should state units
- Full words in variable names, not abbreviations
- Always include a runnable `__main__` example

That repetition is the signal — if you're saying the same thing every time, write it down once as a skill instead.

## 3. Build the skill live (10 min)

Open `finmath-code-style.md` in this folder and walk through each section:

| Section | Why it's here |
|---|---|
| Rates are always decimals | This was the #1 ambiguity in Demo 2's vague prompt |
| Docstring units | Prevents "is `years` an int or a float, and is it years or months" confusion |
| Naming | Keeps scripts readable for someone who hasn't seen the formula before |
| Runnable example | Matches the `__main__` block pattern from Demo 3's `bond_price.py` |
| Sanity-check comment | Reinforces the Review step — a human should be able to eyeball whether output looks right |

If time allows, ask the class to propose one more rule and add it live.

## 4. Load and use it in Claude Code (8 min)

With the skill file in place, prompt Claude for a new function and reference the skill:

```
Using the finmath-code-style skill, write a Python function `present_value(future_value,
rate, years)` that returns the present value of a single future cash flow.
```

Compare the output to what Demo 2's vague prompt produced — same AI, dramatically more
consistent output, because the style constraints no longer live only in your head.

## Talking points

- A skill is leverage: 10 minutes now saves you from repeating the same correction in every future prompt.
- Skills don't replace the Plan step — they encode *how* you want things built, not *what* to build.
- Keep skills short and concrete. A skill nobody can remember the rules of is a skill nobody follows.

## Optional stretch example — a skill for real messy data

If time allows, see [gfdd-stretch-example/](gfdd-stretch-example/) — the same idea applied to a
real public multi-sheet financial dataset (the World Bank's Global Financial Development
Database) instead of a bond formula, to show that skills matter most on data you didn't design
yourself.
