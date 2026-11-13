# Tasks on GitHub, the vault is the network

Up: [[Decisions]]

- **Date:** 2026-11-13
- **Decided by:** the repo owner, before kickoff
- **Status:** decided

## Decision
GitHub is our project manager: every task is an issue, shown on the [board](https://github.com/users/C-Nietzschmann/projects/3). The Obsidian vault is the network of everything around the tasks: protocols, project notes, decisions, logs. It is also where we double-check: the rules, the definition of done and the submission checklist live here.

## Why
- The board changes many times an hour. On GitHub a change is visible to all three of us at once, and on a phone. In the vault it only arrived after a `git sync`.
- The vault's strength is linked notes that stay true for the whole weekend. Mixing fast-changing task notes into it made the graph noisy.

The alternative was keeping one note per task in the vault with a board built from them.

## What it changes
- No more task notes in the vault. The "How it works" explanation is the closing comment on the issue.
- Changing a task needs no `git sync`.
- Claude reads and moves tasks through the GitHub command-line tool (`gh`), so each of us runs `gh auth login` once. Without it, use the board in the browser.
