# Demo 1 — Model and Effort Comparison (slide-level: AI Terminology)

Roughly 10 of the 20 minutes for "AI Terminology." Pre-run this before class and save the transcripts/token counts — model behavior changes over time and you don't want surprises live. If time allows, re-run one combination live to show the mechanics of switching.

## The question

Use the **same** question for every run — nothing else changes:

```
A 10-year corporate bond has a 4% annual coupon and is priced at $920 (face value $1,000).
A 10-year Treasury note yields 4.5%. Walk through how you'd estimate this corporate bond's
approximate yield to maturity, calculate its credit spread over the Treasury, and explain two
distinct reasons the spread could widen even if the issuer's fundamentals haven't changed.
```

This is deliberately not a one-line lookup — it has three parts (approximate YTM, a spread
calculation, and open-ended reasoning about *why* spreads move), which is what makes model and
effort differences visible instead of every response looking identical.

## Runs to do

| Model | Effort | Notes |
|---|---|---|
| Haiku | Medium | Fast/cheap baseline |
| Haiku | High | Same model, more reasoning budget |
| Sonnet | Medium | Balanced baseline |
| Sonnet | High | Same model, more reasoning budget |
| Opus | Medium | Most capable baseline |
| Opus | High | Most capable, most reasoning budget |

Switch models with `/model <name>` (e.g. `/model opus`, `/model sonnet`, `/model haiku`) — the class watched this happen in the setup for this lesson already. Switch effort using whatever control your Claude Code version exposes (an effort/thinking setting alongside `/model`, or in `/config`) — check your installed version, since this UI has moved around across releases.

## What to record for each run

| Model | Effort | Output tokens | Response time | Did it get the approximate YTM formula right? | Did it give 2 distinct, correct reasons for spread widening? |
|---|---|---|---|---|---|
| Haiku | Medium | | | | |
| Haiku | High | | | | |
| Sonnet | Medium | | | | |
| Sonnet | High | | | | |
| Opus | Medium | | | | |
| Opus | High | | | | |

Input tokens are effectively constant across every run (same prompt) — that's the point. **Output tokens are what moves**, and that's what you're paying for and waiting on. Check your Claude Code usage/cost display (varies by version — look for a token or `/cost`-style indicator) after each run and fill in the table live or from your pre-run notes.

## What to look for

- **Haiku, Medium** — usually the fastest, cheapest, and tersest. Watch whether it skips one of the three parts of the question (the approximation, the spread, or the second reason) under time/token pressure.
- **Higher effort, same model** — expect more visible reasoning/structure and often a longer, more hedged answer, at the cost of more output tokens and more wait time. Ask the class: *"Was the extra length worth it, or did it just restate the same answer more slowly?"*
- **Opus vs Sonnet vs Haiku at the same effort** — the capability gap should show up most in the open-ended part (the two reasons spreads widen): expect Opus to reach for less obvious, more precise reasons (e.g. liquidity premium widening vs. duration/convexity effects vs. sector-wide risk repricing) where Haiku may give one generic answer ("the market got riskier").
- **Correctness of the approximate YTM formula** — a good answer uses something like:
  `YTM ≈ [Coupon + (Face − Price) / Years] / [(Face + Price) / 2]`. Check whether cheaper models skip showing the formula and just assert a number.

## Talking points

- Bigger/higher-effort isn't strictly "better" — it's a cost/latency/quality tradeoff you choose per task. A quick syntax lookup doesn't need Opus at High effort; a nuanced credit-spread explanation might.
- Effort is a dial on the *same* model — it's not the same axis as choosing between Haiku/Sonnet/Opus. You can combine a cheap model with high effort, or an expensive model with low effort, depending on the task.
- Token usage is the concrete, visible cost of a prompt. Vague, open-ended prompts (see Demo 2) tend to burn more output tokens for less useful content — connect this back to why scoping your prompt matters.
- There's no universal "best" combination — the right choice depends on how much the task's difficulty justifies the wait and the cost.
