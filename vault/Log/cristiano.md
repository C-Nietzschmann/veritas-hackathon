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
