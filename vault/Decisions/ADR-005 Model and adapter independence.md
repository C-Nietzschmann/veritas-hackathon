# ADR-005 Model and adapter independence

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09, reviewed 07:35
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
Stages talk to each other only through the tables and graphs defined in ADR-001 to ADR-004. Swapping a data source or a method means changing one file and one line in the notebook.

## Why
- **A fair baseline.** The hard-merge baseline and our method run on identical input and are scored by the same code. That's a Finance must-have.
- **Parallel work.** One owner per file, so three people never edit the same code (Git Workflow).
- **Room to change.** The application can still move at scope lock. A new source is a new adapter, and nothing downstream changes.

The alternative was one notebook with everything inline. It's fastest for the first hour, then brings merge conflicts, no clean way to swap the baseline in, and changes that touch everything.

## What it changes
- `src/` holds one file per box: `evidence.py`, `ingest_<source>.py`, `baseline.py`, `graph.py`, `resolve.py`, `infer.py`, `decide.py`, `interface.py` and `evaluate.py`. `notebooks/main.ipynb` only calls them, top to bottom.
- Every method within a stage takes the same inputs and returns the same outputs. The notebook chooses which one to call.
- Each box has tests on the tiny world (`tests/tiny_world.py`), a hand-made example with known answers. The rule tests from Hard rules R1-R8 live in `tests/` too.
- Every file has one owner, set when the roles are agreed (task #3).
- A new library gets mentioned on the call and added to `requirements.txt` and Credits.

Next: [[Modules]]
