# Evaluation

The living record of how well it works. Owner: Data and evaluation lead. Method: [[Evaluation Protocol]].
Only numbers from code that was actually run go in here.

## Setup
- **Main metric:**
- **Label (since Sun 15 Nov, decision note A strike-off counts only after real accounts):** a company failed if, on or before the day 24 months after its incorporation, its first liquidation or administration started, or it was dissolved (removed from the register) after filing at least one set of accounts that were not dormant. Neither, or only later, means it did not fail. A members' voluntary liquidation, which is a solvent wind-down, is not counted as an insolvency. Code: `label_failures(mentions, traded=companies_that_traded(raw))`; `real_slice.load_slice` uses it (#171, #175). The tiny world keeps the earlier label. Earlier labels: liquidation or administration only, until 14 Nov (`count_dissolved=False`); then any dissolution, until 15 Nov (no `traded`, card #142).
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

### The matcher on validation: calibration (#88) and hand check (#89)
Is the matcher's `p` a probability? ADR-004 asks for this check before we call it one. Checked on the 9,171 validation pairs of the full local crawl, which the matcher never learned from. Label 1 is the same officer id, label 0 different ids.

- **Brier score:** 0.028, against a bar of 0.184 from always answering the training share of label 1 (0.41). Label 1 is much rarer among the validation pairs (730 of 9,171, 8%): always answering that share would score 0.073, worked out from those two counts. So the fairer comparison is 0.028 against 0.073.
- **Too sure at the top:** in the bin 0.6–0.8, 365 of 651 pairs have the same officer id (56%, interval 52–60%) at a mean `p` of 0.74. In the bin 0.8–1, 349 of 415 do (84%, interval 80–87%) at a mean `p` of 0.95.
- **Verdict:** `p` is a score, not a probability. The two top bins sit clearly below the diagonal.
- **A cause this check can't rule out:** the matcher learned from pairs where label 1 is common (41%) and is checked on pairs where it is rare (8%). A model fitted on the first mix gives a `p` that is too high on the second. So the gap in the top bins may come from that mismatch, and not only from label error or a matcher that is too sure. Not tested.

**Hand check (#89): judged by an AI (Claude Opus 5.5) at the user's request, not by hand.** 50 pairs with different officer ids that the same-name rule or the matcher links, sampled as in `jonas_real.ipynb` (seed 42). The rule: the same name and the same birth month and year gives yes; a different birth month or year gives no; evidence both ways gives unsure. The verdicts, by pair id only: `notebooks/cristiano_handcheck.csv`.

| Which method links the pair | Pairs | Same person | Two people | Unsure |
|---|---|---|---|---|
| Both | 24 | 24 | 0 | 0 |
| The same-name rule, not the matcher | 25 | 0 | 24 | 1 |
| The matcher only | 1 | 0 | 0 | 1 |
| All | 50 | 24 | 24 | 2 |

The "two people" pairs already get a `p` of at most 0.006, or none, so they don't touch the gap in the top bins. The "same person" pairs have a `p` from 0.720 to 0.947: if the AI is right, part of the gap is label error, one person under two officer ids. But the agreement is partly built in: the rule leans on birth month and year, and the matcher can't reach a `p` of 0.5 without the same birth month and year (weight 6.16, its largest after name similarity). So this is not independent evidence that the matcher is right. A person still has to look at the 2 unsure pairs and spot-check others.

The 50 pairs were spread over the three groups on purpose, so "24 of 50" is not a rate of anything. Card #89 asked for 50 pairs with a high `p`; only 25 of these have a `p` of 0.5 or more (the 24 both methods link and the 1 only the matcher links).

Source: `notebooks/cristiano_calibration.ipynb`, merged with pull request #174.

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
- **These rows use the earlier label** (any dissolution counts), from before the label changed on Sun 11:55. Rerun them before the write-up quotes them.
- **Ours flags nothing, so its zeros say nothing yet.** The failure line slopes down (34.1% without a predecessor, 14.4% with one, fitted on 5,362 training companies), so every validation company lands between CLEAR (10%) and FLAG (50%): 1,552 of 1,552 are NOT ENOUGH EVIDENCE. See the comments on #19.
- The counts are small: 9 false flags in the common band.

### The failure line, checked on validation (card #94)
**Validation, not test:** the 1,552 companies formed Oct–Dec 2021; one has no director on record and is left out. Each line is fitted on the 5,346 training companies with director records. Main label: the stricter one (a strike-off counts only after real accounts). Old label: every strike-off within 24 months counts. Printed by `notebooks/cristiano_failure_line.ipynb` (costs 10/2/1, seed 42), AI worker-1 with cristiano, Sun 11:21.

| Label | P(predecessor) | Companies | Failed | Line predicts | Really failed (95% interval) |
|---|---|---|---|---|---|
| Main (stricter) | 0 | 1,065 | 18 | 1.4% | 1.7% (1.1% to 2.7%) |
| Main (stricter) | Above 0, up to 0.5 | 381 | 5 | 1.4% | 1.3% (0.6% to 3.0%) |
| Main (stricter) | Above 0.5 | 105 | 0 | 1.8% | 0.0% (0.0% to 3.5%) |
| Old (every strike-off) | 0 | 1,065 | 407 | 34.1% | 38.2% (35.3% to 41.2%) |
| Old (every strike-off) | Above 0, up to 0.5 | 381 | 105 | 34.0% | 27.6% (23.3% to 32.3%) |
| Old (every strike-off) | Above 0.5 | 105 | 14 | 17.1% | 13.3% (8.1% to 21.1%) |

- **Main label: the line is nearly flat and under CLEAR, so FLAG never fires.** Fitted on train (77 failures), it goes from 1.4% with no likely insolvent predecessor to 1.8% with a certain one, so the decision layer answers CLEAR for every company with director records. On validation every group's prediction lies inside its interval (1.4% predicted, 1.5% failed on average over the 1,551 companies with director records), but the three intervals overlap: a likely insolvent predecessor makes no difference we can measure.
- **Old label: the line slopes down** (34.1% to 14.4%), so every company gets NOT ENOUGH EVIDENCE, and on validation it misses the two lower groups: the prediction lies below the interval at 0 and above it in the middle group.
- **Insolvency only can't replace the label:** 15 training companies and 1 validation company failed through liquidation or administration. Its line is flat at 0.3%, and 1 failure checks nothing.
- Reported as found: the labels, the costs and the line were not tuned.

## Where it fails
The matcher's wrong links on the 9,171 validation pairs (card #40): the 15 missed links (the same officer id, `p` under 0.5) and the 353 possible false links (different officer ids, `p` of 0.5 or more). Each example is a pair id, never a name.

| Kind of failure | Example | How often | Why we think it happens |
|---|---|---|---|
| Surname changed | `10c47a09f0c9674d` | 6 of the 15 missed links | The matcher leans hardest on name similarity (weight 17.88), so a new surname, for example after a marriage, outweighs the same birth month and year. |
| Middle name on one record only | `64adbfe28b96c411` | 3 of the 15 missed links | Name similarity compares whole names, so a middle name missing from one record pulls the score under 0.5 even with the same birth month and year. |
| Different first name | `74ee622353d9c6f5` | 2 of the 15 missed links | One record uses another first name (perhaps a middle name or a short form), and "English" against "British" counts as a different nationality. |
| Nationality written differently | `175e5f9bb2dc84b3` | 4 of the 15 missed links | Same name and birth month and year, but "British" against "Irish", or a second nationality on one record, counts as a mismatch. Together with a different postcode district, that keeps the score at 0.29. |
| Possible false link: common name | `06e42263c856e26b` | 43 of the 353 possible false links | Two people with a common surname can share a name and a birth month and year, and the matcher has no feature for how common a name is. Not proven wrong: the register gives two officer ids, but the hand check (#89, an AI's verdicts) judged pairs like these as one person, all 12 of these 43 that it included. |

The reasons were drafted by an AI (Claude Opus 5.5) and accepted by the user. Source: `notebooks/cristiano_calibration.ipynb`, section "Where the matcher fails (#40)": the missed links are sorted into kinds by the notebook's rule (`kind_of_miss`), the possible false links by name-commonness band.

## Limits
What we did not test, and who it might not work for.
- The 2021 companies' 24-month outcomes run into 2023, past the start of the test year, so some training labels use information from after some test companies were formed. Every 24-month window ends by December 2024, so every label is fully observed in today's register.
- The label counts a dissolution within 24 months only after real accounts were filed. A company that traded but never filed is missed, and a company closed by its owners with no debts still counts as failed: the register's profile doesn't say why a company was dissolved. The label before it (any dissolution) mostly counted companies that never filed anything and probably never traded: 95% of the early dissolutions among the 2021 training companies (phantodevc, #19). It turned the signal upside down, because experienced directors file their accounts. The first label (liquidation or administration only) had too few cases: 16 in all of 2021.
- The matcher learns from the register's officer ids: the same id counts as the same person, different ids as two people. The register sometimes gives one person two officer ids, so some "two people" labels are wrong, and the matcher is taught to miss exactly those people. 50 such pairs were judged by an AI at the user's request, not by hand (card #89, in the matcher section above), and we judge the method at the decision level against the officer-links baseline. Code: `labelled_pairs` in `src/resolve.py`.
- The decision layer can't flag any company with the failure line fitted on the crawl. Under the main label the line is nearly flat (1.4% to 1.8%) and under CLEAR, so every company with director records is cleared: on failure alone it does what "flag nothing" does. Under the old label the line slopes down and every company gets NOT ENOUGH EVIDENCE. See the subsection The failure line, checked on validation (card #94), above.
