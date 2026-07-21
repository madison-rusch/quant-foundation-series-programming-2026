# Homework Submissions — Example & Guide

This folder contains examples to help you understand how to submit your homework via Pull Request (PR).

## Files in this folder

- **`SUBMISSION_TEMPLATE.md`** — The complete guide for submitting your homework. Read this first.
- **`example_01_FIXED.py`** — A corrected version of `savings_calculator_01.py` showing what the fixed script should look like.
- **`EXAMPLE_PR_DESCRIPTION.md`** — A concrete example of what your PR description should look like.
- **Student submissions** — `savings_calculator_NN_<student-name>.py` files (your fixed scripts)
- **`README.md`** — This file.

**Note:** Since multiple students may have the same script assigned, include your name when submitting: `savings_calculator_NN_<your-name>.py`

## Quick Start

1. Read **`SUBMISSION_TEMPLATE.md`** — it covers everything you need to know about formatting your PR.
2. Look at **`example_01_FIXED.py`** — compare it to your assigned script to see what kind of fix might be needed.
3. Complete your own script following the same pattern.
4. **Create a copy of your fixed script in this folder** with your name: `savings_calculator_NN_<your-name>.py`
5. Submit via PR with a description answering the three questions in the template.

## What to do with your script

1. **Clone the repo** (if you haven't already)
   ```bash
   git clone https://github.com/madison-rusch/quant-foundation-series-programming-2026.git
   cd quant-foundation-series-programming-2026
   ```

2. **Check out your assigned script**
   ```bash
   git checkout main
   git pull
   python lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_NN.py
   ```
   Replace `NN` with your assigned number.

3. **Find and fix the bug** (use the debugger if needed)
   - Syntax errors: Python will refuse to run and show you where
   - Runtime errors: You'll get a traceback with the line number
   - Logic errors: The script runs but prints wrong numbers — use F5 (debugger) and breakpoints

4. **Commit your fix**
   ```bash
   git checkout -b lesson1/<your-name>
   git add lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_NN.py
   git commit -m "fix: [one-line description]"
   git push origin lesson1/<your-name>
   ```

5. **Open a Pull Request** on GitHub with:
   - **Title:** `fix: [description of bug]`
   - **Description:** Answer the three questions (see `SUBMISSION_TEMPLATE.md`)

## The Three Questions

Every PR description must answer:

1. **What was the bug?** — Describe the exact problem in the code.
2. **Which kind — syntax, runtime, or logic?** — Explain how you knew.
3. **How did you find it?** — Walk through your debugging process.

**The reasoning matters more than the fix.** Every bug here is just one line to change; the diagnosis is the assignment.

## Help & Resources

- **Stuck?** Check the `lessons/lesson-01-dev-environment-git/` directory for demos on:
  - `01-git-walkthrough/` — Git workflow practice
  - `02-virtual-environment/` — Python setup
  - `03-scripts-vs-notebooks/` — Script structure
  - `04-python-orientation/` — Python review
  - `05-debugging/` — Debugging techniques (F5, breakpoints, VARIABLES pane)

- **Still stuck after 30 minutes?** Open a GitHub Issue — that's not giving up, that's the process.

## Don't

- ❌ Rewrite the script — change only what's necessary
- ❌ Edit anyone else's script — only your assigned number
- ❌ Commit without a PR description
- ❌ Force-push or delete branches (your instructor may still be reviewing)

## Questions?

Ask your instructor, or open an Issue on GitHub.
