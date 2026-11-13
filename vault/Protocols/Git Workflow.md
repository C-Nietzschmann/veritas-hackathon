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
- **Stay in your lane.** Your notebook, your task note, your log, your part of `src/`. Two people editing one file is where conflicts come from. Need a change in someone else's file? Ask them.
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
Every push that changes code is checked automatically (notes-only pushes are skipped). On github.com the latest commit shows ✓ or ✗, and GitHub emails whoever pushed a failure.
It checks: no `.env` committed, every notebook is valid, and `pytest` passes once `tests/` exists.

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

## For something risky
A big rewrite, or a library that might not work? Do it on a branch so `main` stays safe:
```bash
git switch -c <handle>/<idea>
# ... work, commit ...
git push -u origin HEAD
```
When it works: `git switch main && git merge <handle>/<idea> && git sync`. If it doesn't: switch back to `main` and forget the branch. Remember that task and board updates made on a branch are invisible to the others until you merge.

## Kickoff setup (once, by the Model lead)
After 06:00 CET on Saturday, the first push creates the structure:
```
notebooks/main.ipynb
src/__init__.py
tests/
requirements.txt
```
From then on CI installs `requirements.txt` and runs `pytest` if `tests/` has tests.
