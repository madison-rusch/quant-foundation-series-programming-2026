# Demo 2 — Good vs Bad Prompting

Roughly 30 minutes. Screen share Claude Code. Same bond throughout: a $1,000 face value bond, 5% annual coupon, 5 years to maturity, currently priced at $980.

## Part A — The vague prompt

Type this into Claude, live:

```
write me some finance code
```

**What comes back** is unpredictable and generic — maybe a random `calculate_interest()` function, maybe a stock price simulator, maybe nothing to do with bonds at all. Ask the class: *"What am I even going to get here?"*

The point: no inputs specified, no outputs specified, no context about what "finance code" even means. Claude has to guess, and a guess is not a plan.

## Part B — The well-scoped prompt

Now type a scoped prompt built from a plan written out **before** touching the keyboard:

```
Write a Python function `bond_price(face_value, coupon_rate, market_rate, years, coupons_per_year=1)`
that returns the present value (price) of a bond by discounting each coupon payment and the face
value at the market rate. Include a docstring, type hints, and a __main__ block that prices a
$1,000 face value, 5% annual coupon, 5-year bond at a 6% market rate.
```

**What comes back** is a specific, testable function — inputs and outputs are exactly what you asked for, so you can review it line by line instead of guessing what it's supposed to do.

## Part C — Ask Claude to fix your own bad prompt

Live, ask Claude to critique Part A's prompt:

```
Here's a prompt I gave an AI coding assistant: "write me some finance code". What's wrong with
it, and how would you rewrite it for a bond pricing function?
```

Watch Claude name the same gaps the class just identified — no inputs, no outputs, no scope. Point out: *"You can use AI to sharpen your own prompts before you use it to write code."*

## Part D — Model comparison (pre-run before class)

Run the **same** well-scoped prompt from Part B — swap `bond_price` for a bond **duration** calculation — through Claude, ChatGPT, Gemini, and Copilot ahead of time, and screenshot or save each output. Do not run this live; model behavior changes and you don't want surprises in front of the class.

```
Write a Python function `bond_duration(face_value, coupon_rate, market_rate, years,
coupons_per_year=1)` that returns the Macaulay duration of a bond in years.
```

| Ask the class to compare | Look for |
|---|---|
| Structure | Did it use a loop, a closed-form formula, or numpy? |
| Explanation | Did it explain the formula, or just hand over code? |
| Edge cases | Did it handle `coupons_per_year != 1` correctly? |
| Style | Docstring, type hints, variable naming |

**Talking point:** the goal is *awareness of differences*, not crowning a winner. Different tools are better for different jobs, and that changes over time.

## Talking points to hit

- A vague prompt outsources the plan to the AI — and the AI can't read your mind.
- Specificity, context, and constraints are the three levers: what do you want, what does it need to know, what are the boundaries.
- "Improve my prompt" is itself a legitimate use of AI — you're not cheating by asking for help scoping the ask.
- Model comparison is about developing judgment, not memorizing a ranking that will be outdated in a month.
