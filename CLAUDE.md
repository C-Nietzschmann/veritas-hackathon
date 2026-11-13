# CLAUDE.md

Code repo for a team of 3 in the Veritas AI International High School Hackathon.
48 hours: Sat 14 Nov 2026 06:00 CET → Mon 16 Nov 05:59 CET. The team submits Sun 15 Nov 21:00 CET.
Stack: Python, Jupyter notebooks run in Google Colab.

## The vault comes first
The plan, tasks, decisions and protocols are in the team's Obsidian vault: a separate private repo cloned at `vault/` (ignored by this repo).
If `vault/` is missing, ask the user to clone it: `git clone https://github.com/C-Nietzschmann/veritas-hackathon-vault.git vault`

Every session:
1. `git -C vault pull --rebase --autostash`
2. Read `vault/Home.md`, `vault/Project/Idea.md`, the open notes in `vault/Tasks/`, and `vault/Decisions/`.
3. Follow `vault/Protocols/AI Agent Protocol.md`. It is binding. The rest of `vault/Protocols/` explains the team's workflow: read the note that matches what you are doing (`Git Workflow`, `Colab Workflow`, `Evaluation Protocol`, `Task Protocol`, `Submission Checklist`).
4. Confirm the task with the user before writing code. Work on one task.

## Hackathon rules (these override everything)
- **No project code before kickoff** (Sat 14 Nov 06:00 CET). Before that, only docs and config.
- **The humans must understand every line.** Finalists are questioned live. Write the simplest code that works, explain before you write, and never hand over code the user hasn't read. Help the owner fill in "How it works" in the task note.
- **Never invent results.** Every metric comes from code that was run. Say plainly when something is untested.
- **Credit everything.** New dataset, pre-trained model or library → `vault/Project/Credits.md` and `requirements.txt` right away.
- **Blind review.** No names, school or personal details in this repo: not in code, comments, notebook outputs, README or commit messages you write.

## Repo rules
- Never commit to `main`. Branch `<handle>/<task-slug>` → pull request → CI green → `gh pr merge --squash --delete-branch`.
- One task per branch. Small pull requests.
- Notebooks have one owner each. Don't edit a notebook the user doesn't own. Shared logic goes in `src/*.py`.
- `notebooks/main.ipynb` is what gets submitted. It must run top to bottom in a fresh Colab session.
- No secrets in git. Use Colab Secrets or a local `.env`, and list the variable name in `.env.example`.
- No datasets or model weights in git. Download them in the notebook from the public source.
- If CI or `main` is red, that comes first. See "MAIN BROKEN" in `vault/Protocols/Git Workflow.md`.
- After feature freeze (Sun 15 Nov 14:00 CET): bug fixes, evaluation, write-up and demo only.

## Evaluation
Baseline first, fixed seed, held-out test set used once at the end, results logged in `vault/Project/Evaluation.md`. Details: `vault/Protocols/Evaluation Protocol.md`.

## End of a session
1. Commit, push, open or update the pull request.
2. Update the task note (`status`, `pr`) and append to `vault/Log/<handle>.md`.
3. `git -C vault add -A && git -C vault commit -m "<what changed>" && git -C vault pull --rebase && git -C vault push`

## Commands
- Install: `pip install -r requirements.txt`
- Test: `pytest -q`
