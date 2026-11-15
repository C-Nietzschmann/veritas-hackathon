# The main metric is unconfirmed links next to recall

Up: [[Decisions]]

- **Date:** 2026-11-15 13:45
- **Decided by:** cristiano, on jonas's suggestion on card #45. Decided before the test set was opened.
- **Status:** decided

## Decision
The main metric is the number of **links to an earlier insolvent company that the register doesn't confirm** (the two records have different officer ids; fewer is better), overall and for common surnames. It is always read next to **recall against the register**: the share of the confirmed links (same officer id) a method finds. The baseline is the same-name rule.

## Why
- **It measures the headline.** Since the decision "A strike-off counts only after real accounts" the main result is the matcher: does it keep the links the register confirms and make fewer doubtful ones than matching by name, above all for common surnames?
- **One number alone can be gamed.** A method that links nothing has no unconfirmed links, so recall stands next to it.
- **The alternative we didn't take:** precision and recall of the FLAG decision against failure. On our data the decision layer never flags, so that metric would compare 0 with 0 (Evaluation, the failure line on validation).
- **Where it is weak:** an unconfirmed link is not proven wrong. The register sometimes gives one person two officer ids, so some of these links are right. The hand check (#89) looks at that.

On validation (`notebooks/main.ipynb` @ f38cebd): the same-name rule makes 375 unconfirmed links (85 for common surnames) at a recall of 0.988, the matcher 130 (9 for common surnames) at a recall of 0.952.

## What it changes
- jonas fills "Final result" and "By group" in Evaluation with these numbers from the one test run (#45), and the write-up (#46) leads with them.
- `main.ipynb` prints them for the 2022 companies once the switch of card #185 is turned on.
