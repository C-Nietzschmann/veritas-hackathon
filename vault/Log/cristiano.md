Up: [[Log]]

## 2026-11-14 12:43
- **Task:** #24 crawl (card on the board): 2021, part 2 of 2, on my computer with my own key
- **Did:** Set up my own Companies House key (the first one was from a test application, which the live API refuses with a 401; a live application fixed it). Started jonas's crawler from PR #134 for 2021, part 2 of 2. Changed the crawler so a part keeps the usual 0.55 s gap between requests instead of 0.55 s times the number of parts: each part runs on its owner's own key, so each key stays under its own limit. The test that expected the doubled gap now expects the usual one.
- **Result:** not finished. My part holds 38,756 companies; 40 were crawled in full by 12:43. Measured over 90 seconds after the change: about 106 requests a minute, under 600 per 5 minutes. 134 tests pass.
- **AI used for:** Claude Code read #24 and PR #134, tested the key, ran the crawl, and made the speed change and its test change at my request.
- **Next:** jonas confirms the one-key-per-person reading of the rate rule, since his version slowed down on purpose. Let the crawl run, then zip `data/raw/` for jonas. The matcher (#30/#31) while it runs.
- **Blocked by:** nothing

## 2026-11-14 13:35
- **Task:** #142 the failure label (card on the board), with the #24 crawl still running
- **Did:** Counted failures on the companies crawled so far and found the label has almost no positives. Changed `label_failures` so a dissolution within 24 months counts too, with `count_dissolved=False` for the old label. Added tests, updated the label's definition in Evaluation, Idea, Modules, Plan and the notebook, and wrote the decision note Early dissolution counts as failure. Moved this log out of jonas's PR #134 so it doesn't conflict there.
- **Result:** on the first 253 companies of 2021 (part 2 of 2, 13:20): 1 failed by the old label, 89 (35%) by the new one. Only 5 have an insolvent predecessor under the same officer id, and 2 of them failed, so whether a predecessor raises the failure rate is still open. `main.ipynb` runs top to bottom with the same outputs as before.
- **AI used for:** Claude Code counted the failures, proposed three ways to fix the label, made the change and its tests, had a second AI pass review it, and drafted the notes, all at my request.
- **Next:** jonas and phantodevc confirm the label at the next check-in. The costs need a second look (#94): with a third of companies failing, CLEAR at 10% can't fire. Settle with jonas whether each of us may use an own key (his comment on #24 says one key for the project).
- **Blocked by:** nothing

## 2026-11-14 19:11
- **Task:** #157 the gap between requests in the crawler (card on the board), with my #24 crawl still running
- **Did:** Put the usual 0.55 s gap back for every part of the crawl, which undoes 3e94e7b: each part runs on its owner's own key. A run started as part K of N now prints a reminder that it needs its own key. jonas set a one-key rule on #24 at 13:53; my crawl keeps running on my own key until the team settles it.
- **Result:** 259 tests pass, 1 skipped. My crawl of 2021 part 2 of 2 had 2,148 query companies finished at 19:11, with no error and no rate-limit wait in its log.
- **AI used for:** Claude Code read what changed on #24 and in PR #134, checked Companies House's rate-limit pages, made the change and its test at my request, and wrote this entry.
- **Next:** settle the key rule with jonas and phantodevc at the next check-in: one key per person, or one key for all. Tell them before they restart a crawl from `main`: with this version two parts on one key pass the limit. Send jonas my `data/raw/`. Nobody is crawling 2022 yet.
- **Blocked by:** nothing

## 2026-11-15 09:14
- **Task:** #159 crawl 2022, part 2 of 2, until Sunday 09:00, then merge all crawls (card on the board)
- **Did:** Stopped my 2021 crawl at 2,335 companies on Sat 19:54, because phantodevc crawled the same companies in the same order, and started 2022, part 2 of 2, on my own key. Wrote the plan on #159: every crawl stops Sun 09:00, and each person uploads one zip of `data/raw/` to the team-only draft release `crawl-data`, never into git. My crawl stopped at 02:49 when the network dropped (five tries without an answer) and stood still until the restart at 08:38. At 09:06 I merged jonas's and phantodevc's zips into my `data/raw/`: a file is copied only when the folder doesn't have it yet, and `query_companies.csv` gains the companies it doesn't list.
- **Result:** one merged database with 13,761 query companies: 6,914 of 2021 and 6,847 of 2022 (the test set, only counted). It has 251,180 raw files, none unreadable, and no company listed twice; 2,335 companies were in two crawls and are kept once. `real_slice.load_slice()` from `task-36` (b7b5441) loads it in 31 s: 5,362 train companies (1,778 failed), 1,552 validation companies (527 failed), none left out. My own crawl ended at 2,634 companies of 2022, roughly 2,000 fewer than without the night's stop (estimated from its rate before). Counts and load steps are in my comment on #159, and `raw_merged.zip` (351 MB) is on the draft release.
- **AI used for:** Claude Code ran and restarted the crawl, wrote the merge and check scripts (scratch files, not in the repo), merged the zips, ran the loading check, and wrote the card texts and this entry, at my request.
- **Next:** jonas and phantodevc download `raw_merged.zip` and confirm on #159. Then I delete the draft release, which must be gone before the repo is public, and close #159 with its "How it works" note.
- **Blocked by:** nothing

## 2026-11-15 09:27
- **Task:** #162 add the script that merges the crawls into one data/raw (card on the board)
- **Did:** Put the merge script into the repo as `src/merge_crawls.py`, with one test on made-up files. It reuses the crawler's `save`, `finished_companies` and `mark_finished`. I confirmed I can explain it before the merge.
- **Result:** pull request #163 is merged. 295 tests pass, 1 skipped. Run on the three real zips into an empty folder, it rebuilt the merged folder of #159 file for file: 251,181 files and the same `query_companies.csv`.
- **AI used for:** Claude Code wrote the script and its test from the scratch version that did the merge, ran the tests and the rebuild, opened and merged the pull request, and wrote the card texts and this entry, at my request.
- **Next:** jonas and phantodevc load `raw_merged.zip` (steps on #159). `vault/Project/Modules.md` does not list the new file yet.
- **Blocked by:** nothing

## 2026-11-15 11:40
- **Task:** #171 a failure label that needs filed accounts before a strike-off (card on the board), from phantodevc's finding on #19
- **Did:** Checked phantodevc's finding on 2021 (train and validation; 2022 not read). His numbers hold, and 95% of the early strike-offs never filed accounts. Added a stricter label: `label_failures(mentions, traded=adapter.companies_that_traded(raw))` counts a strike-off only after a set of non-dormant accounts. The default label is unchanged. Wrote the proposal "A strike-off counts only after real accounts" in Decisions for the 14:00 call.
- **Result:** pull request #172 is merged and main is green. 305 tests pass, 1 skipped. 2021 train: 77 failures of 5,362 (1.4%) by the stricter label, against 1,778 (33%) by the current one; validation 23 of 1,552. With an insolvent predecessor (same officer id) 3 of 186 failed (1.6%), without one 97 of 6,711 (1.4%): no lift either way, and too few cases to rule one out.
- **AI used for:** Claude Code repeated the count, wrote the label option, the adapter function and their tests, counted both labels, and wrote the decision note, the card texts and this entry, at my request.
- **Next:** decide on the call whether the stricter label becomes the main label, and whether the headline moves to the matcher (phantodevc's plan B on #19). Then whoever owns `real_slice.py` and `main.ipynb` (#170) switches the label.
- **Blocked by:** nothing

## 2026-11-15 12:05
- **Task:** #175 use the stricter failure label in the real slice (card on the board)
- **Did:** Made the label call myself, since there was no call: the stricter label is the main label, the matcher is the headline (phantodevc's plan B), and the decision layer stays as it is. Marked the note "A strike-off counts only after real accounts" decided. `real_slice.slice_from_raw` now passes `companies_that_traded(raw)` to the label. Told both crew sessions (#170, #88) and wrote it on #19.
- **Result:** pull request #177 is merged and main is green. 309 tests pass, 1 skipped. Real-slice labels on 2021: train 77 failed of 5,362, validation 23 of 1,552.
- **AI used for:** Claude Code weighed the options against our data, made the change and its test, updated the decision note, and wrote the card texts, the messages and this entry, at my request.
- **Next:** the README and the write-up (#46) say "failed" as in the note and lead with the matcher. `failure_dates` still uses the old label.
- **Blocked by:** nothing

## 2026-11-15 13:40
- **Task:** #30 build blocking and pair features, with its sub-tasks #83 and #85 (cards on the board)
- **Did:** Closed the paperwork on blocking. The code has been on `main` since pull request #137, but #83 and #85 were still marked blocked on the crawl, and the recall number was only in the notebook's output. Wrote the subsection "Blocking recall, on validation (card #85)" in Evaluation and recounted it with a scratch script that loads the slice the way `main.ipynb` does (2022 files dropped).
- **Result:** blocking keeps 724 of 730 same-officer-id pairs on validation (99.18%) and 103,835 of 103,870 on train (99.97%), the same counts as `main.ipynb` @ f38cebd. It proposes 263,601 candidate pairs from 65,806 person records in 26.4 s. The rule is not loosened: the bar was a recall under about 90%.
- **AI used for:** Claude Code checked the cards against the code and the notebook, ran the recount, wrote the Evaluation subsection, the closing comments on the cards and this entry, at my request.
- **Next:** the switch in `main.ipynb` that opens 2022 for jonas's one test run (#45), and the main metric in Evaluation.
- **Blocked by:** nothing

## 2026-11-15 13:45
- **Task:** the main metric for the test run (jonas's question on #45), and loose ends on my cards
- **Did:** Chose the main metric, on jonas's suggestion and before the test set was opened: the links to an earlier insolvent company that the register doesn't confirm, overall and for common surnames, next to recall against the register, with the same-name rule as the baseline. Wrote the decision note "The main metric is unconfirmed links next to recall" and the Setup line in Evaluation. Added `src/merge_crawls.py` to Modules. Moved #81's card to Done and added the missing "How it works" note to #32, which was already closed.
- **Result:** no new number. On validation the metric reads 375 unconfirmed links for the same-name rule against 130 for the matcher (85 against 9 for common surnames), at a recall of 0.988 against 0.952 (`main.ipynb` @ f38cebd).
- **AI used for:** Claude Code wrote the decision note, the Evaluation line, the Modules row, the card note and this entry, at my request. The choice of metric is mine.
- **Next:** card #185, the switch in `main.ipynb` that opens 2022 for jonas's run. The `crawl-data` draft release is deleted once jonas confirms on #159 that he has the merged data.
- **Blocked by:** nothing

## 2026-11-15 14:00
- **Task:** #185 the switch in `main.ipynb` that opens the 2022 test set (card on the board), for jonas's run of #45
- **Did:** Added the section "The test set, opened once (card #45)" before the Demo, with `OPEN_TEST = False`. Turned on, it loads the crawl with the 2022 companies, scores their pairs with the matcher trained above and prints the Evaluation tables for them. The code that built `validation_links` and the failure-next-to-link table became two functions (`held_out_links`, `failure_by_link`), so validation and test go through the same code. The 2022 companies were not opened.
- **Result:** pull request #186 is open, not merged: I read it first. With the switch off the notebook ran top to bottom on the merged crawl and every code cell prints what it printed before, except two Demo cells that now use the wording of #180. With the switch on and the validation companies as a stand-in (a scratch copy), the five new tables are identical to the five validation tables. 314 tests pass, 1 skipped.
- **AI used for:** Claude Code designed and wrote the switch and the two functions, ran the notebook both ways, compared the outputs, opened the pull request and wrote the card and this entry, at my request.
- **Next:** read #186 and merge it, then jonas runs #45 once. Loading the 2022 files from the new cell has not been run: his run is the first. After it, a short "What it shows" cell goes under the tables.
- **Blocked by:** nothing

## 2026-11-15 15:15
- **Task:** #189 audit the code and clean the repo for the judges (card on the board)
- **Did:** Had two AI agents read the whole repo: one all of `src/`, `scripts/` and `tests/` for bugs, one every tracked file, the git history and the GitHub side for names, secrets and what a judge would trip over. Fixed what can be fixed in files. `check.sh` skipped any file with an accent in its name. Two name-guard tests had the same name, so the first never ran. The name guard searched only `main.ipynb`; it now searches all four notebooks, and the check says so when it is skipped. `task.sh` stops before changing anything when `gh` is missing. The README asked for Python 3.10, but the pinned numpy needs 3.12. The masking docstring said a label can't be turned back; it now says a reader with a list of names can hash and compare. A first name in `jonas_real.ipynb` and a GitHub username in jonas's log became handles. "Where it fails" item 2 in `main.ipynb` now reports the hand check. Evaluation states that `cristiano_calibration.ipynb` read the 2022 files before the test run and printed only their count. Stale lines in Home, Team, Idea and Credits are corrected, and the template `SECURITY.md` is gone.
- **Result:** 317 tests pass, 1 skipped by design. The widened name guard, run with the 49,253 real names of the local crawl, finds none in any of the four notebooks. The audit found no bug in `src/` that changes a reported number, and it recounted the validation table from the raw files without `src/` (527 / 84 / 42 for officer links, 1,349 / 458 / 219 for the same-name rule): the same as `main.ipynb`. Shared as a pull request linked to #189, open until I have read it.
- **AI used for:** Claude Code (Claude Fable 5.2) ran both audits, made the fixes, ran the tests and the name guard, and wrote the pull request and this entry, at my request.
- **Next:** read the pull request, then merge it. Not done, because a re-run or a team decision is needed first: six crash guards for inputs no notebook reaches, the "random: 1%" label on the PR figure, real company numbers in notebook outputs, and the decision notes still marked proposed. The clean-up on GitHub itself (the draft release, merged branches, the board's visibility) waits for my yes.
- **Blocked by:** nothing
