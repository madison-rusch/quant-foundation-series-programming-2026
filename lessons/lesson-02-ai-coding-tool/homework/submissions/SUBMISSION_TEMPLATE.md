# Homework Submission Template — Lesson 2

Use this format when submitting your homework via Pull Request (PR).

## Branch name

```bash
git checkout -b lesson2/<your-name>
```

**Example:** `lesson2/alice-chen` or `lesson2/bob-martinez`

## PR title

```
homework: <your-name> plan/code/review FinMath script
```

## PR description

Your PR description should answer **four things**:

### 1. What was your plan?

Describe what you wanted the script to do before you opened Claude — inputs, outputs, edge cases.

**Example:**
> I wanted a script that takes a bond's face value, coupon rate, price, and years to maturity, and returns the approximate yield to maturity. I wanted it to handle a zero-coupon case too.

### 2. First prompt and output

Paste your first prompt to Claude, and briefly describe what it produced.

**Example:**
> First prompt: "write me a python function for yield to maturity"
>
> Claude produced a function with no docstring, no input validation, and it assumed annual coupons without saying so.

### 3. Refined prompt and what changed

Paste your refined prompt, and describe what changed in the output.

**Example:**
> Refined prompt: "Write a Python function `yield_to_maturity(face_value, coupon_rate, price, years, coupons_per_year=1)` that approximates YTM using the standard approximation formula. Include a docstring, type hints, and handle the zero-coupon case."
>
> The refined output added type hints, a docstring, handled `coupons_per_year`, and explicitly branched for the zero-coupon case instead of dividing by zero.

### 4. What you learned reviewing the code

Note anything you had to look up, question, or push back on.

**Example:**
> I didn't recognize the approximation formula Claude used, so I looked it up to confirm it matched what we'd expect for YTM. I also asked Claude to explain why it used `coupons_per_year` as a default argument instead of a required one.

## Annotations

In your script, add comments to **at least 3 lines** explaining what they do and why. These should be your own words, not copied from Claude's explanation.

## Optional: mock interview reflection

If you tried the AI-as-mock-interviewer exercise, add a short note on what Claude asked and how its critique of your explanation went.

## File submission

Add your annotated script to this folder, named with your topic and your name:

```bash
# Example: yield-to-maturity script by Alice Chen
lessons/lesson-02-ai-coding-tool/homework/submissions/ytm_alice-chen.py
```

## Commits

```bash
git add lessons/lesson-02-ai-coding-tool/homework/submissions/<topic>_<your-name>.py
git commit -m "homework: <your-name> plan/code/review FinMath script"
git push origin lesson2/<your-name>
```

## Opening the PR

1. Go to https://github.com/madison-rusch/quant-foundation-series-programming-2026
2. Click **"Pull requests"** tab
3. Click **"New pull request"**
4. Set base to `main`, compare to `lesson2/<your-name>`
5. Paste your description (answering the four questions above)
6. Click **"Create pull request"**

Your instructor will review and provide feedback!
