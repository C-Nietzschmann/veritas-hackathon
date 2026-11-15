# TENSEGRITY

**Is this young company run by people whose earlier companies went bust?** A small UK supplier types in a customer's company number and gets back FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the evidence graph behind it and how sure we are. Built from public Companies House data for the Veritas AI International High School Hackathon, 14–15 November 2026 (Finance track).

*This project is a prototype and is not financial advice.*

**See it without running anything:** open [`notebooks/main.ipynb`](notebooks/main.ipynb) on GitHub. It reads top to bottom: problem, data, baseline, model, evaluation, demo.

## Run it
You need Python 3.10 or newer. The notebook runs on a small hand-made "tiny world" with invented companies and people, so it needs no API key and no download:
```bash
git clone https://github.com/C-Nietzschmann/veritas-hackathon.git && cd veritas-hackathon
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt jupyter
jupyter lab notebooks/main.ipynb
```
Then Run → Run All Cells. To run the tests: `pip install pytest`, then `pytest -q`.

To crawl real Companies House data you need your own free API key from the [Companies House developer hub](https://developer.company-information.service.gov.uk/). Put it in a file called `.env` (see `.env.example`); git never shares that file. The raw data stays on your computer in `data/raw/` and is never put in this repo.

## What's in this repo
| Path | What |
|---|---|
| `notebooks/main.ipynb` | The project, top to bottom: data, baseline, model, evaluation, demo |
| `src/` | Code shared between notebooks |
| `tests/` | Checks that run when code is pushed |
| `requirements.txt` | Python packages |
| `vault/` | How we worked: plan, task board, decisions, evaluation log. An Obsidian vault, readable as plain Markdown |

## Credits
Full list with links and licences: [`vault/Project/Credits.md`](vault/Project/Credits.md).
- **Data:** the [Companies House public data API](https://developer.company-information.service.gov.uk/). Names, birth dates and postcodes of real directors are never shown: outputs use masked labels.
- **Libraries:** numpy, pandas, scikit-learn, matplotlib, requests, python-dotenv, ipywidgets, Jupyter, pytest.
- **Ideas:** Chow's rule (1970) for when to abstain instead of deciding.
- **AI tools:** Claude and Claude Code (Anthropic) helped write and review code, tests and notes. Our rules for using them are in Credits.

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
- Code goes through a pull request that names its task (`Closes #12`), or its check fails. `sh scripts/task.sh ship 12 "message"` does the whole chain.
- No secrets, no full names, no school anywhere in this repo. It becomes public for the judges.
- With Claude Code, say "push" instead: it also updates your card on the board and your log, and confirms the checks on GitHub.
- AI agents: read `CLAUDE.md` first.
