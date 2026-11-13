---
name: push
description: Share the current work with the team the proper way - checks, task note, log, git sync, then confirm GitHub's checks passed. Use whenever the user says push, sync, share, save, upload, ship, "I'm done", or finishes a task, and at the end of every working session.
---

# Push

One routine for sharing work. Do the steps in order and don't skip any. Keep the user informed in short lines.

## 1. Look at what changed
Run `git status --short`.
- Nothing changed: run `git sync` anyway to fetch the team's changes, report, stop.
- Only files in `vault/` changed: this is a notes push. Skip steps 2 and 5.
- Files changed that are not part of the user's task, or belong to a teammate (their notebook, their task note, their log): stop and ask the user before going on.

## 2. Is the code ready? (code pushes only)
Everyone shares `main`, so only code that runs may be pushed.
- If `tests/` exists, run `pytest -q`. A failure stops the push: fix it first. Exit code 5 ("no tests ran") is not a failure: `tests/` just has no tests yet.
- If a notebook changed, ask the user: "Did it run top to bottom with Restart and run all?" If not, wait.
- If the work is unfinished, it may only be pushed when it can't break anything (a new file, a function nothing calls yet). Otherwise offer to push the notes only.

## 3. Bookkeeping in the vault
Do what applies, then show the user a two-line summary of what you wrote.
- **Task note** (`vault/Tasks/`): set `status` (`doing`, `blocked` or `done`) and `link`. For a finished task, draft "How it works" in at most five plain bullets, and ask the owner to read it and say whether they could explain it out loud. If they can't, explain it to them first. That is a hackathon rule, not a formality.
- **Log** (`vault/Log/<handle>.md`): append an entry from `vault/Templates/Session Log.md`, including the "AI used for" line, honestly.
- **Credits** (`vault/Project/Credits.md`): any new dataset, pre-trained model or library.
- **Evaluation** (`vault/Project/Evaluation.md`): one row per new result. Only numbers that came from code that was run in this session or that the user gives you. Never estimate.

## 4. Share
Run `git sync "<message>"`. The message says what changed, in the imperative ("Add baseline model"). For a notes push, "Update board and log" is fine.

`git sync` first runs `scripts/check.sh`. If it reports a problem (a secret, a conflict marker, a file too big, a broken notebook), fix the cause and run it again. Never work around the check.

If `git sync` is not a known command, switch the shortcuts on once: `git config --local include.path ../.gitalias`

If the pull stops with a conflict: stop. Show the user the file and follow `vault/Protocols/Sync.md`. Don't resolve a teammate's file by guessing; `git rebase --abort` is always safe.

## 5. Confirm GitHub's checks (code pushes only)
Watch the run for your own commit, not "the latest run on main": right after a push that is often the previous run (a ✓ that says nothing about yours) or a teammate's.
```bash
sha=$(git rev-parse HEAD); id=""
for i in 1 2 3 4 5 6; do
  id=$(gh run list --commit "$sha" --limit 1 --json databaseId -q '.[0].databaseId')
  [ -n "$id" ] && break; sleep 5
done
if [ -n "$id" ]; then gh run watch "$id" --exit-status; else echo "no CI run for $sha"; fi
```
- No run after 30 seconds: the push changed only `vault/` (CI skips those), or GitHub is slow. Look for the ✓ next to the commit on github.com.
- Passed: say so.
- Failed: run `gh run view --log-failed`, tell the user what broke in one sentence, and fix it now. If the fix isn't obvious within a few minutes, `git revert` the commit and `git sync`, and tell the user to post `MAIN BROKEN` in the team chat (see `vault/Protocols/Git Workflow.md`).
- `gh` isn't installed or signed in: tell the user to look for the ✓ next to the latest commit on github.com.

## 6. Report
Three lines at most: what was shared, whether the checks passed, and what is next. Finish with the board: `sh scripts/board.sh`.
