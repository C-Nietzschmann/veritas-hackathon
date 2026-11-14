# Evaluation

The living record of how well it works. Owner: Data and evaluation lead. Method: [[Evaluation Protocol]].
Only numbers from code that was actually run go in here.

## Setup
- **Main metric:**
- **Label:** a company failed if its first liquidation or administration started on or before the day 24 months after its incorporation (a members' voluntary liquidation, which is a solvent wind-down, does not count), and no insolvency or a later one means it did not fail. Code: `label_failures` in `src/evaluate.py`.
- **Data split:** train __ / validation __ / test __ · seed: __
- **Test set first used on:** _not yet_

## Results
Newest row at the bottom. One row per experiment.

| # | When | What changed | Validation | Test | Notebook @ commit | Who |
|---|---|---|---|---|---|---|
| 0 | | Baseline: | | | | |

## Final result
Filled in after feature freeze, from the one test-set run.

- **Baseline:**
- **Our model:**
- **In plain words:**

## By group
The main metric for each group on the test set. Hackathon rule: say so if it's uneven.

| Group | Examples | Baseline | Our model |
|---|---|---|---|
| | | | |

## Where it fails
From reading 10 to 20 wrong predictions.

| Kind of failure | Example | How often | Why we think it happens |
|---|---|---|---|
| | | | |

## Limits
What we did not test, and who it might not work for.
-
