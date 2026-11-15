# Evaluation

The living record of how well it works. Owner: Data and evaluation lead. Method: [[Evaluation Protocol]].
Only numbers from code that was actually run go in here.

## Setup
- **Main metric:**
- **Label:** a company failed if, on or before the day 24 months after its incorporation, its first liquidation or administration started or it was dissolved (removed from the register). Neither, or only later, means it did not fail. A members' voluntary liquidation, which is a solvent wind-down, is not counted as an insolvency, but a dissolution inside the 24 months counts whatever led to it. Until 14 Nov only liquidation or administration counted: see the decision note Early dissolution counts as failure (card #142). Code: `label_failures` in `src/evaluate.py`; `count_dissolved=False` gives the old label.
- **Data split:** train: formed Jan–Sep 2021 / validation: formed Oct–Dec 2021 / test: formed in 2022 · seed: none needed, because the split is by formation date (`incorporated_on`), so a seed doesn't change it; `SEED = 42` in the notebook covers anything random. A company formed outside these dates is in none of the three. Code: `split` in `src/evaluate.py`.
- **As-of rule:** a company formed on day t is judged only on claims (who directs or controls which company) that started on or before t (the day itself counts, because directors are usually appointed the day the company forms), with these dates emptied when they fall after t: when an appointment ended, and when an earlier company went insolvent or was dissolved; companies formed after t are left out, and company status is never used, because it has no date. Code: `history_as_of` in `src/evaluate.py` and `mentions_as_of` in `src/evidence.py`.
- **Test set first used on:** _not yet_

## Results
Newest row at the bottom. One row per experiment.

| # | When | What changed | Validation | Test | Notebook @ commit | Who |
|---|---|---|---|---|---|---|
| 0 | | Baseline: | | | | |

### Tiny world check (a code check, not a result)
The three baselines on the tiny world's 5 hand-made query companies (`tests/tiny_world.py`). One of them fails within 24 months: TW000002, the phoenix. These numbers show the code behaves the way the tiny world was built to show. They say nothing about real companies.

Printed by `score_methods` in `src/evaluate.py`, and pinned by `tests/test_score.py::test_the_baselines_on_the_tiny_world` @ fedf96b (merged in #130, jonas, Sat 13:52).

| Baseline | Flags | False flags | Misses | Precision | Recall |
|---|---|---|---|---|---|
| Flag nothing | 0 | 0 | 1 | none (nothing flagged) | 0 |
| Same name | 3 | 2 | 0 | 0.33 | 1 |
| Officer links | 0 | 0 | 1 | none (nothing flagged) | 0 |

Validation numbers follow once the crawl (#24) is in.

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

### False flags by name-commonness band, on validation (card #106)
**Validation, not test:** the 1,552 companies formed Oct–Dec 2021, from the merged crawl (#159). The false-flag rate is false flags / companies that didn't fail. A company's band is the commonest surname band among its directors on record when it was formed (`company_bands`, bands from `name_commonness`); one company has no director on record and is left out. Printed by `false_flags_by_band` in `src/evaluate.py`, from a scratch run of the same steps as `notebooks/jonas_real.ipynb` (costs 10/2/1, seed 42), phantodevc, Sun 10:18.

| Band | Companies | Didn't fail | Same name: false flags | Officer links: false flags | Ours (formula): false flags |
|---|---|---|---|---|---|
| Rare surname | 420 | 232 | 0 of 232 (0%) | 0 of 232 (0%) | 0 of 232 (0%) |
| Medium | 990 | 693 | 26 of 693 (3.8%) | 8 of 693 (1.2%) | 0 of 693 (0%) |
| Common surname | 141 | 100 | 9 of 100 (9.0%) | 0 of 100 (0%) | 0 of 100 (0%) |

- **Uneven, as the claim expects, for the same-name rule:** its false-flag rate grows with how common the surname is, from 0% to 3.8% to 9.0%. The rare band can't be falsely flagged by name at all: a surname seen once in the data matches no one.
- **Ours flags nothing, so its zeros say nothing yet.** The failure line slopes down (34.1% without a predecessor, 14.4% with one, fitted on 5,362 training companies), so every validation company lands between CLEAR (10%) and FLAG (50%): 1,552 of 1,552 are NOT ENOUGH EVIDENCE. See the comments on #19.
- The counts are small: 9 false flags in the common band.

### The failure line, checked on validation (card #94)
**Validation, not test:** the 1,552 companies formed Oct–Dec 2021; one has no director on record and is left out. The line is fitted on the 5,346 training companies with director records, under the team's label (insolvent or dissolved within 24 months). Printed by `notebooks/cristiano_failure_line.ipynb` (costs 10/2/1, seed 42), AI worker-1 with cristiano, Sun 11:03.

| P(predecessor) | Companies | Failed | Line predicts | Really failed (95% interval) |
|---|---|---|---|---|
| 0 | 1,065 | 407 | 34.1% | 38.2% (35.3% to 41.2%) |
| Above 0, up to 0.5 | 381 | 105 | 34.0% | 27.6% (23.3% to 32.3%) |
| Above 0.5 | 105 | 14 | 17.1% | 13.3% (8.1% to 21.1%) |

- **The line slopes down, so FLAG never fires.** Fitted on train, it falls from 34.1% with no likely insolvent predecessor to 14.4% with a certain one. Every P(fail) it gives lies between those two, below FLAG (50%) and above CLEAR (10%), so the decision layer answers NOT ENOUGH EVIDENCE for every company.
- **It misses the two lower groups:** the prediction lies below the interval at 0 and above it in the middle group; only the top group's is inside. On average it looks right (32.9% predicted, 33.9% failed, over the 1,551 companies with director records) because the two misses go opposite ways.
- **Insolvency only can't replace the label:** 15 training companies and 1 validation company failed through liquidation or administration. The line fitted on those 15 is flat at 0.3%, and 1 failure checks nothing.
- Reported as found: the label, the costs and the line were not tuned.

## Where it fails
From reading 10 to 20 wrong predictions.

| Kind of failure | Example | How often | Why we think it happens |
|---|---|---|---|
| | | | |

## Limits
What we did not test, and who it might not work for.
- The 2021 companies' 24-month outcomes run into 2023, past the start of the test year, so some training labels use information from after some test companies were formed. Every 24-month window ends by December 2024, so every label is fully observed in today's register.
- The label counts every dissolution within 24 months as a failure. The register's profile doesn't say why a company was dissolved, so this includes companies closed by their owners with no debts, and companies struck off because they never filed anything, which may never have traded. Some of these "failures" cost no supplier any money. The old label (liquidation or administration only) made the opposite mistake: it missed every company that was struck off leaving debts behind.
- The matcher learns from the register's officer ids: the same id counts as the same person, different ids as two people. The register sometimes gives one person two officer ids, so some "two people" labels are wrong, and the matcher is taught to miss exactly those people. We hand-check about 50 such pairs (card #89) and judge the method at the decision level against the officer-links baseline. Code: `labelled_pairs` in `src/resolve.py`.
- With the team's label and the failure line fitted on the crawl, the decision layer can't flag any company: the line slopes down, so every P(fail) stays below FLAG (and above CLEAR), and every company gets NOT ENOUGH EVIDENCE. See the subsection The failure line, checked on validation (card #94), above.
