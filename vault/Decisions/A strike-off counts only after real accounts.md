# A strike-off counts only after real accounts

Up: [[Decisions]]

- **Date:** 2026-11-15 11:20
- **Decided by:** cristiano, Sun 11:55, after phantodevc's analysis on card #19. There was no call: the team left the decision to cristiano.
- **Status:** decided

## Decision
1. **The main failure label is the stricter one.** A company failed if, within 24 months, it went into liquidation or administration, or it was struck off **after filing at least one set of accounts that were not dormant**. The write-up shows the old label next to it.
2. **The headline is the matcher** (phantodevc's plan B on card #19), which is our own question in Idea: does keeping identity uncertainty cut false matches for common names without missing real ones? The evidence: calibration (#88), the hand-checked pairs (#89) and the results by name commonness.
3. **The decision layer stays as it is** until the freeze. It now clears nearly every company, and the write-up reports that as the honest result: on our data an insolvent predecessor does not predict that a young company fails.

## Why
- **The current label mostly counts companies that never started.** On 2021, 95% of the companies struck off within 24 months never filed a set of accounts (phantodevc, #19). A company that never traded leaves no supplier unpaid, and our user is a supplier.
- **Experienced directors file their accounts, so the current label punishes the signal we look for.** A director with an earlier insolvent company goes with fewer failures by the current label: 11% against 34%.
- **The stricter label is close to the harm, and failure is rare again,** as the costs (10 / 2 / 1) assumed.
- **But an insolvent predecessor doesn't raise the failure rate under the stricter label either.** So predicting failure can't be the headline:

Counted on Sun 15 Nov, 2021 only (train and validation; 2022 is the test set and was not read), with `label_failures` and `companies_that_traded` from #171 over the merged database (#159). Script outside the repo.

| 2021 | Companies | Current label | Stricter label | Insolvency only |
|---|---|---|---|---|
| Train (Jan–Sep) | 5,362 | 1,778 (33%) | 77 (1.4%) | 15 |
| Validation (Oct–Dec) | 1,552 | 527 (34%) | 23 (1.5%) | 1 |

| Train + validation, predecessor by the same officer id | Companies | Current label | Stricter label |
|---|---|---|---|
| No insolvent predecessor | 6,711 | 34% | 97 (1.4%) |
| Insolvent predecessor | 186 | 11% | 3 (1.6%) |
| Experienced directors, no insolvent predecessor | 2,083 | 28% | 43 (2.1%) |

"Insolvent predecessor" here: a director on record at formation was appointed, before the formation date, at another company whose liquidation or administration started before that date. Only among the companies the crawl reached. With 3 cases, an effect can't be ruled out either.

The alternatives we didn't take:
- **Keep the current label.** It measures "registered and never got going", and it turns our signal upside down.
- **Insolvency only.** 15 train cases and 1 in validation: too few to fit or to check anything.
- **Insolvency within 36–48 months.** The 2021 outcomes would run into 2025 and deep into the test year.

## What it changes
- **Code:** `label_failures(mentions, traded=adapter.companies_that_traded(raw))` gives the stricter label (#171). `real_slice.slice_from_raw` and `load_slice` use it from #175, so `main.ipynb` and `jonas_real.ipynb` get it with no change of their own. The tiny world keeps the old label, because its companies file no accounts. `failure_dates` (the predecessors' side table) keeps the old label too.
- **The headline (plan B, #19):** the main result is the matcher. Does it find a director's earlier insolvent company better than the officer-id and exact-name baselines, with fewer false flags for common names? Checked on the hand-checked pairs (#89).
- **The output:** a due-diligence warning ("this director probably ran an earlier company that went insolvent: check before giving credit") instead of a failure probability.
- **The failure line (#94):** with about 1.5% failures in both groups, P(fail) stays far under 10% for every company. So CLEAR fires for nearly everyone and FLAG never does, and "flag nothing" ties with our method on the failure metrics. We don't move FLAG onto the predecessor probability: the officer-links baseline would then be right by definition (the alternative Idea already rejected).
- **The write-up:** all three labels with their counts, and this finding as the honest answer to "where does it fail".
- **Idea, the README and the write-up (#46):** say "failed" as defined here, name the matcher as the main result, and put this finding under "where does it fail".
