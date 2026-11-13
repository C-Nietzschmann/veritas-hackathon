# CLAUDE.md

Repo of a team of 3 in the Veritas AI International High School Hackathon.
48 hours: Sat 14 Nov 2026 06:00 CET → Mon 16 Nov 05:59 CET. The team submits Sun 15 Nov 21:00 CET.
Stack: Python, Jupyter notebooks run in Google Colab.

## The vault comes first
`vault/` holds the team's shared notes: plan, protocols, project notes, decisions, logs. Tasks are not in the vault: they are GitHub issues on the project board (see "Tasks" below). Plain Markdown, opened in Obsidian (the repo folder itself is the Obsidian vault; shared settings are in `.obsidian/`).

A session-start hook (`.claude/settings.json` → `scripts/session-start.sh`) pulls the team's changes, switches on the `git sync` shortcut and prints the task board. If you don't see its output at the top of the session, run `sh scripts/session-start.sh` yourself.

Every session, before anything else:
1. Look at the board the hook printed.
2. Read `vault/Home.md`, `vault/Project/Idea.md` and `vault/Decisions/`.
3. Follow `vault/Protocols/AI Agent Protocol.md`. It is binding. The rest of `vault/Protocols/` explains the team's workflow: read the note that matches what you are doing (`Git Workflow`, `Colab Workflow`, `Evaluation Protocol`, `Task Protocol`, `Submission Checklist`).
4. Confirm the task with the user before writing code, and claim its card (see "Tasks"). Work on one task.

## Hackathon rules (these override everything)
- **No project code before kickoff** (Sat 14 Nov 06:00 CET). Before that, only docs and config.
- **The humans must understand every line.** Finalists are questioned live. Write the simplest code that works, explain before you write, and never hand over code the user hasn't read. Help the owner write the "How it works" comment that closes the task's issue.
- **Never invent results.** Every metric comes from code that was run. Say plainly when something is untested.
- **Credit everything.** New dataset, pre-trained model or library → `vault/Project/Credits.md` and `requirements.txt` right away.
- **This repo becomes public for blind judging.** No full names, school, phone numbers, emails or private links anywhere, including `vault/` and commit messages. People are referred to by their handle from `vault/Protocols/Team.md`.

## Repo rules
- The team works on `main` and shares with `git sync "message"` (alias in `.gitalias`: add all, commit, pull --rebase, push).
- **Before you sync, run `git status`.** `git sync` commits everything in the working tree. If there are changes that are not from your task or not ready, ask the user first, or commit only your files with `git add <paths>`.
- **Push only what runs.** `notebooks/main.ipynb` must run top to bottom in a fresh Colab session at every moment.
- Pull requests are optional, but **every pull request must be linked to its task**: open it with `sh scripts/task.sh pr <number>` (the description starts with `Closes #<number>`). No task yet: create the card first. The "Linked task" check fails an unlinked pull request.
- Never force-push. Never rewrite pushed history. If a pull stops with a conflict, show the user; don't resolve someone else's file by guessing.
- Stay in the user's lane: their notebook, their log, their part of `src/`, their cards on the board. Don't edit a file another teammate owns.
- Shared logic goes in `src/*.py`, not copied between notebooks.
- No secrets in git. Use Colab Secrets or a local `.env`, and list the variable name in `.env.example`.
- No datasets or model weights in git. Download them in the notebook from the public source.
- If CI or `main` is red, that comes first. See "MAIN BROKEN" in `vault/Protocols/Git Workflow.md`.
- After feature freeze (Sun 15 Nov 14:00 CET): bug fixes, evaluation, write-up and demo only.

## Vault conventions
- `[[wikilinks]]` between notes.
- The graph view is organised as hubs: `vault/Home.md` links to six hub notes (`Protocols`, `Tasks`, `Project`, `Decisions`, `Brief`, `Log`), and each hub links to its notes. New decision notes keep the `Up: [[Decisions]]` line from their template; a new log file starts with `Up: [[Log]]`. Don't add links from Home to individual notes.
- Link sparingly, so the graph stays readable: a note links up to its hub and sideways only to the note the reader goes to next. Mention other notes by name without brackets.
- Only edit the user's log in `vault/Log/` and notes you were asked to edit. Never delete or rewrite someone else's note.

## Tasks: GitHub is the project manager
Every task is an issue in this repo, shown as a card on the board: https://github.com/users/C-Nietzschmann/projects/3 (columns Todo, In Progress, Done). The vault is the network around the tasks and the place to double-check (rules, definition of done, submission checklist).

- See the board: `sh scripts/board.sh`
- New task: `sh scripts/task.sh new "Verb and object" P1 [technical|originality|impact|testing|communication]`. It lands in Todo by itself.
- Start: `sh scripts/task.sh start <number>` assigns it to the user and moves the card to In Progress. Do this before writing code. One card In Progress per person.
- Blocked: `sh scripts/task.sh block <number> "<on what>"`, and tell the user to say it on the call.
- Finished: draft the "How it works" comment (five plain bullets at most: what it does, why this way, where it could be wrong) and have the owner confirm they can explain it. End the push message with `closes #<number>`: GitHub closes the issue and the card moves to Done. Then `sh scripts/task.sh note <number> "<comment>"`. With nothing to push: `sh scripts/task.sh done <number> "<comment>"`.
- Never reassign, relabel or close a teammate's card.
- These need the GitHub CLI (`gh auth login`). If it is missing, say so and ask the user to make the change on the board in the browser.
- Details: `vault/Protocols/Task Protocol.md`.

## Evaluation
Baseline first, fixed seed, held-out test set used once at the end, results logged in `vault/Project/Evaluation.md`. Details: `vault/Protocols/Evaluation Protocol.md`.

## Sharing work: always the push skill
Whenever the user says push, sync, share, save or "done", and at the end of every session, run the `push` skill (`.claude/skills/push/SKILL.md`). It checks the work, updates the task's card and the log, runs `git sync`, and confirms GitHub's checks passed. Don't run a bare `git push`.

## Check-ins
When the user says "check-in", run the `checkin` skill (`.claude/skills/checkin/SKILL.md`): it gathers the facts since the last check-in and drafts the entry for `vault/Log/Sync notes.md`.

## Commands
- Install: `pip install -r requirements.txt`
- Test: `pytest -q`
- Share: `git sync "message"` (runs `scripts/check.sh` first)
- Board in the terminal: `git board` or `sh scripts/board.sh`
- Move a task: `sh scripts/task.sh new|start|block|unblock|note|pr|done …`
- Facts for a check-in: `sh scripts/checkin.sh [hours]`
