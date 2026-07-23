# Lesson 2 Homework — Plan / Code / Review with AI

Due before Lesson 3. Your instructor will review every PR.

## What you're doing

Practice the **plan/code/review** framework from class by using Claude to write a simple FinMath script — for example, a yield-to-maturity (YTM) calculator.

## Steps

```bash
# 1. Make sure you're starting from the latest main
git checkout main
git pull

# 2. Create your own branch
git checkout -b lesson2/<your-name>

# 3. Plan: write down what you want the script to do BEFORE prompting Claude
#    (inputs, outputs, edge cases — see "Plan first" below)

# 4. Code: prompt Claude Code to write the script based on your plan

# 5. Review: read every line Claude gives you. Annotate at least 3 lines
#    with comments explaining what they do and why.

# 6. Refine your prompt at least once and re-generate. Note what changed
#    in the output compared to the first attempt.

# 7. Save your final script and notes, then commit and push
git add lessons/lesson-02-ai-coding-tool/homework/submissions/
git commit -m "homework: <your-name> plan/code/review FinMath script"
git push origin lesson2/<your-name>
```

Then open a **Pull Request** back to `main` on GitHub.

## Plan first

Before you open Claude, write down (in your PR description or a notes section):

- What should the script calculate? (e.g. yield to maturity, present value, duration)
- What are the inputs and outputs?
- Any edge cases you want handled (e.g. zero coupon, negative rates)?

This is your "Plan" step — don't skip it. A vague plan produces a vague prompt.

## What to submit

In [submissions/](submissions/), add:

1. **Your script** — `<topic>_<your-name>.py` (e.g. `ytm_alice-chen.py`), with **at least 3 lines annotated** with comments explaining what they do.
2. **Your prompt notes** — see [SUBMISSION_TEMPLATE.md](submissions/SUBMISSION_TEMPLATE.md) for the exact format.

## In your PR description, answer four things

1. What was your plan before you prompted Claude?
2. What was your first prompt, and what did Claude produce?
3. How did you refine the prompt, and what changed in the output?
4. What did you learn reviewing the code — were there any lines you had to look up or question?

**The reasoning matters more than the script.** This assignment is about the process, not the output.

## Optional: AI as a mock interviewer

Ask Claude to quiz you on yield to maturity (or your chosen topic) in plain English, then ask it to critique your explanation. Note anything surprising in your PR description — this part is optional and ungraded.

## Rules

- Use Claude Code (or another AI assistant), but **read and understand every line** before submitting. This lesson is about working *with* AI, not being handed answers by it.
- Stuck for more than 30 minutes? **Open a GitHub Issue.** That's not giving up, that's the process.
