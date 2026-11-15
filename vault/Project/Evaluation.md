# Evaluation

The living record of how well it works. Owner: Data and evaluation lead. Method: [[Evaluation Protocol]].
Only numbers from code that was actually run go in here.

## Setup
- **Main metric (decision note The main metric is unconfirmed links next to recall, Sun 15 Nov, before the test set was opened):** the links to an earlier insolvent company that the register doesn't confirm (different officer ids; fewer is better), overall and for common surnames, read next to recall against the register (the share of same-officer-id links a method finds). Baseline: the same-name rule.
- **Label (since Sun 15 Nov, decision note A strike-off counts only after real accounts):** a company failed if, on or before the day 24 months after its incorporation, its first liquidation or administration started, or it was dissolved (removed from the register) after filing at least one set of accounts that were not dormant. Neither, or only later, means it did not fail. A members' voluntary liquidation, which is a solvent wind-down, is not counted as an insolvency. Code: `label_failures(mentions, traded=companies_that_traded(raw))`; `real_slice.load_slice` uses it (#171, #175). The tiny world keeps the earlier label. Earlier labels: liquidation or administration only, until 14 Nov (`count_dissolved=False`); then any dissolution, until 15 Nov (no `traded`, card #142).
- **Data split:** train: formed Jan–Sep 2021 / validation: formed Oct–Dec 2021 / test: formed in 2022 · seed: none needed, because the split is by formation date (`incorporated_on`), so a seed doesn't change it; `SEED = 42` in the notebook covers anything random. A company formed outside these dates is in none of the three. Code: `split` in `src/evaluate.py`.
- **As-of rule:** a company formed on day t is judged only on claims (who directs or controls which company) that started on or before t (the day itself counts, because directors are usually appointed the day the company forms), with these dates emptied when they fall after t: when an appointment ended, and when an earlier company went insolvent or was dissolved; companies formed after t are left out, and company status is never used, because it has no date. Code: `history_as_of` in `src/evaluate.py` and `mentions_as_of` in `src/evidence.py`.
- **Test set first used on:** Sun 15 Nov 14:11, main.ipynb @ 74d8a97
- **One earlier contact with the 2022 files, no result:** `notebooks/cristiano_calibration.ipynb` ran the adapter over the whole crawl, 2022 files included, before it split the companies. Its saved output counts the 2022 companies (6,847) and shows nothing else about them: no label, no rate, no score. Its training and validation pair counts (145,518 and 9,171) are the same as in `main.ipynb`, where the 2022 files are dropped first.

## Results
Newest row at the bottom. One row per experiment. Validation and Test give the main metric: the links to an earlier insolvent company that the register doesn't confirm, how many of them are for common surnames, and recall against the register.

| # | When | What changed | Validation | Test | Notebook @ commit | Who |
|---|---|---|---|---|---|---|
| 0 | Sun 15 Nov | Baseline: the same-name rule | 375 unconfirmed, 85 for common surnames, recall 0.988 | 1,537 unconfirmed, 442 for common surnames, recall 0.980 | main.ipynb @ f38cebd (validation), @ 74d8a97 (test) | cristiano (validation, #182), jonas (test, #45) |
| 1 | Sun 15 Nov | The matcher (score 0.5 or more) | 130 unconfirmed, 9 for common surnames, recall 0.952 | 534 unconfirmed, 112 for common surnames, recall 0.918 | main.ipynb @ f38cebd (validation), @ 74d8a97 (test) | cristiano (validation, #182), jonas (test, #45) |

### Tiny world check (a code check, not a result)
The three baselines on the tiny world's 5 hand-made query companies (`tests/tiny_world.py`). One of them fails within 24 months: TW000002, the phoenix. These numbers show the code behaves the way the tiny world was built to show. They say nothing about real companies.

Printed by `score_methods` in `src/evaluate.py`, and pinned by `tests/test_score.py::test_the_baselines_on_the_tiny_world` @ fedf96b (merged in #130, jonas, Sat 13:52).

| Baseline | Flags | False flags | Misses | Precision | Recall |
|---|---|---|---|---|---|
| Flag nothing | 0 | 0 | 1 | none (nothing flagged) | 0 |
| Same name | 3 | 2 | 0 | 0.33 | 1 |
| Officer links | 0 | 0 | 1 | none (nothing flagged) | 0 |

The validation numbers from the real crawl are in the sections below.

### Blocking recall, on validation (card #85)
Blocking is the cheap rule that proposes which pairs of person records the matcher compares: the same surname and first initial, or the same birth month and year with a similar surname (`candidate_pairs` in `src/resolve.py`). A true pair it never proposes can never be matched (ADR-003), so we count how many of the register's own links it keeps. A true pair is two records with the same officer id.

| Split | Same-officer-id pairs | Kept by blocking | Recall |
|---|---|---|---|
| Train | 103,870 | 103,835 | 99.97% |
| Validation | 730 | 724 | 99.18% |

- **The rule stays as it is:** the card's bar for loosening it was a recall under about 90%.
- **What it costs:** 263,601 candidate pairs out of 2,165,181,915 possible, from 65,806 person records. Blocking took 26.4 s on the real slice (one run, Sun 15 Nov, cristiano's computer).
- **What it can't see:** a person the register split across two officer ids has no label, so this number says nothing about whether blocking keeps those pairs.
- **Not looked at:** why the 6 validation pairs were dropped.

Source: printed by `notebooks/main.ipynb` @ f38cebd (#182), section "Model", on the merged crawl (#159) with the 2022 companies' files dropped. Recounted with the same steps in a scratch script on Sun 15 Nov, which gave the same counts and the timing.

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

**The same 50 pairs, checked by a person (jonas, Sun 15 Nov, card #46).** Blind: a page made by `real_slice.handcheck_html`, in pair-id order, with no group, band, match score or AI verdict. It shows the two records side by side: the director's pseudonym (the same pseudonym means the same name), whether the two names match after normalising, birth month and year, nationality, postcode area, company and dates, and the co-directors' pseudonyms. The verdicts, by pair id only: `notebooks/jonas_handcheck.csv`.

| Which method links the pair | Pairs | Same person | Two people | Same as the AI |
|---|---|---|---|---|
| Both | 24 | 24 | 0 | 24 of 24 |
| The same-name rule, not the matcher | 25 | 0 | 25 | 24 of 24, plus 1 the AI left unsure |
| The matcher only | 1 | 1 | 0 | the AI left it unsure |
| All | 50 | 25 | 25 | 48 of the 48 the AI decided |

- **The person agrees with the AI on all 48 pairs it decided, and settles the 2 it left unsure:** the same-name pair is two people, the matcher-only pair is one person.
- **On these 50 pairs the person's verdict matches the matcher's call every time:** the matcher links the 25 pairs judged one person and leaves out the 25 judged two people. The same-name rule also links the 25 two-people pairs, and misses the matcher-only pair. The pairs were spread over the groups on purpose, so these are counts, not rates.
- **So the 24 sampled links that both methods make and the register doesn't confirm were each judged one person under two officer ids,** which is why precision against the register is a lower bound.
- **Still not independent evidence:** the person saw pseudonyms, not names, and the same kind of evidence the matcher leans on, above all birth month and year. One person checked each pair once.

Groups as `handcheck_sample` defines them, recomputed with `main.ipynb`'s steps in a scratch script on the merged crawl; they give the AI table above exactly.

### The matcher against the baselines, on validation (card #170)
**Validation, not test:** the 1,552 companies formed Oct–Dec 2021, from the merged crawl (#159), under the main (stricter) label. Each method links a validation company's director to a record at an earlier insolvent company. The register confirms a link when both records have the same officer id. Printed by `notebooks/main.ipynb` @ f38cebd (#182), section "Evaluation: which earlier insolvent companies does each method find?". Copied from the saved outputs by jonas (with Claude), Sun 12:50.

| Method | Links | Confirmed (same officer id) | Not confirmed (different ids) | Confirmed links it misses | Precision vs the register | Recall vs the register | Companies linked |
|---|---|---|---|---|---|---|---|
| Same name | 458 | 83 | 375 | 1 | 0.181 | 0.988 | 219 |
| Officer links | 84 | 84 | 0 | 0 | 1.000 | 1.000 | 42 |
| Matcher (score 0.5 or more) | 210 | 80 | 130 | 4 | 0.381 | 0.952 | 105 |

| Surname band | Same name: not confirmed | Matcher: not confirmed | Confirmed (same officer id) | Confirmed, missed by the matcher |
|---|---|---|---|---|
| Rare | 0 | 0 | 0 | 0 |
| Medium | 290 | 121 | 66 | 2 |
| Common | 85 | 9 | 18 | 2 |

- **Officer links are perfect against the register by construction:** they are the register's own links, so they can't see a person the register split across two ids.
- **The matcher keeps 80 of the 84 confirmed links and makes 130 unconfirmed ones, against 375 for the same-name rule;** for common surnames 9 against 85.
- **Precision vs the register is a lower bound:** some unconfirmed links are one person under two ids (#89). How many is unknown until a person checks them.
- **On links to any earlier record** (not only insolvent ones), the same picture: 832 unconfirmed links by the same-name rule against 261 by the matcher (195 against 23 for common surnames), precision 0.383 against 0.663, and the matcher misses 13 of the 527 confirmed links.

### A harder baseline and a stress test, on validation (card #191)
`notebooks/main.ipynb` @ d0b0052, section "A harder baseline, and a stress test" (phantodevc, Sun 15 Nov). Validation only. Added after the test set was opened (#45): the rule has nothing to fit, no other number changed, and 2022 was not run again.

**A rule with nothing learned: same name and same birth month and year.** Links to an earlier insolvent company:

| Method | Links | Confirmed (same officer id) | Not confirmed | Recall vs the register | Companies linked |
|---|---|---|---|---|---|
| Same name | 458 | 83 | 375 | 0.988 | 219 |
| Officer links | 84 | 84 | 0 | 1.000 | 42 |
| Matcher | 210 | 80 | 130 | 0.952 | 105 |
| Name + birth rule | 221 | 83 | 138 | 0.988 | 108 |

For common surnames: the rule 11 unconfirmed and 18 of 18 confirmed, the matcher 9 and 16 of 18. On the register's own records the rule does as well as the matcher.

**Stress test.** One record of each of the 730 confirmed validation pairs is rewritten (seed 42), then the pair is asked again. Share still linked:

| Change to one record | Blocking still proposes it | Matcher | Same-name rule |
|---|---|---|---|
| Nothing changed | 99.2% | 97.9% | 98.4% |
| Moved (new postcode) | 99.2% | 97.8% | 98.4% |
| Typo in the first name | 99.2% | 81.0% | 2.6% |
| Typo in the surname | 74.1% | 57.7% | 5.8% |
| Middle names dropped | 99.2% | 32.3% | 29.6% |
| Birth month one off | 98.9% | 0.0% | 98.4% |
| Birth date missing | 98.9% | 0.0% | 98.4% |
| New surname | 0.0% | 0.0% | 0.0% |

- **Where the matcher is better:** misspelt names. **Where it is worse:** a wrong or missing birth date, and dropped middle names lose two thirds of the pairs.
- **Where this could be wrong:** the changes are made up by us, not found in the register, so they show what the matcher can stand, not how often each happens.

## Final result
Filled in after feature freeze, from the one test-set run: `notebooks/main.ipynb` @ 74d8a97 with `OPEN_TEST = True`, section "The test set, opened once (card #45)", run once on Sun 15 Nov 14:11 (jonas). The 6,847 test companies were formed in 2022, and nothing above was built or chosen on them; 65 of them failed (main label). Links to an earlier insolvent company, as printed:

| Test | Links | Confirmed (same officer id) | Not confirmed (different ids) | Confirmed links it misses | Precision vs the register | Recall vs the register | Companies linked |
|---|---|---|---|---|---|---|---|
| Same name (baseline) | 1,836 | 299 | 1,537 | 6 | 0.163 | 0.980 | 909 |
| Officer links | 305 | 305 | 0 | 0 | 1.000 | 1.000 | 169 |
| Matcher (score 0.5 or more) | 814 | 280 | 534 | 25 | 0.344 | 0.918 | 348 |

- **Baseline:** the same-name rule makes 1,537 links to an earlier insolvent company that the register doesn't confirm, 442 of them for common surnames, at a recall against the register of 0.980.
- **Our model:** the matcher makes 534 unconfirmed links, 112 of them for common surnames, at a recall of 0.918: it misses 25 of the 305 confirmed links, against 6 for the same-name rule.
- **In plain words:** on companies it never saw, the matcher raises far fewer links the register can't back up than matching by name, most of all for common surnames, and pays for it with some confirmed links missed. A link is a reason to check a director before giving credit, not a forecast: with or without one, about 1% of the test companies failed, for every method.

**Does a link go with failure on the test set?** As printed:

| Method | Failed, linked to an earlier insolvent company | Failed, not linked |
|---|---|---|
| Same name | 9 of 909: 1% (1–2%) | 56 of 5,938: 1% (1–1%) |
| Officer links | 1 of 169: 1% (0–3%) | 64 of 6,678: 1% (1–1%) |
| Matcher | 3 of 348: 1% (0–3%) | 62 of 6,499: 1% (1–1%) |

On links to any earlier record (not only insolvent ones), the same picture: 3,284 unconfirmed links by the same-name rule against 1,172 by the matcher (933 against 189 for common surnames), precision 0.336 against 0.582, recall 0.985 against 0.968.

## By group
The main metric for each group on the test set. Hackathon rule: say so if it's uneven.

The groups are the director's surname band (`name_commonness`: rare, medium, common). Test companies formed in 2022, links to an earlier insolvent company, printed by the same test-set run as the Final result.

| Surname band | Confirmed links (same officer id) | Same name (baseline): not confirmed | Matcher: not confirmed | Confirmed, missed by the matcher |
|---|---|---|---|---|
| Rare | 1 | 0 | 0 | 1 |
| Medium | 285 | 1,095 | 422 | 22 |
| Common | 19 | 442 | 112 | 2 |
| All | 305 | 1,537 | 534 | 25 |

- **Uneven for the same-name rule:** its unconfirmed links sit in the medium and common bands (1,095 and 442) and none in the rare band, where a surname seen once matches no one. The matcher makes 422 and 112 there.
- **The matcher's misses:** 22 of 285 confirmed links in the medium band, 2 of 19 in the common band, and the only confirmed link in the rare band (1 of 1).
- **Small groups:** the rare band has 1 confirmed link and the common band 19, so the missed-link counts there are noise.
- **On links to any earlier record,** the same pattern: the same-name rule makes 2,351 and 933 unconfirmed links in the medium and common bands, against 982 and 189 for the matcher (which also makes 1 in the rare band); the matcher misses 1 of 1, 51 of 1,533 and 2 of 155 confirmed links in the rare, medium and common bands.

### False flags by name-commonness band, on validation (card #106)
**Validation, not test:** the 1,552 companies formed Oct–Dec 2021, from the merged crawl (#159), under the main (stricter) label. The false-flag rate is false flags / companies that didn't fail. A company's band is the commonest surname band among its directors on record when it was formed (`company_bands`, bands from `name_commonness`); one company has no director on record and is left out. Printed by `false_flags_by_band` in `src/evaluate.py`, in `notebooks/main.ipynb` @ f38cebd (#182), the section "The figures".

| Band | Companies | Didn't fail | Same name: false flags | Officer links: false flags | Ours (formula): false flags |
|---|---|---|---|---|---|
| Rare surname | 457 | 448 | 0 of 448 (0%) | 0 of 448 (0%) | 0 of 448 (0%) |
| Medium | 955 | 942 | 34 of 942 (3.6%) | 9 of 942 (1.0%) | 0 of 942 (0%) |
| Common surname | 139 | 138 | 14 of 138 (10.1%) | 0 of 138 (0%) | 0 of 138 (0%) |

- **Uneven, as the claim expects, for the same-name rule:** its false-flag rate grows with how common the surname is, from 0% to 3.6% to 10.1%. The rare band can't be falsely flagged by name at all: a surname seen once in the data matches no one.
- **Every baseline flag is a false flag under this label:** same name flags 48 companies and officer links 9, and none of them failed (23 validation companies failed).
- **Ours flags nothing, so its zeros say nothing about fairness.** The line is nearly flat and under CLEAR (see the next subsection), so the decision layer clears every company with director records.
- The counts are small: 14 false flags in the common band.
- Under the earlier label (any dissolution counts; scratch run, Sun 10:18) the same-name rule gave 0% / 3.8% / 9.0%: the same pattern.

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

### One identity against the formula, on validation (card #92)
**Worked out from the failure line in `notebooks/main.ipynb` @ f38cebd, not a separate run.** The line, fitted on train under the main label, goes from 1.4% at P(predecessor) = 0 to 1.8% at 1. P(fail) is read off a straight line, so for every company it lies between 1.4% and 1.8%, whatever its P(predecessor) is. That is under CLEAR (10%) for every value.

| Validation, by band | Formula: flags / false flags | One identity: flags / false flags |
|---|---|---|
| Rare, medium, common surname | 0 / 0 in each | 0 / 0 in each |

- **It didn't change anything, and it can't here:** the one-identity rule only changes P(predecessor) (it never raises it above the formula's), and no P(predecessor) moves P(fail) out of 1.4% to 1.8%. So both clear every validation company with director records. The rule matters only once a predecessor changes the failure rate enough to cross a threshold.

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
- The test run is judged against the register only. The links it doesn't confirm (534 by the matcher, 1,537 by the same-name rule) include people the register split across two officer ids, so precision against the register (0.344 and 0.163) is a lower bound. Nobody has looked at a test pair: the hand checks (#89, #46) used validation pairs.
- On the test set the matcher misses more confirmed links than the same-name rule: 25 of 305 against 6 (recall 0.918 against 0.980).
- The failure counts on the test set are small: 65 of the 6,847 test companies failed, 3 of them among the 348 the matcher links. With or without a link about 1% failed for every method, so the test set can't show whether a link changes the failure rate.
- The adapter's known gaps are in the test run too: it skipped 27 director records whose resignation is dated before the appointment, and 6 companies are flagged insolvent with no insolvency file in the crawl.
