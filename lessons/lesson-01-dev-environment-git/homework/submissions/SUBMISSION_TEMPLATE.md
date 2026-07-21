# Homework Submission Template

Use this format when submitting your homework via Pull Request (PR).

## Branch Name
```bash
git checkout -b lesson1/<your-name>
```

**Example:** `lesson1/alice-chen` or `lesson1/bob-martinez`

## PR Title
Keep it concise and descriptive:
```
fix: [brief description of bug found]
```

**Examples:**
- `fix: missing colon in function definition`
- `fix: incorrect operator in interest calculation`
- `fix: off-by-one error in loop`

## PR Description

Your PR description should answer **three things**:

### 1. What was the bug?
Describe the specific issue in your assigned script.

**Example:**
> Line 25 was missing a colon (`:`) after the function definition. Python requires this syntax to mark the start of a function body.

### 2. Which kind was it — syntax, runtime, or logic?
Identify the category and explain how you knew.

**Example:**
> This was a **syntax error**. I knew because Python refused to run the script and showed `SyntaxError: invalid syntax` pointing to line 25.

### 3. How did you find it?
Describe your debugging process. Did you read the error message? Use breakpoints? Step through the code?

**Example:**
> I ran the script with `python lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_01.py` and got an immediate error pointing me to line 25. The error message said `SyntaxError: invalid syntax`, so I looked at that line and noticed the missing colon.

---

## Full PR Description Example

```markdown
## What was the bug?
Line 25 was missing a colon (`:`) after the function definition for `present_value()`. Python syntax requires a colon to mark the start of an indented block.

## Bug type
**Syntax error** — Python's parser caught this immediately and refused to run the script.

**How I knew:** When I ran the script, Python printed:
```
SyntaxError: invalid syntax
  File "savings_calculator_01.py", line 25
    def present_value(future_amount, annual_rate, years)
                                                         ^
```

The caret (^) points right to where the colon should go.

## How I found it
I ran the script as instructed with `python savings_calculator_01.py` and got an immediate error. The error message was clear—it pointed to line 25 and indicated a syntax problem. I read the line and noticed the missing colon right away. Once I added it, the script ran and printed the expected output.
```

## File Submission

Before committing, **copy your fixed script to the submissions folder with your name**:

```bash
# Copy your fixed script to submissions with your name included
cp lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_NN.py \
   lessons/lesson-01-dev-environment-git/homework/submissions/savings_calculator_NN_<your-name>.py
```

**Example:** If you're fixing `savings_calculator_01.py` and your name is Alice Chen:
```bash
cp lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_01.py \
   lessons/lesson-01-dev-environment-git/homework/submissions/savings_calculator_01_alice-chen.py
```

## Commits

Make a **single, focused commit** with both files:

```bash
git add lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_NN.py
git add lessons/lesson-01-dev-environment-git/homework/submissions/savings_calculator_NN_<your-name>.py
git commit -m "fix: missing colon in function definition"
git push origin lesson1/<your-name>
```

## Opening the PR

1. Go to https://github.com/madison-rusch/quant-foundation-series-programming-2026
2. Click **"Pull requests"** tab
3. Click **"New pull request"**
4. Set base to `main`, compare to `lesson1/<your-name>`
5. Paste your description (answering the three questions above)
6. Click **"Create pull request"**

Your instructor will review and provide feedback!
