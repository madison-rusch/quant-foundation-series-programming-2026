# Demo 1 — Live Git Walkthrough (slide 8)

Switch screen share to VS Code. Narrate each step as you type it. Roughly 10 minutes.

## Commands

```bash
# 1. Clone — copy the repo (and its full history) to your machine
git clone https://github.com/madison-rusch/quant-foundation-series-programming-2026.git
cd quant-foundation-series-programming-2026

# 2. Branch — an independent line of work off main
git checkout -b your-name-branch

# 3. Change — add your name to CLASS_ROSTER in hello_finance.py
#    (edit in VS Code, then save)

# 4. See what changed, before committing anything
git status
git diff

# 5. Stage + commit — a saved snapshot, with a message
git add lessons/lesson-01-dev-environment-git/demos/01-git-walkthrough/hello_finance.py
git commit -m "first commit: add <your name> to roster"

# 6. Push — send local commits up to GitHub
git push origin your-name-branch
```

Then open GitHub in the browser and click **Compare & pull request** to show what a PR looks like.

## Talking points to hit while typing

| Step | Say this |
|---|---|
| `clone` | "This is a *repository* — the project folder plus its entire history." |
| `checkout -b` | "`main` stays stable. My work lives here until it's reviewed." |
| `status` / `diff` | "Always look before you commit. `diff` is the line-by-line truth." |
| `commit` | "A snapshot, not a save. The message is for the next person — often future you." |
| `push` | "Local → GitHub. Nothing is shared until you push." |
| PR on GitHub | "This is the review gate. This is exactly what your homework produces." |

## If something goes wrong live

- **Auth prompt / push rejected** — expected the first time; use it as a teaching moment about credentials, then push again.
- **Wrong branch** — `git switch -c correct-branch` carries uncommitted work over.
- **Total derail** — fall back to `git status` and narrate what it reports. Recovering calmly in front of the class is itself the lesson.
