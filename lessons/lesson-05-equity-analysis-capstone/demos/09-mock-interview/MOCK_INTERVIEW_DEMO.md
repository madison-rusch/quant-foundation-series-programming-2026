# Demo 9 — Mock Interview Closer

Roughly 20 minutes. Use Claude as a live mock interviewer, drawing on today's analysis and the whole
course. The goal is to show students *how* to practise this on their own — and to send them out able
to talk about what they built. The full question set lives in
[../04-interview-question-bank/interview-question-bank.md](../04-interview-question-bank/interview-question-bank.md).

## Set Claude up as the interviewer

```
Act as an interviewer for an entry-level quantitative research / data-analyst role. Ask me ONE
question at a time. Draw on: the equity-index analysis I just built (returns, rolling volatility,
drawdown, a matplotlib chart), plus Python fundamentals, pandas/NumPy, and Big O. Wait for my answer,
give brief feedback, then ask ONE harder follow-up based on what I said. Don't give me the answer up
front. After about 6 questions, stop and give me structured written feedback.
```

Take a volunteer (or answer the first yourself to model it), let Claude follow up, and critique together.

## Questions to make sure you hit

Pulled from today and the course — see the bank for model answers:

- *"Walk me through what your script does."* — the big one. Goal → pipeline → output, not line by line.
- *"How would you explain a rolling average to a non-technical stakeholder?"*
- *"What would you check if your analysis produced an unexpected result?"*
- *"How did you decide which data source to use?"*
- *"Why annualize volatility with √252?"*
- *"What's the difference between a list and a NumPy array — and when does it matter?"*

## Prompting Claude for *structured* feedback

This is the reusable skill — show them the exact prompt:

```
Now score my answers. For each: what was strong, what was missing, and a tighter model answer.
Then give me an overall read — my two biggest strengths and the two things to study next before
a real interview.
```

## What makes a strong answer — discuss as a class

- **Definition → concrete example → trade-off.** One sentence of what it is, one real example (ideally
  from today), one line on the limitation. This shape signals genuine understanding.
- **"Walk me through it" = goal first.** Lead with what the script achieves, then the pipeline, then
  the output. Narrate the shape, not every line.
- **Honesty beats bluffing.** "I haven't used that, but I'd expect X because Y, and I'd verify in the
  docs" is a *strong* answer. Confident nonsense is the worst one.
- **Tie answers to decisions.** "Missing data is a decision, not a default." "float for analytics,
  Decimal for money." These sentences do a lot of work.

## Talking points

- The point isn't to memorize answers — it's to practise talking about their own work fluently.
- Tell them they can run this exact mock alone, any time, for free. That's the durable takeaway: they
  now have an interview partner on demand.
- Answer *out loud*, as in a real interview. Reading a written answer builds the wrong muscle.
