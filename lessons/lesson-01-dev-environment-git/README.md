# Lesson 1 — Developer Environment & Git

2-hour live session. Everything the slides call a demo lives here.

## Pre-class checklist

- [ ] GitHub account
- [ ] VS Code installed
- [ ] Claude Code extension for VS Code
- [ ] Python installed

## Running order

| # | Slides | Time | Folder | What happens |
|---|---|---|---|---|
| Opening | 1–5 | 5 min | — | Backgrounds, tone, the GitHub Issues process |
| 1. Git & GitHub | 6–12 | 40 min | [demos/01-git-walkthrough/](demos/01-git-walkthrough/) | Live clone → change → commit → push → PR |
| 2. Scripts vs Notebooks | 13–17 | 15 min | [demos/03-scripts-vs-notebooks/](demos/03-scripts-vs-notebooks/) | Same analysis both ways; hidden state, live |
| Breakout | 18 | ~15 min | — | Unstructured; groups of 4–6 |
| 3. Virtual Environments | 19–25 | 15 min | [demos/02-virtual-environment/](demos/02-virtual-environment/) | Create `.venv`, install, prove it changed |
| 4. Python Orientation | 26–30 | 10 min | [demos/04-python-orientation/](demos/04-python-orientation/) | Read a script; four landmarks |
| 5. Debugging | 31–36 | 30 min | [demos/05-debugging/](demos/05-debugging/) | Three error kinds, breakpoints, stepping |
| Wrap-up | 37–38 | 5 min | [homework/](homework/) | Assign scripts, restate the PR workflow |
| Bonus | 39–44 | if time | [demos/05-debugging/pricing.py](demos/05-debugging/pricing.py) | Full traceback read-through, git extras, shortcuts |

Each demo folder has a markdown file with the exact commands and talking points. Read those, not this table.

## Setup before class

```bash
git clone <repo-url>
cd quant-foundation-series-programming-2026

# Ctrl+Shift+P -> "Python: Create Environment" -> Venv -> check requirements.txt
pip install -r requirements.txt
```

`.vscode/launch.json` is already configured — `F5` debugs whichever file is open.

## Homework

See [homework/README.md](homework/README.md). Each student gets one script from
[homework/scripts/](homework/scripts/) containing exactly one bug, fixes it on their own branch, and opens a PR.

Instructor answer key: [../../instructor/lesson-01-answer-key.md](../../instructor/lesson-01-answer-key.md) — read the warning at the top before sharing this repo.
