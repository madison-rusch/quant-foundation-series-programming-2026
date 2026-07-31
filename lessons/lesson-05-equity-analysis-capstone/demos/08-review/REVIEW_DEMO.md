# Demo 8 — Review

Roughly 15 minutes. The **Review** step of plan/code/review, applied to the finished analysis. Walk
the whole pipeline as a class, judge the output against the brief, and be honest about where AI helped
and where it needed correcting.

## 1. Does it answer the brief?

Put `index_analysis.png` on the screen next to the printed numbers and check each ask off out loud:

- **Trend?** Yes — the 50-day line shows the direction through the daily noise.
- **Notable volatility?** Yes — the shaded drawdown panel and the printed "most volatile stretch".
- **A clean chart?** Yes — labelled, titled, presentation-ready.

If any answer is "not really," that's the most valuable moment of the lesson — fix it live.

## 2. Read the code as a reviewer

You never trust unread code. Walk the pipeline and interrogate the decisions:

| Reviewer question | What a good answer sounds like |
|---|---|
| Where could the data be wrong? | Wrong symbol, wrong date range, time zone, splits, missing days — checked at load. |
| Is any calculation subtly wrong? | Look-ahead in a rolling signal; `×252` vs `√252`; off-by-one in `pct_change`. |
| Did we handle missing data explicitly? | Yes — we `raise` on a missing close rather than analyze a hole. |
| Did we round too early? | No — raw precision is kept until the `:.2%` display boundary in `main()`. |
| Could someone reproduce this? | Yes — committed backup CSV + a scripted pull, no manual steps. |

## 3. Where did AI help, where did it need correcting?

Have this conversation openly — it's the meta-skill the whole course builds toward:

- **Helped:** boilerplate (the Yahoo JSON parsing, the matplotlib scaffolding), remembering method
  names, first-draft speed.
- **Needed a human:** choosing sensible windows (why 50 days? why a 21-day vol window?), catching a
  wrong annualization, deciding to *fail* on missing data rather than fill it, judging whether the
  chart actually reads cleanly.

## 4. "What would you do with more time?"

Let the class pitch extensions — this seeds the homework:
- Compare against a second index or a sector.
- A different volatility measure (e.g. EWMA), or rolling Sharpe.
- Annotate the chart with the biggest drawdown date.
- Overlay volume, or mark earnings-season windows.

## How this maps to their masters coursework

Say it explicitly: this is the exact loop they'll run for the next two years — *take a vague question,
scope it, pull and clean data, compute something defensible, visualize it, and defend every choice.*
The tools change; the workflow doesn't. Plan/code/review with AI is how they'll move fast **without**
handing their judgement to a machine.

## Talking points

- Review is not a formality — it's where wrong-but-plausible results get caught. A number that looks
  reasonable and is wrong is more dangerous than one that's obviously broken.
- The best reviewers ask "what would make this wrong?" not "does this look fine?"
- Reproducibility (the backup CSV + scripted pull) is what separates a one-off answer from real
  research. Praise it.
