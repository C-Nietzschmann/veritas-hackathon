# Git Workflow

One repo, one branch. Everyone works on `main` and shares small changes often. There are no pull requests to wait for, which keeps us fast and keeps the board current. The price is one rule: **push only what runs.**

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
Day to day we push straight to `main`. A pull request is for a big or risky change that should pass the checks before it reaches `main`.

**The rule: every pull request is linked to its task.** Its description starts with `Closes #12`. That makes the pull request show up next to the card on the board (column *Linked pull requests*), and merging it closes the task and moves the card to Done. A pull request without a linked task fails the "Linked task" check.

```bash
git switch -c <handle>/<task>       # a branch for the task
# ... work ...
git sync "Add baseline model"       # on a branch this pushes the branch, not main
sh scripts/task.sh pr 12            # opens the pull request, already linked to task 12
```
When the checks are green, merge it on GitHub with **Squash and merge**, then `git switch main && git sync`.

No task yet? Create the card first, then the pull request. By hand on github.com: write `Closes #12` as the first line of the description.

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
