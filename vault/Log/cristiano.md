Up: [[Log]]

## 2026-11-14 12:43
- **Task:** #24 crawl (card on the board): 2021, part 2 of 2, on my computer with my own key
- **Did:** Set up my own Companies House key (the first one was from a test application, which the live API refuses with a 401; a live application fixed it). Started jonas's crawler from PR #134 for 2021, part 2 of 2. Changed the crawler so a part keeps the usual 0.55 s gap between requests instead of 0.55 s times the number of parts: each part runs on its owner's own key, so each key stays under its own limit. The test that expected the doubled gap now expects the usual one.
- **Result:** not finished. My part holds 38,756 companies; 40 were crawled in full by 12:43. Measured over 90 seconds after the change: about 106 requests a minute, under 600 per 5 minutes. 134 tests pass.
- **AI used for:** Claude Code read #24 and PR #134, tested the key, ran the crawl, and made the speed change and its test change at my request.
- **Next:** jonas confirms the one-key-per-person reading of the rate rule, since his version slowed down on purpose. Let the crawl run, then zip `data/raw/` for jonas. The matcher (#30/#31) while it runs.
- **Blocked by:** nothing
