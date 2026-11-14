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
