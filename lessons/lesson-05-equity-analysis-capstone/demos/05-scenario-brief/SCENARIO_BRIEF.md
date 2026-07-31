# Demo 5 — The Scenario Brief

Roughly 5 minutes. This opens the second half of class: the live equity-index analysis. Read the
brief to the class exactly as written, then let the ambiguity sit before anyone touches a keyboard.

## The brief

> *"You've just joined a quantitative research team. Your manager has asked for a quick analysis of
> how a major equity index has performed over the past year. She wants to know the trend, any notable
> periods of volatility, and a clean chart she can drop into a presentation. You have two hours. Go."*

## Run it as a discussion (don't answer for them)

Put these on the board and let the class surface the answers:

| Question | What you're fishing for |
|---|---|
| What does "a major equity index" mean? | S&P 500? FTSE 100? We have to *choose* — and justify it. |
| Where do we get the data? | Yahoo Finance, an API, a scrape. Reliability and reproducibility matter. |
| What's "the past year"? | ~252 trading days. Calendar year vs trailing 12 months — pick one and say so. |
| What does "the trend" mean numerically? | A rolling average? A regression line? Total return? |
| What counts as "a notable period of volatility"? | Rolling volatility spikes; large drawdowns. We have to operationalize a vague word. |
| What makes a chart "clean"? | Labelled axes, a title, a legend, no clutter. Readable by someone who won't see the code. |

## The point to make

Real briefs are **vague on purpose** — your manager is busy and trusts you to scope it. The skill
being tested here isn't pandas; it's turning "how did the index do this year?" into a concrete,
defensible list of calculations and outputs. That translation *is* the job.

Resist jumping to code. The next section (Plan) is where we write that scope down — deliberately,
before asking Claude to build anything.

## Talking points

- Every word in the brief that could mean two things is a decision you get to make — and must be
  ready to defend. "I chose the S&P 500 because it's the most-referenced US large-cap benchmark."
- "You have two hours" is realistic. Scoping fast and sensibly beats a perfect analysis delivered
  next week.
- Tell them: by the end of the hour they'll have answered this brief end to end. Set the energy —
  this is the capstone.
