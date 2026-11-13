# CLAUDE.md

Repo of a team of 3 in the Veritas AI International High School Hackathon.
48 hours: Sat 14 Nov 2026 06:00 CET → Mon 16 Nov 05:59 CET. The team submits Sun 15 Nov 21:00 CET.
Stack: Python, Jupyter notebooks run in Google Colab.

## The vault comes first
`vault/` holds the team's shared notes: plan, tasks, decisions, protocols. Plain Markdown, opened in Obsidian (the repo folder itself is the Obsidian vault; shared settings are in `.obsidian/`).

Every session, before anything else:
1. `git pull --rebase --autostash`, then `sh scripts/board.sh` to see the task board. If `git sync` is not a known command yet: `git config --local include.path ../.gitalias`
2. Read `vault/Home.md`, `vault/Project/Idea.md`, the open notes in `vault/Tasks/`, and `vault/Decisions/`.
3. Follow `vault/Protocols/AI Agent Protocol.md`. It is binding. The rest of `vault/Protocols/` explains the team's workflow: read the note that matches what you are doing (`Git Workflow`, `Colab Workflow`, `Evaluation Protocol`, `Task Protocol`, `Submission Checklist`).
4. Confirm the task with the user before writing code. Work on one task.

## Hackathon rules (these override everything)
- **No project code before kickoff** (Sat 14 Nov 06:00 CET). Before that, only docs and config.
- **The humans must understand every line.** Finalists are questioned live. Write the simplest code that works, explain before you write, and never hand over code the user hasn't read. Help the owner fill in "How it works" in the task note.
- **Never invent results.** Every metric comes from code that was run. Say plainly when something is untested.
- **Credit everything.** New dataset, pre-trained model or library → `vault/Project/Credits.md` and `requirements.txt` right away.
- **This repo becomes public for blind judging.** No full names, school, phone numbers, emails or private links anywhere, including `vault/` and commit messages. People are referred to by their handle from `vault/Protocols/Team.md`.

## Repo rules
- The team works on `main` and shares with `git sync "message"` (alias in `.gitalias`: add all, commit, pull --rebase, push).
- **Before you sync, run `git status`.** `git sync` commits everything in the working tree. If there are changes that are not from your task or not ready, ask the user first, or commit only your files with `git add <paths>`.
- **Push only what runs.** `notebooks/main.ipynb` must run top to bottom in a fresh Colab session at every moment.
- Never force-push. Never rewrite pushed history. If a pull stops with a conflict, show the user; don't resolve someone else's file by guessing.
- Stay in the user's lane: their notebook, their task note, their log, their part of `src/`. Don't edit a file another teammate owns.
- Shared logic goes in `src/*.py`, not copied between notebooks.
- No secrets in git. Use Colab Secrets or a local `.env`, and list the variable name in `.env.example`.
- No datasets or model weights in git. Download them in the notebook from the public source.
- If CI or `main` is red, that comes first. See "MAIN BROKEN" in `vault/Protocols/Git Workflow.md`.
- After feature freeze (Sun 15 Nov 14:00 CET): bug fixes, evaluation, write-up and demo only.

## Vault conventions
- `[[wikilinks]]` between notes. One task per file in `vault/Tasks/`, with the YAML properties from `vault/Templates/Task.md`.
- Only edit task notes the user owns, the user's log in `vault/Log/`, and notes you were asked to edit. Never delete or rewrite someone else's note.

## Evaluation
Baseline first, fixed seed, held-out test set used once at the end, results logged in `vault/Project/Evaluation.md`. Details: `vault/Protocols/Evaluation Protocol.md`.

## Sharing work: always the push skill
Whenever the user says push, sync, share, save or "done", and at the end of every session, run the `push` skill (`.claude/skills/push/SKILL.md`). It checks the work, updates the task note and log, runs `git sync`, and confirms GitHub's checks passed. Don't run a bare `git push`.

## Commands
- Install: `pip install -r requirements.txt`
- Test: `pytest -q`
- Share: `git sync "message"` (runs `scripts/check.sh` first)
- Board in the terminal: `git board` or `sh scripts/board.sh`
