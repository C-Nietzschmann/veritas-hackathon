# Hackathon project

Our entry for the Veritas AI International High School Hackathon, 14–15 November 2026.

<!-- After kickoff, replace this block with: project name, one line on what it does, and the Open in Colab badge. -->
> Nothing here yet. All project code is written during the 48 hours, starting Sat 14 Nov 00:00 ET.

## Run it
<!-- Fill in before submitting. A reviewer must be able to follow this with no help. -->
1. Open `notebooks/main.ipynb` in Google Colab.
2. Runtime → Run all.

## What's in this repo
| Path | What |
|---|---|
| `notebooks/main.ipynb` | The project, top to bottom: data, baseline, model, evaluation, demo |
| `src/` | Code shared between notebooks |
| `tests/` | Checks that run when code is pushed |
| `requirements.txt` | Python packages |
| `vault/` | How we worked: plan, task board, decisions, evaluation log. An Obsidian vault, readable as plain Markdown |

## Credits
<!-- Datasets, pre-trained models and libraries, with links. Copied from vault/Project/Credits.md before submitting. -->

---

## For the team

Setup, once:
```bash
git clone https://github.com/C-Nietzschmann/veritas-hackathon.git
cd veritas-hackathon
git config --local include.path ../.gitalias
```
Then open the `veritas-hackathon` folder in Obsidian (*Open folder as vault*) and start at `vault/Home`. Full steps: `vault/Setup.md`.

Day to day there is one command. It checks your files, saves your changes, gets everyone else's and uploads yours:
```bash
git sync "what I changed"
```

- Everyone works on `main`. Push only what runs.
- Tasks are issues on the [project board](https://github.com/users/C-Nietzschmann/projects/3): Todo, In Progress, Done.
- One owner per notebook, so two people never edit the same file.
- No secrets, no full names, no school anywhere in this repo. It becomes public for the judges.
- With Claude Code, say "push" instead: it also updates your card on the board and your log, and confirms the checks on GitHub.
- AI agents: read `CLAUDE.md` first.
