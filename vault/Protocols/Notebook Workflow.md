# Notebook Workflow

We run the notebooks on our own computers with Jupyter, and GitHub holds them. The judges open the notebook on GitHub, where it shows with all its outputs, so what we commit is what they see.

## Set up once
```bash
cd veritas-hackathon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt jupyter
```
Open notebooks in VS Code (pick the `.venv` kernel) or with `jupyter lab`. Run `source .venv/bin/activate` again in every new terminal.

## Open and save
- Work in the repo folder. The notebook is a file like any other: save it, then share it with the push skill or `sh scripts/task.sh ship <task> "message"`.
- `git sync` first, so you start from the latest `src/` and `requirements.txt`.
- New package? Add it to `requirements.txt` in the same push, or nobody else can run your notebook.

## Rules for notebooks
- **One owner per notebook** (see [[Git Workflow]]).
- **Before every push:** Restart kernel and run all. If it doesn't run top to bottom, it isn't done.
- **Set the seed** in the second cell and use it everywhere (`random`, `numpy`, the framework, the train/test split). Results must be repeatable.
- **Data comes from its source.** Download it in a cell from the public URL into `data/raw/` (ignored by git). Never a file that only exists on your computer.
- **Imports from `src/`:** the first cell is `%load_ext autoreload`, `%autoreload 2`, and `import sys; sys.path.insert(0, "..")`, so changes to `src/` are picked up without restarting.
- **Headings and one sentence per section.** The notebook is read by a reviewer: Problem → Data → Baseline → Model → Evaluation → Demo.
- **Keep outputs in `main.ipynb`**, so results are visible on GitHub without running. The check allows notebooks up to 25 MB. Clear outputs in personal scratch notebooks before committing if they are large.
- **No secrets in cells.** Put them in `.env` (ignored by git), list the name in `.env.example`, and read them with `os.environ["NAME"]` after `from dotenv import load_dotenv; load_dotenv()`.

## Training time
- There is no free cloud GPU in our setup. Pick data sizes and models that train in minutes on a laptop.
- If training takes more than 20 minutes, use less data or a smaller model first. We need many fast experiments, not one slow one.
- Long training: save checkpoints to `data/` (ignored by git), and say on the call whose laptop is busy.

## The fresh-run test
At Sun 18:00 someone who did not write `main.ipynb` runs it from a clean copy of GitHub:
```bash
git clone https://github.com/C-Nietzschmann/veritas-hackathon.git /tmp/fresh && cd /tmp/fresh
python3 -m venv .venv && . .venv/bin/activate && pip install -q -r requirements.txt jupyter
jupyter nbconvert --to notebook --execute --inplace notebooks/main.ipynb
```
Everything that breaks is a bug we fix before submitting.
