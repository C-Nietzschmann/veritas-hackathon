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
| `tests/` | Checks that run on every pull request |
| `requirements.txt` | Python packages |

## Credits
<!-- Datasets, pre-trained models and libraries, with links. Copied from the team notes before submitting. -->

---

## For the team

Setup, once:
```bash
git clone https://github.com/C-Nietzschmann/veritas-hackathon.git
cd veritas-hackathon
git clone https://github.com/C-Nietzschmann/veritas-hackathon-vault.git vault
```
Then open `vault/` in Obsidian and start at `Home`. The plan, the task board and all protocols live there. `vault/` is a separate private repo and is ignored by this one.

How we work here:
- Never commit to `main`. Branch `<handle>/<task>`, pull request, CI green, squash-merge.
- One owner per notebook.
- No secrets, no names, no school in this repo.
- AI agents: read `CLAUDE.md` first.

`main` protection (pull request and green CI required) is defined in `.github/rulesets/main.json`. GitHub only enforces it on public repos, so apply it when the repo goes public:
```bash
gh api -X POST repos/C-Nietzschmann/veritas-hackathon/rulesets --input .github/rulesets/main.json
```
