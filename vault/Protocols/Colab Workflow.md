# Colab Workflow

We build in Google Colab so nobody's laptop is a bottleneck and the reviewers can run exactly what we ran.

## Open and save
- **Open:** colab.research.google.com → File → Open notebook → **GitHub** tab → tick *Include private repos* and authorise once → choose the repo, your branch, the notebook.
- **Save:** File → **Save a copy in GitHub** → choose the repo, branch `main`, keep the file path as it is → write a real commit message. This puts your notebook straight on `main`, so only save a state that runs.
- Afterwards run `git sync` on your computer so your local copy has it too.
- Only ever save **your own** notebook this way. Saving replaces the whole file on GitHub.

## First cell of every notebook
So that a fresh session has the repo's code and packages:
```python
!git clone -q https://github.com/C-Nietzschmann/veritas-hackathon.git 2>/dev/null || git -C veritas-hackathon pull -q
%cd veritas-hackathon
!pip install -q -r requirements.txt
```
This works without a login once the repo is public. While it is private, keep everything the notebook needs inside the notebook, or switch the repo to public first.

## Rules for notebooks
- **One owner per notebook** (see [[Git Workflow]]).
- **Before every save to GitHub:** Runtime → **Restart session and run all**. If it doesn't run top to bottom, it isn't done.
- **Set the seed** in the second cell and use it everywhere (`random`, `numpy`, the framework, the train/test split). Results must be repeatable.
- **Data comes from its source.** Download it in a cell from the public URL. Never from your own Drive, because the reviewers don't have your Drive.
- **Headings and one sentence per section.** The notebook is read by a reviewer: Problem → Data → Baseline → Model → Evaluation → Demo.
- **Keep outputs in `main.ipynb`**, so results are visible without running. Clear outputs in personal scratch notebooks before committing if they are large.
- **No secrets in cells.** Use the key icon in the left sidebar (Secrets) and `from google.colab import userdata; userdata.get("NAME")`.

## GPU and sessions
- Runtime → Change runtime type → T4 GPU, only when you train. Free GPU time is limited and shared per account.
- Free sessions disconnect when idle and after some hours. Anything not saved to GitHub or Drive is gone. Save checkpoints of long trainings.
- If training takes more than 20 minutes, use less data or a smaller model first. We need many fast experiments, not one slow one.
- If someone hits a GPU limit, another teammate runs the training from the same notebook.

## The fresh-run test
At Sun 18:00 someone who did not write `main.ipynb` opens it from the GitHub link in a new Colab session, logged out of our team context if possible, and runs all cells. Everything that breaks is a bug we fix before submitting.
