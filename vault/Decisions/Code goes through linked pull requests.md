# Code goes through linked pull requests

Up: [[Decisions]]

- **Date:** 2026-11-13
- **Decided by:** the repo owner, before kickoff
- **Status:** decided

## Decision
When Claude shares code for a task, it goes through a pull request whose description starts with `Closes #<task>`. Notes in `vault/` still go straight to `main`. People working by hand may still push their own notebook straight to `main`.

## Why
- The board then shows, for every finished task, the pull request that finished it.
- The checks run before the code reaches `main`, not after.
- It costs us nothing: Claude does the branch, the pull request, the waiting and the merge.

The alternative was pushing everything straight to `main`, which is how we started (see the decision "One repo, everyone works on main").

## What it changes
- "Push" takes about a minute longer for code, because it waits for the checks.
- A pull request closes its task. If only part of a task is done and others need it now, split the task.
- Details and commands: [[Git Workflow]].
