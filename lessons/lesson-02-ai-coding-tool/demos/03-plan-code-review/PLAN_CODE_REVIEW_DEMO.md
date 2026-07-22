# Demo 3 — Plan / Code / Review, End to End

Roughly 20 minutes. This is the live demo referenced in slide-level talking points as "a simple FinMath example end to end." `bond_price.py` in this folder is the artifact it produces.

## 1. Plan (say this out loud, write it where the class can see it)

Before touching Claude, write the plan in plain English:

- **What:** price a bond given its face value, coupon rate, market rate, and years to maturity
- **Inputs:** `face_value`, `coupon_rate`, `market_rate`, `years`, and support for more than one coupon per year
- **Output:** a single float — the present value of the bond
- **Edge cases:** semiannual/quarterly coupons (`coupons_per_year`), not just annual

Ask the class: *"What did we just do?"* — we scoped the problem without writing a line of code. This is the step people skip, and it's the one that determines whether the AI's output is useful.

## 2. Code

Turn the plan directly into a prompt — notice how little translation is needed because the plan was already specific:

```
Write a Python function `bond_price(face_value, coupon_rate, market_rate, years, coupons_per_year=1)`
that returns the present value (price) of a bond by discounting each coupon payment and the face
value at the market rate. Include a docstring, type hints, and a __main__ block that prices a
$1,000 face value, 5% annual coupon, 5-year bond at a 6% market rate.
```

Let Claude generate it. Paste the result into `bond_price.py` (or use the version already in this folder).

## 3. Review

Read it out loud, line by line — don't just glance at it:

| Line / block | Question to ask the class |
|---|---|
| `periods = years * coupons_per_year` | Why multiply instead of just using `years`? |
| `coupon_payment = (face_value * coupon_rate) / coupons_per_year` | What happens if `coupons_per_year=2`? Walk through it. |
| the `for` loop | Why discount each coupon by a different power of `(1 + period_rate)`? |
| `price += face_value / (1 + period_rate) ** periods` | Why is this line outside the loop, and only added once? |

Run it:

```bash
python lessons/lesson-02-ai-coding-tool/demos/03-plan-code-review/bond_price.py
```

Expected output:

```
Bond price: 957.88
```

Ask: *"Does 957.88 make sense?"* — the coupon rate (5%) is below the market rate (6%), so the bond should be priced **below** face value ($1,000). It is. That sanity check — does the number make intuitive sense — is part of Review, not optional.

## Talking points

- Plan is cheap; a bad Code step is expensive to debug later. Spend the time up front.
- Code is a conversation, not a vending machine — the prompt above only worked because the plan was already precise.
- Review means reading *and* reasoning about the output, not just checking that it runs. "Does this number make sense" catches errors that a green checkmark won't.
- This loop — Plan, Code, Review — repeats every lesson from here on. Say that explicitly.
