# Git Workflow

One repo, and `main` is what we submit. There are two ways in:

- **Notes** (anything in `vault/`) go straight to `main` with `git sync`.
- **Code** goes through a **pull request linked to its task**. With Claude Code you just say "push": it opens the pull request, waits for the checks and merges it. Every finished card on the board then shows its pull request.

Working by hand, for example saving your own notebook from Colab, you may still push straight to `main`. Then one rule carries the weight: **push only what runs.**

## The loop
```bash
git sync                          # 1. get the latest before you start
# 2. work on your task, in your files
git sync "Add baseline model"     # 3. share it when it works
```
How `git sync` works and what to do when it complains: [[Sync]]

## Rules
- **Push only what runs.** Unfinished work is fine as long as it can't break anyone: a new file, a function nobody calls yet, your own scratch notebook. If it could break `main.ipynb` or `src/`, finish it first.
- **Stay in your lane.** Your notebook, your log, your part of `src/`. Two people editing one file is where conflicts come from. Need a change in someone else's file? Ask them.
- **Sync often.** Small changes merge cleanly. A day of unshared work does not.
- **Say what changed** in the message, in the imperative: "Add test split", "Fix label leak in features".
- **Never `git push --force`.** It deletes other people's work.
- **Touching something shared** (`src/`, `requirements.txt`, `main.ipynb`)? Say it on the call before you push, and post `PUSHED:` in the chat after.

## Notebooks
Notebooks are JSON, and git merges them badly. So:
- **One owner per notebook.** Only the owner edits it. Others say what they need.
- Personal work goes in `notebooks/<handle>_<topic>.ipynb`.
- The submitted notebook is `notebooks/main.ipynb`. Its owner is the Product lead.
- Code that more than one notebook needs lives in `src/*.py` and is imported.
- Colab saves straight to GitHub. Run `git sync` afterwards so your computer has it too.

More in [[Colab Workflow]].

## What stays out of git
- Secrets: API keys, tokens, `.env`. CI rejects a committed `.env`.
- Datasets and model weights bigger than a few MB. Download them in the notebook from their public source, so the reviewers can run it too.
- Full names, school, phone numbers, emails, private links. The repo becomes public.

## CI: is main green?
`git sync` checks your files on your computer before sharing them (see [[Sync]]). Then every push that changes code is checked again on GitHub (notes-only pushes are skipped). On github.com the latest commit shows ✓ or ✗, and GitHub emails whoever pushed a failure.
It checks: no secrets, no conflict markers, no huge files, every notebook valid, and `pytest` passes once `tests/` has tests. An empty `tests/` folder is fine.

## MAIN BROKEN
`main.ipynb` doesn't run, or CI shows ✗.
1. Whoever notices posts `MAIN BROKEN: <what fails>` in the chat. **Nobody pushes code** until it's fixed. Notes are fine.
2. Whoever pushed last owns the fix.
3. If the fix isn't obvious within 15 minutes, undo instead:
   ```bash
   git log --oneline -5          # find the commit that broke it
   git revert <commit>           # makes a new commit that undoes it
   git sync "Revert broken commit"
   ```
   Then repair in peace and push again when it works.
4. Post `MAIN OK` when it runs again.

## Pull requests
**The rule: every pull request is linked to its task.** Its description starts with `Closes #12`. That makes the pull request show up next to the card on the board (column *Linked pull requests*), and merging it closes the task and moves the card to Done. A pull request without a linked task fails the "Linked task" check.

One command does the whole chain:
```bash
sh scripts/task.sh ship 12 "Add baseline model"
```
It puts your changes on a branch for task 12, checks them, pushes, opens the linked pull request, waits for GitHub's checks, merges, and brings you back to an up-to-date `main`. If a check fails, nothing is merged: fix it and run the same command again.

Not finished yet, but want to share or stop for the day?
```bash
sh scripts/task.sh pr 12 "Add test split"
```
The same, but the pull request stays open and you stay on the task's branch (`task-12`). Run `ship` when it's done.

Claude Code runs these for you when you say "push". By hand on github.com: write `Closes #12` as the first line of the pull request's description, and merge with **Squash and merge**.

No task yet? Create the card first, then the pull request.

## Kickoff setup (once, by the Model lead)
After 06:00 CET on Saturday, the first push creates the structure:
```
notebooks/main.ipynb
src/__init__.py
tests/
requirements.txt
```
From then on CI installs `requirements.txt` and runs `pytest` if `tests/` has tests.

## When the repo goes public (once, by the repo owner)
Import `.github/rulesets/main.json`: Settings → Rules → Rulesets → New ruleset → Import a ruleset. From then on GitHub itself refuses force-pushes to `main` and deleting it. GitHub only offers rulesets on public repos (or with a paid plan), so this can't be switched on earlier.
