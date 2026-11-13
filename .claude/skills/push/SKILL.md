---
name: push
description: Share the current work with the team the proper way - checks, log, then notes straight to main and code through a pull request linked to its task, and confirm GitHub's checks passed. Use whenever the user says push, sync, share, save, upload, ship, "I'm done", or finishes a task, and at the end of every working session.
---

# Push

One routine for sharing work. Do the steps in order and don't skip any. Keep the user informed in short lines.

Two kinds of push:
- **Notes push:** only files in `vault/` changed. Goes straight to `main` with `git sync`.
- **Code push:** anything outside `vault/` changed. Goes through a pull request that is linked to its task. That is a team rule: every finished task shows its pull request on the board.

## 1. Look at what changed
Run `git status --short` and `git branch --show-current`.
- Nothing changed: run `git sync` anyway to fetch the team's changes, report, stop.
- Only files in `vault/` changed and you are on `main`: this is a notes push. Skip step 2.
- Anything else is a code push. It needs a task: which card on the board (`sh scripts/board.sh`) is this for? If there is none, create it first (`sh scripts/task.sh new "Verb and object" P1`, then `sh scripts/task.sh start <number>`).
- Files changed that are not part of the user's task, or belong to a teammate (their notebook, their log): stop and ask the user before going on.

## 2. Is the code ready? (code pushes only)
- If `tests/` exists, run `pytest -q`. A failure stops the push: fix it first. Exit code 5 ("no tests ran") is not a failure: `tests/` just has no tests yet.
- If a notebook changed, ask the user: "Did it run top to bottom with Restart and run all?" If not, wait.
- Ask yourself: is the task finished? Finished means the card's "Done when" boxes are all true. This decides step 4.

## 3. Bookkeeping
Do what applies, then show the user a two-line summary of what you did.
- **"How it works"** (finished tasks only): draft it in at most five plain bullets (what it does, why this way, where it could be wrong), and ask the owner to read it and say whether they could explain it out loud. If they can't, explain it to them first. That is a hackathon rule, not a formality.
- **Blocked instead of finished:** `sh scripts/task.sh block <number> "<on what>"`, and tell the user to say it on the call.
- **Log** (`vault/Log/<handle>.md`): append an entry from `vault/Templates/Session Log.md`, including the "AI used for" line, honestly.
- **Credits** (`vault/Project/Credits.md`): any new dataset, pre-trained model or library.
- **Evaluation** (`vault/Project/Evaluation.md`): one row per new result. Only numbers that came from code that was run in this session or that the user gives you. Never estimate.

## 4. Share
The message says what changed, in the imperative ("Add baseline model").

**Notes push:** `git sync "<message>"`. "Update log" is fine.

**Code push, task finished:**
```bash
sh scripts/task.sh ship <number> "<message>"
```
This one command puts the changes on a branch for the task, runs `scripts/check.sh`, pushes, opens a pull request whose description starts with `Closes #<number>`, waits for GitHub's checks, merges it, and returns to an up-to-date `main`. The merge closes the task and the board moves the card to Done, with the pull request shown next to it. Then add the explanation: `sh scripts/task.sh note <number> "<How it works …>"`.

**Code push, task not finished** (sharing progress, or stopping for now):
```bash
sh scripts/task.sh pr <number> "<message>"
```
Same, but the pull request stays open and you stay on the task's branch. The card shows the open pull request. Run `ship` when the task is finished. If teammates need part of the work on `main` right now, split the task: finish and ship the part that is done under its own card.

If something goes wrong:
- `scripts/check.sh` reports a problem (a secret, a conflict marker, a file too big, a broken notebook): fix the cause and run the command again. Never work around the check.
- The checks fail on the pull request: nothing was merged. Read `gh pr checks`, fix it on the branch, run `ship` again.
- The merge is refused, or a pull stops with a conflict: stop. Show the user the file and follow `vault/Protocols/Sync.md`. Don't resolve a teammate's file by guessing; `git rebase --abort` is always safe.
- `git sync` is not a known command: switch the shortcuts on once with `git config --local include.path ../.gitalias`.
- No `gh` on this computer: a pull request can't be opened from here. Tell the user, and fall back to `git sync "<message>, closes #<number>"`, which pushes to `main` and still closes the task.

## 5. Confirm `main` is green (code pushes that were merged)
The pull request's checks passed before the merge. This confirms the check on the merged result. Watch the run for your own commit, not "the latest run on main":
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
- Failed: run `gh run view --log-failed`, tell the user what broke in one sentence, and fix it now through a new linked pull request. If the fix isn't obvious within a few minutes, `git revert` the commit, and tell the user to post `MAIN BROKEN` in the team chat (see `vault/Protocols/Git Workflow.md`).

## 6. Report
Three lines at most: what was shared (with the pull request number for a code push), whether the checks passed, and what is next. Finish with the board: `sh scripts/board.sh`.
