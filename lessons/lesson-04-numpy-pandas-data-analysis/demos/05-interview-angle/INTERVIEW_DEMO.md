# Demo 5 — Interview Angle

Roughly 10 minutes. Quick round on the data-analysis topics interviewers actually ask. Run it as a
dialogue: ask the class first, take an answer, then show the model answer.

## The questions (7 min)

| Question | What a good answer hits |
|---|---|
| What's the difference between a NumPy array and a Python list? | Array is typed and fixed-size, so math is vectorized and fast; a list holds mixed types and grows. Use arrays for numeric work. |
| What is a DataFrame and when would you use one? | A table with labelled rows/columns and an index. Use it for tabular/time-series data — loading, filtering, grouping, analysis. |
| How do you handle missing data in Pandas? | Detect with `isna()`, then decide explicitly: drop (`dropna`), fill (`fillna`/`ffill`), or fail. The point is it's a decision, not a default. |
| What is vectorization and why is it faster than a loop? | Applying an operation to a whole array at once, run in compiled code instead of a Python-level loop over elements. Faster and clearer. |

**Framing to teach:** definition in one sentence, then one concrete example (ideally from today —
"I grouped S&P 500 companies by sector," "I filled a missing yield with the prior day"). A real
example beats a memorized definition.

## Claude as a mock interviewer (3 min)

```
Act as an interviewer for an entry-level quant/data role. Ask me one question at a time about NumPy,
Pandas, and handling missing data. Wait for my answer, then ask a harder follow-up based on it.
Don't give me the answer up front.
```

Take a volunteer answer, let Claude follow up, and critique together.

## Talking points

- These four questions map exactly onto the four demos today — the lesson *is* the interview prep.
- "Missing data is a decision, not a default" is the sentence that signals you actually understand
  Pandas, not just its syntax.
- Same instinct as every lesson: explain out loud, get critiqued, refine.
