# Lesson 1 Homework — Debug & Open a PR

Due before Lesson 2. Your instructor will review every PR.

## What you're doing

You've been assigned one script in [scripts/](scripts/) — `savings_calculator_NN.py`, where `NN` is your assigned number.
Everyone's script is the same except for **one unique bug**. Yours might be a syntax error, a runtime error, or a logic error.

## Steps

```bash
# 1. Clone the repo (skip if you did this in class)
git clone https://github.com/madison-rusch/quant-foundation-series-programming-2026.git
cd quant-foundation-series-programming-2026

# 2. Make sure you're starting from the latest main
git checkout main
git pull

# 3. Create your own branch
git checkout -b lesson1/<your-name>

# 4. Run YOUR script and see what happens
python lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_NN.py

# 5. Fix the bug, then confirm the output matches the target below

# 6. Commit and push
git add lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_NN.py
git commit -m "fix: <one line describing the bug you found>"
git push origin lesson1/<your-name>
```

Then open a **Pull Request** back to `main` on GitHub.

## Target output

The script is fixed when it prints exactly:

```
Principal:         1,000.00
Rate:                 5.00%
Years:                   10
Future value:      1,628.89
Present value:     1,000.00
Interest earned:     628.89
```

If it runs without an error but the numbers are wrong, you have a **logic error** — the hardest kind, because nothing complains. The debugger (F5, breakpoints, the VARIABLES pane) is how you find those.

## In your PR description, answer three things

1. What was the bug?
2. Which kind was it — syntax, runtime, or logic — and how did you know?
3. How did you find it? (Reading the traceback? A breakpoint? Stepping through?)

**The reasoning matters more than the fix.** Every bug here is a one-line change; the diagnosis is the assignment.

## Rules

- Change as little as possible. Don't rewrite the script.
- Only edit **your** script — leave everyone else's alone.
- Stuck for more than 30 minutes? **Open a GitHub Issue.** That's not giving up, that's the process — issues shape Lesson 5.
- Feel free to use Claude, but read and understand the fix. Lesson 2 is about working *with* AI, not being handed answers by it.
