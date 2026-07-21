# Demo 2 — Create & Activate a Virtual Environment (slides 20–21)

Switch screen share to VS Code. Roughly 8 minutes.

## Run it once *before* the venv exists

```bash
python lessons/lesson-01-dev-environment-git/demos/02-virtual-environment/check_environment.py
```

Point at the interpreter path — it's the system-wide Python. Some packages may be missing.

## Create the environment

```
Ctrl+Shift+P  ->  "Python: Create Environment"
Select: Venv
Select interpreter: Python 3.x
Check: requirements.txt   (VS Code offers to install it for you)
```

Show the `(.venv)` prefix appearing in the integrated terminal prompt. That prefix *is* the activation.

If installing manually:

```bash
pip install -r requirements.txt
pip list
```

## Run it again

Same command, different answer: the interpreter path now points inside `.venv/`, and every package reports `[ok]`.

## Talking points

- The environment is **just a folder**. `.venv/` is in `.gitignore` — you never commit it; you commit `requirements.txt` and let others rebuild it.
- One environment **per project**. Project A needing an old pandas can't break Project B.
- `requirements.txt` is the recipe; `.venv/` is the meal. Share the recipe.
- Mention that `conda`, `poetry`, and `uv` solve the same problem differently (slide 22) — recognition only.
