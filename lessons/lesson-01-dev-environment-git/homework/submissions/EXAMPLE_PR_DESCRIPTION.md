# Example PR Description

This is what a **complete, well-written PR description** looks like.

Copy this format (not the content!) when you submit your homework.

---

## PR Title
```
fix: missing colon after function definition on line 25
```

## PR Description (what you paste into GitHub)

```markdown
## What was the bug?

Line 25 was missing a colon (`:`) after the `present_value()` function definition:

```python
def present_value(future_amount, annual_rate, years)  # ❌ Missing colon here
```

Python's syntax requires a colon to mark the start of an indented block. The fix:

```python
def present_value(future_amount, annual_rate, years):  # ✅ Fixed
```

## Bug type

**Syntax error**

**How I knew:** Python's parser rejected the script immediately. When I ran:
```bash
python savings_calculator_01.py
```

I got:
```
  File "savings_calculator_01.py", line 25
    def present_value(future_amount, annual_rate, years)
                                                         ^
SyntaxError: invalid syntax
```

The caret (`^`) points right to where the colon should be.

## How I found it

1. Ran the script as instructed: `python lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_01.py`
2. Python immediately failed with `SyntaxError: invalid syntax`
3. The error message pointed me to line 25
4. I looked at line 25 and compared it to other function definitions in the script
5. I noticed `present_value()` was missing the `:` that the other functions had
6. Added the colon, ran the script again, and it printed the expected output
```

---

## Key points

✅ **Do this:**
- Name the exact bug (line number, what's wrong)
- Show the before/after code in a code block
- Explain how you identified the error type
- Walk through your debugging steps
- Keep it clear and concise

❌ **Avoid:**
- "I fixed it" with no explanation
- Vague descriptions like "it was broken"
- Long rambling stories
- Multiple commits (one fix = one commit)

---

## How to submit

1. **Copy your fixed script to the submissions folder** with your name:
   ```bash
   cp lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_01.py \
      lessons/lesson-01-dev-environment-git/homework/submissions/savings_calculator_01_alice-chen.py
   ```
   (Replace `alice-chen` with your name)

2. **Commit both files:**
   ```bash
   git add lessons/lesson-01-dev-environment-git/homework/scripts/savings_calculator_01.py
   git add lessons/lesson-01-dev-environment-git/homework/submissions/savings_calculator_01_alice-chen.py
   git commit -m "fix: missing colon after function definition on line 25"
   git push origin lesson1/alice-chen
   ```

3. **Open a Pull Request** on GitHub

4. In the PR description box, paste your answers to the three questions (the part starting with `## What was the bug?`)

5. Your instructor will review!
