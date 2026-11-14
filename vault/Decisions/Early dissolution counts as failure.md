# Early dissolution counts as failure

Up: [[Decisions]]

- **Date:** 2026-11-14 13:30
- **Decided by:** cristiano, from the first real crawl data. jonas and phantodevc: confirm or change it at the next check-in.
- **Status:** decided

## Decision
A company failed if, within 24 months of incorporation, it went into liquidation or administration **or was dissolved** (removed from the register). Before, only liquidation and administration counted.

## Why
- **The old label has almost no positives.** Of the first 253 companies of 2021 crawled in full (part 2 of 2, 14 Nov 13:20), 1 failed by the old label and 89 (35%) by the new one. jonas's small run found 0 of 50 (his comment on card #24). The crawl can reach at most about 20,000 companies of 2021 by the feature freeze. At one failure in 250 that is under a hundred failures, and almost none of them with an insolvent predecessor: too few to train, validate and test on.
- **Young construction companies don't end in a liquidation.** They are struck off the register, most of them in their second year.
- **For our user the harm is the same.** A customer that is struck off while owing money leaves the supplier's invoice unpaid, just as a liquidation does. UK law now treats it that way too: under the Rating (Coronavirus) and Directors Disqualification (Dissolved Companies) Act 2021, former directors of dissolved companies can be investigated and, where it is in the public interest, disqualified, because dissolution was being used to shed liabilities. Source: the Act's explanatory notes, https://www.legislation.gov.uk/ukpga/2021/34/notes/division/3/index.htm

The alternatives we didn't take:
- **Keep the label and crawl more.** Not reachable this weekend, see above.
- **Predict "has an insolvent predecessor" instead of "fails".** The officer-links baseline would then be right by definition, because the label would be its own rule.
- **Crawl failed companies on purpose.** That needs new crawl code, and a sample chosen by its outcome has to be corrected before precision means anything.

## What it changes
- `label_failures` in `src/evaluate.py` counts a dissolution inside the window. `count_dissolved=False` still gives the old label, so the write-up can show both counts.
- Nothing has to be crawled again: every company profile already holds the dissolution date.
- **Failure is no longer rare:** about a third of the companies. Two things follow.
  - Idea and the notebook's baseline text say "failures are rare". Now it is the flags that are rare. Precision and recall stay the main metric, and the wording needs an update when the real numbers come in (#36).
  - The costs were chosen for a rare failure. CLEAR needs P(fail) at or below 10%, but companies with no insolvent predecessor already fail at about 37% here (80 of 217), so CLEAR could never fire. Card #94 has to check both ends of the failure line, and the call may have to change the costs.
- **The label is noisier.** It also counts companies closed by their owners with no debts, and companies struck off because they never filed anything. The register's profile can't tell these apart. It is written as a limit in Evaluation.
- **Still open: does an insolvent predecessor raise the failure rate at all?** Only 5 of the 253 companies have one under the same officer id, and 2 of them failed. Of the 31 that have one only through a same-name officer, 7 failed. That is far too few to say, and it is the first thing to check once more data is in.
- The counts in this note come from a throwaway script over the files crawled so far, using the adapter and `label_failures`. The notebook repeats them on the full data (#36, #62).
