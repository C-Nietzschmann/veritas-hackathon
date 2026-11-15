Up: [[Log]]

## 2026-11-13 12:14
- **Task:** #5 Setup (card on the board)
- **Did:** Claimed my setup task and started this log. Fixed CI traps before kickoff: an empty `tests/` no longer fails CI, pushes to `main` no longer cancel each other's checks, the push skill watches the CI run for its own commit, notebooks may be up to 25 MB. Brought the vault in line with the official Hacker Guide: four tracks including Languages, official kickoff call, write-up template, video shape, what judges reward and the red flags, per-group results, health and finance disclaimer, 30-minute data rule, confirmation screenshot to WhatsApp instead of `Log/`, git identity and `gh auth login` in Setup.
- **Result:** pushed to `main`. Docs and config only, no project code.
- **AI used for:** Claude (claude.ai) compared the repo with the official Hacker Guide, made these changes and pushed them at my request. Tested the CI step and the size check before pushing.
- **Next:** set up my own computer (Git, Obsidian, gh, clone), agree roles, make sure all three of us are registered before 05:59.
- **Blocked by:** nothing

## 2026-11-13 12:47
- **Task:** #5 Setup (card on the board)
- **Did:** Switched to the new workflow: tasks are issues on the GitHub board, code goes through a pull request linked to its task. Pointed this log at card #5 instead of the old vault task note.
- **Result:** notes only.
- **AI used for:** Claude (claude.ai) read the new instructions and updated this log.
- **Next:** on my own computer: Git, Obsidian, gh, clone, drag #5 on the board, read Rules, Timeline, Calls and Task Protocol.
- **Blocked by:** nothing

## 2026-11-14 07:12
- **Task:** #16 Draft the architecture decisions and hard rules (card on the board)
- **Did:** Drafted ADR-001 to ADR-005 and the hard rules R1–R8 as proposed notes in `Decisions/`. Open choices are marked for the call: the matcher in ADR-003, how uncertainty is propagated in ADR-004, and the attribute columns in ADR-001.
- **Result:** notes only, status proposed. Not confirmed by the team yet.
- **AI used for:** Claude (claude.ai) read the repo, created card #16, drafted the six notes from our TENSEGRITY concept at my request and pushed them.
- **Next:** confirm or change them on the 08:00 call, drag #16 to In Progress, finish #5 Setup.
- **Blocked by:** nothing

## 2026-11-14 07:40
- **Task:** #16 Prepare the architecture and build plan for the kickoff call (card on the board)
- **Did:** Added Pipeline (the diagram and how it works) and Modules (the boxes, files, contracts, leads and cards) to Project. Drafted Idea around phoenix-company risk for small suppliers on Companies House data. Reviewed the ADRs against it: claim dates are now intervals with an as-of rule against leakage, ids come from stable keys, the register's officer id is a weak label and never the truth, worlds are sampled per query, and the file list matches Modules. Created build cards #19 to #48 on the board, unassigned.
- **Result:** notes and cards only, all proposed until the call.
- **AI used for:** Claude (claude.ai) drafted the notes and the cards at my request, checked the Companies House data limits on the web, and pushed.
- **Next:** 08:00 call: confirm the use case, the ADR choices, the three costs and the roles. Then everyone claims cards.
- **Blocked by:** nothing

## 2026-11-14 07:58
- **Task:** #16 Prepare the architecture and build plan for the kickoff call (card on the board)
- **Did:** Applied the review on #16.
  - Plan: the lighter MVP uses P(insolvent predecessor) = 1 − ∏(1 − pᵢ) and a straight line from that to P(fail), so the cost thresholds run on failure. One identity per director becomes Sunday's measured improvement.
  - Data and evaluation: officer ids are the matcher's label, never a feature; three baselines (flag nothing, same name, Companies House officer links); 2021 train and 2022 test cohorts; masking in every output.
  - Rules: R1 kept in its cheapest form, R5 skipped while we have one source, R7 tested once #32 exists.
  - Notes updated: Pipeline, Modules, Idea, ADR-001, ADR-003, ADR-004, ADR-005 and Hard rules.
  - Cards: 15 updated, #26 merged into #22, #41, #43 and #44 cut, #49 to #52 added.
- **Result:** notes and cards only, all proposed until the call.
- **AI used for:** Claude (claude.ai) checked the review, worked out the two maths fixes (the step from predecessor to failure, and the one-identity rule) and applied everything at my request.
- **Next:** 08:00 call: confirm the lighter MVP, the slice, the label, the costs and the roles.
- **Blocked by:** nothing

## 2026-11-14 08:05
- **Task:** #16 Prepare the architecture and build plan for the kickoff call, and #3 Agree roles and schedule (cards on the board)
- **Did:** Made the five choices as coordinator: the lighter MVP, construction 2021 and 2022, liquidation or administration within 24 months, costs 10/2/1, and roles. Wrote Plan: three lanes, each owning its own files, meeting only through the six shared tables in `evidence.py`. Updated Modules (owners, the six tables), ADR-005 (no spider web), Idea (choices) and Team (roles). Assigned every build card to its owner, moved the rule tests to the model lead, and moved masking into the schema and adapter.
- **Result:** notes and card assignments. The call can still change them.
- **AI used for:** Claude (claude.ai) proposed the split into lanes and the table contracts, and applied them at my request.
- **Next:** on the call, confirm. Then start #22, schema v1 by 09:30.
- **Blocked by:** nothing

## 2026-11-14 08:12
- **Task:** #16 Prepare the architecture and build plan for the kickoff call (card on the board)
- **Did:** Switched to no fixed roles. Took everyone off the cards I had assigned, removed the owner suggestions from the cards, and emptied the role table in Team again. Rewrote Plan as a pick-your-own order of cards, wrote the decision "No fixed roles, everyone claims their own cards", and took the owner column out of Modules. The shared-schema rules stay.
- **Result:** every build card is free to claim. Notes only.
- **AI used for:** Claude (claude.ai) undid the assignments and rewrote the notes at my request.
- **Next:** everyone claims their first card from the start of the order in Plan.
- **Blocked by:** nothing

## 2026-11-14 08:42
- **Task:** #22 Write the evidence schema, checks and observed graph, with sub-tasks 22.1 to 22.4 (cards on the board)
- **Did:** Built `src/evidence.py` and `tests/test_evidence.py` on branch `task-22`:
  - the six shared tables' columns
  - stable ids and `record_ref` with the raw response's hash
  - `check_rows`, which names each bad row and its rule
  - `observed_graph` with the as-of rule

  Modules now lists the exact column names.
- **Result:** 16 tests pass locally. Branch pushed. The pull request is not open yet: it waits for me to read the code.
- **AI used for:** Claude (claude.ai) wrote the schema, the tests and the draft "How it works" while I was away.
- **Next:** read the code, open the pull request from `task-22` (description drafted), confirm I can explain it, then ship #22.
- **Blocked by:** nothing

## 2026-11-14 08:55
- **Task:** #22 schema and #21 tiny world (cards on the board)
- **Did:** Opened pull request #117 for the schema; its CI and the linked-task check pass. Built the tiny world on top of it: 28 hand-made rows with known answers (a phoenix with a new officer id, a same-name look-alike, a common name, a future insolvency that must not leak, a company with no evidence, a clean history, a copied source). Opened #118, stacked on #117.
- **Result:** 26 tests pass locally. Both pull requests wait for me to read them before they merge.
- **AI used for:** Claude (claude.ai) built the tiny world from the cases I approved and opened both pull requests at my request.
- **Next:** read and ship #117, then #118. Then pick the next card: the baselines (#27) give the first numbers for the 14:00 gate.
- **Blocked by:** nothing

## 2026-11-14 09:40
- **Task:** #22 schema and #21 tiny world (cards on the board)
- **Did:** cristiano reviewed #117. I applied his patch unchanged: stricter row checks (empty ids, swapped claims, dates not in `YYYY-MM-DD`, a `record_ref` in the wrong shape) and end dates after the as-of date now hidden in the graph. I added the same date check for the three company dates, then merged both into #118. ADR-001 now says "on or before t". I replied on #117 to his five open points.
- **Result:** 23 tests pass on #117 and 33 on #118. Both still wait for me to read them before they merge.
- **AI used for:** Claude (claude.ai) checked his patch, applied it, wrote the company-date check and drafted the reply, all at my request.
- **Next:** read and ship #117, then #118. For the call: where the as-of view for company dates lives, which insolvency types count (members' voluntary liquidation doesn't), and which SIC code we keep. Then the baselines (#27).
- **Blocked by:** nothing

## 2026-11-14 09:55
- **Task:** #22 schema and #21 tiny world, then #121 as-of view (cards on the board)
- **Did:** Shipped #117 and #118 as squash merges. #21, #22 and their sub-tasks closed, and their "How it works" notes are posted. Cristiano's review point 1 was a real leak: a company's later insolvency showed up in a query dated before it. I created #121 for it and built `mentions_as_of` in `src/evidence.py`. Pull request #122 is open.
- **Result:** `main` is green with 33 tests. #122 passes 36 locally.
- **AI used for:** Claude (claude.ai) merged the pull requests when I said go, drafted the "How it works" notes, and wrote the as-of view and its tests.
- **Next:** read and ship #122, then the crawl (#24), as Cristiano suggested.
- **Blocked by:** nothing

## 2026-11-14 09:58
- **Task:** #121 as-of view (card on the board)
- **Did:** Shipped #122 as a squash merge. #121 is closed with its "How it works" note.
- **Result:** `main` is green with 36 tests.
- **AI used for:** Claude (claude.ai) merged it when I said go and drafted the note.
- **Next:** set up Claude Code in VS Code on my PC for the code work, because the crawl needs the Companies House API and the cloud session can't reach it. Then #24.
- **Blocked by:** nothing

## 2026-11-14 11:40
- **Task:** #24 crawl (on my PC), plus #27 baselines as the agreed backup (cards on the board)
- **Did:** Set up the repo, Python and my own Companies House API key on my PC; my local Claude is building the crawl (#24). Nobody had claimed #27 by 11:30, so I took it as agreed so the 14:00 gate holds. `src/baseline.py` has flag nothing, same name and officer links, as pairs plus decisions. Pull request #127 is open. Reviewed Cristiano's #123, #124, #125 and #126 and left comments.
- **Result:** 67 tests pass on #127. On the tiny world, same name flags the phoenix and both look-alikes, and officer links miss the phoenix.
- **AI used for:** Claude (claude.ai) built the baselines and their tests, reviewed the team's pull requests, and drafted the comments at my request. Claude Code on my PC is building the crawl.
- **Next:** read and ship #127. Add `score()` (27.4) once #126 merges, then the first numbers in Evaluation. Finish #24.
- **Blocked by:** 27.4 waits for #126 (`src/evaluate.py` is Cristiano's until it merges)

## 2026-11-14 11:55
- **Task:** #27 baselines (card on the board), plus the #24 crawl on my PC
- **Did:** Had #127 reviewed before approving. The review found six problems: names were cut too short so different names matched, `controls` claims counted as directorships, missing data got a misleading reason, the box didn't check its own output, the window boundary was unclear, and name order was only half handled. All six are fixed with regression tests. Shipped #127 as a squash merge, which closed 27.1–27.3. The matching points in `decide.py` went to Cristiano on #34.
- **Result:** `main` is green with 75 tests.
- **AI used for:** Claude (claude.ai) reviewed and fixed the baselines and drafted the notes at my request.
- **Next:** 27.4 `score()` once #126 merges, then the first numbers in Evaluation. The #24 crawl. Team call at 12:30 when phantodevc is back.
- **Blocked by:** 27.4 waits for #126

## 2026-11-14 12:20
- **Task:** #27 baselines (27.4 scoring) and #132 decision layer fix (cards on the board), plus the #24 crawl on my PC
- **Did:** Approved Cristiano's #125 (with follow-ups) and #126, and he merged both. He applied the follow-ups in #131, which I checked. Built `score()` and `score_methods()` in `src/evaluate.py` (PR #130), and put the baselines' first numbers, on the tiny world, in Evaluation. Fixed `decide.py` so only directorships count and its output is checked against the schema, as Cristiano asked (card #132, PR #133).
- **Result:** on the tiny world, same name flags 3 with 2 false flags, while flag nothing and officer links miss the one failure. That's a code check, not a result. 105 tests pass on #133.
- **AI used for:** Claude (claude.ai) reviewed the PRs, wrote `score()`, the decision layer fix and their tests, and drafted the approvals, all at my request.
- **Next:** read and ship #130 and #133. The 12:30 call: owners for #29 and #30/#31, slice size, and splitting the crawl with phantodevc.
- **Blocked by:** nothing

## 2026-11-14 12:37
- **Task:** #24 Crawl the Companies House slice, sub-tasks #71 to #73 (cards on the board)
- **Did:** Built `src/crawl_companies_house.py` and 25 tests with a fake API. It lists the slice month by month with the advanced search, then fetches each query company's profile, insolvency file when flagged and officers, each director's appointments and every company in them, and a name search that follows up to 20 officers with the same name words (their active companies skipped). Settings for years, sample size and part K of N; it resumes where it stopped, reuses one connection and stays under 600 requests per 5 minutes. Moved the API key from `.env.example` into `.env` before anything was committed. Merged main into the branch, and cristiano's Companies House row with mine in Credits. Ran the small real run and started the 2021 crawl as part 1 of 2.
- **Result:** PR #134 open, checks green. The slice is 77,513 companies formed in 2021 and 84,250 in 2022. The small run took 1,140 requests in 32 minutes: median 8.5 requests per query company, mean 21.9, max 174. 0 of its 50 companies failed within 24 months. Numbers on #24.
- **AI used for:** Claude Code (Opus 5.5) in VS Code wrote the crawler and its tests from my decisions, probed the real API's answers, checked the API facts and the plan with a multi-agent workflow, ran the small crawl and the counts with the team's adapter and label code, and opened PR #134, all at my request.
- **Next:** read the crawler line by line and write its "How it works" note. Pick SAMPLE_SIZE for the fresh run and the size of the 2021 and 2022 crawls. Part 2 of 2 runs on a second computer with the same key. Ship #24.
- **Blocked by:** nothing

## 2026-11-14 13:43
- **Task:** #24 Crawl the Companies House slice (card on the board)
- **Did:** Undid the rate part of cristiano's 2ef2ca0 in PR #134: every part of the crawl shares my key, and part K of N keeps N times the gap, because Companies House treats several keys for one application as getting round the limit. Moved my 2021 crawl (part 1 of 2) out of VS Code into its own PowerShell window. Counted, read-only, how the query companies crawled so far ended.
- **Result:** PR #134 checks green on 3e94e7b. 231 query companies of 2021 part 1 finished by 13:41. Of the 281 query companies crawled so far, 0 failed through insolvency within 24 months and 92 were dissolved within 24 months; 91 of those 92 never filed accounts.
- **AI used for:** Claude Code (Opus 5.5) restored the rule, ran the tests and checks, restarted the crawl and counted the failure routes with the team's adapter and label code, at my request.
- **Next:** go through the crawler and write the "How it works" note. Decide with the team whether the label should count dissolution. phantodevc runs part 2 of 2 on my key. Ship #24 when I say so.
- **Blocked by:** nothing

## 2026-11-14 15:32
- **Task:** #36 Run main.ipynb end to end on real data (card on the board)
- **Did:** Built `src/real_slice.py`. It reads the crawl's finished query companies, runs the adapter over `data/raw`, and labels and splits them with the team's `label_failures` and `split`. It also builds the key table: each company under its strongest link to an insolvent earlier company, with 95% Wilson intervals. Ran every box of `main.ipynb` on part 1 of 2021 in my scratch notebook `notebooks/jonas_real.ipynb`, on a copy of the crawl's files taken at 15:04. The name guard doesn't run on Windows yet (#112), so I ran its functions on the notebook by hand: no real name found.
- **Result:** Draft PR #154, checks green. 438 query companies (331 train, 107 validation): 137 failed under the team label, none through insolvency. With a predecessor by officer id or by name and birth month and year, 4 of 30 failed (13%, 5-30%); with none, 120 of 369 (33%, 28-37%). The failure line slopes down (35% to 9.6%), so FLAG can never fire, and the decision layer says NOT ENOUGH EVIDENCE for 106 of 107 validation companies. Blocking kept all 45 same-officer-id pairs in validation.
- **AI used for:** Claude Code (Opus 5.5) in VS Code wrote the loader, its tests and the notebook, ran every box and the checks, and opened the draft PR, at my request.
- **Next:** read `real_slice.py` and the notebook. Decide with the team on the label, the costs and the downward line (#94). Ship #24 when ready.
- **Blocked by:** nothing

## 2026-11-14 16:38
- **Task:** #36 Run main.ipynb end to end on real data (card on the board)
- **Did:** Defined a second key table in commit 469c621 (16:05), before it touched real data. A predecessor counts only if it failed the way our label defines failure (liquidation, administration or dissolution within 24 months of its own incorporation), dated on or before the new company's formation. Its links come from the saved appointment lists, because a predecessor that was only dissolved has no officer list. Ran it next to the first table on the same 438 companies. Also measured, read-only, the share of crawl requests that went to profiles of companies a director's own appointment list showed as active. Four independent read-only checks recounted and reviewed both.
- **Result:** Second table: 24 of 71 companies with a predecessor by officer id or by name and birth month and year failed (34%, 24-45%), against 96 of 310 without one (31%, 26-36%). No row has a failure through insolvency. Skipping those active companies would save 1,036 of 8,824 requests (11.7%), under the 25% bar, so I prepared no crawler change. Draft PR #154 updated, checks green.
- **AI used for:** Claude Code (Opus 5.5) wrote and tested the second table, ran it and the request replay, and had four subagents recount and review both, at my request.
- **Next:** decide with the team what the two tables mean for the label and the predecessor signal. Keep #154 a draft until main.ipynb runs on real data.
- **Blocked by:** nothing

## 2026-11-14 19:35
- **Task:** #24 Crawl the Companies House slice (closed), #155 fresh-run sample, #36 Run main.ipynb end to end on real data (cards on the board)
- **Did:** #134 is merged into main (de1ee00), which closed #24, #71, #72, #73, #60 and #61. Stopped my 2021 crawl at 848 query companies of part 1 and started 2022 part 1 of 2 in a new PowerShell window that waits 60 minutes and resumes after an error. Prepared the merge of phantodevc's and Cristiano's data/raw zips: scripts outside the repo, a full-size rehearsal, four checkers, then their fixes. Wrote phantodevc's steps for 2022 part 2 of 2 on my key; since Cristiano's #158 (19:12) undid the shared key on main, they pin ddc11c8, the last version for two parts on one key. Opened #155 and PR #156, which sets the fresh-run sample to 10 companies per year; #156 is merged. For #36, defined the headline in 156a981 before running it, then ran it in my scratch notebook on the 15:04 copy; a review led to 32763a6, which keeps records at companies formed after September 2021 out of the matcher's training and makes the hand-check sheet blind.
- **Result:** The headline on the 107 validation companies: of the links the register doesn't confirm, the same-name rule makes 28 and the matcher 13, and the matcher finds all 39 links with the same officer id. Only 28 "different ids" pairs exist there, so the hand check takes all 28 (15 same name only, 13 both, 0 matcher only); an independent recount agrees on every cell. Both key tables on all 848 companies of 2021 part 1 (2021 only; two independent recounts agree): with a predecessor by officer id or by name and birth month and year, 10 of 65 failed (15%, 9-26%) in the first table and 39 of 125 (31%, 24-40%) in the second, against 247 of 717 (34%, 31-38%) and 200 of 594 (34%, 30-38%) with none. Draft PR #154 at b7b5441, checks green.
- **AI used for:** Claude Code (Opus 5.5) in VS Code switched the crawl, wrote and rehearsed the merge scripts, wrote phantodevc's steps, the #155 change and the headline code and tests, and had subagents review, mutation-test and recount the work, at my request.
- **Next:** hand-check the 28 pairs (verdicts in notebooks/jonas_handcheck.csv). Settle the key rule with Cristiano at the check-in. Run the merge when phantodevc's and Cristiano's zips arrive, then rerun the headline on more 2021 data to reach 50 pairs. Keep 2022 out of every number until the test run.
- **Blocked by:** nothing

## 2026-11-15 12:52
- **Task:** review of #40 (Cristiano's card), #45 Run the test set once (taken, as agreed on the call), #48 Run the fresh-run test (taking it over, as agreed on the call), planning #46 and #47
- **Did:** Reviewed pull request #183 (failure gallery): every number in its Evaluation rows matches the notebook's saved outputs; posted two wording points. Took #45 (it starts after 14:00) and asked Cristiano for a switch in `main.ipynb` that opens 2022, and for the main metric. Asked phantodevc to hand #48 over: I have no commits on `main.ipynb`. Copied the matcher-against-baselines table from `main.ipynb` @ f38cebd into Evaluation. Checked `raw_merged.zip` from the team's release (251,180 valid files, 13,761 companies, all 5,061 of mine inside); it still has to be merged into my `data/raw`. Planned the structure of the write-up and the video.
- **Result:** Evaluation, "The matcher against the baselines, on validation (card #170)": the matcher keeps 80 of the 84 links the register confirms and makes 130 it doesn't confirm, against 375 for the same-name rule (9 against 85 for common surnames).
- **AI used for:** Claude (claude.ai, Opus 5.5) reviewed #183, wrote and posted the comments on #183, #45 and #48, checked the zip, copied the table into Evaluation from the saved outputs and drafted the write-up and video plans, at my request.
- **Next:** merge `raw_merged.zip` into `data/raw`. After 14:00, run #45 once. Write the write-up text and record the video. Decide whether I person-check the 2 unsure pairs and a sample of the matcher's 130 unconfirmed links (#46). Fresh-run test at about 16:30–17:00.
- **Blocked by:** #45 waits for the model at 14:00 and the 2022 switch.

## 2026-11-15 14:56
- **Task:** #45 Run the test set once and log the final numbers, and the person check of the 50 hand-check pairs (for #46)
- **Did:** Merged the team's crawl into `data/raw` with the steps on #159 (the check printed `{'2021': 6914, '2022': 6847} 13761`) and fixed the venv (ipywidgets; ipykernel and nbconvert to run notebooks). Set `OPEN_TEST = True` and ran `main.ipynb` once, restart and run all, at 14:11 on 74d8a97: no errors, and the name guard found no real name. Added the "What it shows" cell under the TEST tables. Checked the 50 AI-judged pairs myself on a blind page from `real_slice.handcheck_html` (no group, band, match score or AI verdict); the verdicts are in `notebooks/jonas_handcheck.csv`, held back for #46. Filled Evaluation: test set first used, two Results rows, Final result, By group, Limits, and the person check per group.
- **Result:** on the 6,847 test companies the matcher makes 534 links to an earlier insolvent company that the register doesn't confirm, against 1,537 for the same-name rule (112 against 442 for common surnames), at a recall of 0.918 against 0.980. My person check agrees with the AI on 48 of the 48 pairs it decided and settles its 2 unsure ones.
- **AI used for:** Claude Code (Opus 5.5) in VS Code downloaded and checked the merged zip, set up the kernel, ran the notebook once, built the blind page, compared my verdicts with the AI's, drafted the Evaluation text, the "What it shows" cell and the "How it works" note, and shared the work, at my request. The 50 verdicts are mine.
- **Next:** share the person-check file with #46 and write the write-up; record the video (#47); fresh-run test (#48) at about 16:30–17:00. Tell cristiano that `main.ipynb`'s own hand-check sample (cell 31) is not the 50 pairs the AI judged: they share only 8.
- **Blocked by:** nothing

## 2026-11-15 15:14
- **Task:** #193 Person-check the 50 AI-judged pairs
- **Did:** Created and started #193. Rewrote `notebooks/jonas_handcheck.csv` as UTF-8 without BOM with LF line endings (header `pair_id,verdict`, my 50 verdicts unchanged) and added `**/data/` to `.gitignore`, so all of `data/` stays out of git. Shipped both through pull request #194.
- **Result:** #193 closed with its "How it works" note, and CI on `main` passed. Evaluation's hand-check section points to the file.
- **AI used for:** Claude Code (Opus 5.5) in VS Code created the card, changed the file's format and the ignore line, shipped them and drafted the "How it works" note, at my request. The verdicts are mine.
- **Next:** write-up (#46), video (#47), first submission (#51) at 18:00.
- **Blocked by:** nothing

## 2026-11-15 15:40
- **Task:** #196 Update three outdated text cells in main.ipynb (agreed with cristiano in the team chat)
- **Did:** Fixed three markdown cells in `main.ipynb`: the hand-check cell now says the judged pairs were drawn in `cristiano_calibration.ipynb` (8 of 50 overlap with the notebook's own sample); "Where it fails" item 2 reports the verdicts of #89 and #46 with their caveats; item 7 says 2022 ran once (#45). Also re-ran the fresh-run test on a clean clone of `main` @ 803a8fa: no error in 12 s (posted on #48).
- **Result:** pull request #197, merged as 8b3bfab; checks green; #196 closed with its "How it works" note.
- **AI used for:** Claude (claude.ai, Opus 5.5) wrote the three texts from Evaluation's numbers, which I approved, opened and merged the pull request, and ran the fresh-run test, at my request.
- **Next:** the write-up (#46), then the demo video (#47) and the submissions (#51, #52).
- **Blocked by:** nothing

## 2026-11-15 15:55
- **Task:** #198 Remove jonas_real.ipynb before judging; Idea.md brought up to date
- **Did:** The repo is public, so I removed my Saturday scratch notebook `notebooks/jonas_real.ipynb` (its outputs showed real company names, and its 438-company numbers on the earlier label disagreed with `main.ipynb` and Evaluation); Evaluation now names `real_slice.handcheck_sample` instead. Updated Idea.md's "How we measure" to Sunday's decisions: the main metric (unconfirmed links next to recall), the stricter label, and the open question on what score makes it useful, now settled.
- **Result:** pull request #199, merged as 71be093; checks green; #198 closed with its "How it works" note. Idea.md shared straight to main.
- **AI used for:** Claude (claude.ai, Opus 5.5) made the removal and the text changes from the decision notes, which I approved, and opened and merged the pull request, at my request.
- **Next:** the write-up (#46) and the demo video (#47), each in its own chat; the submissions (#51, #52).
- **Blocked by:** nothing

## 2026-11-15 22:01
- **Task:** #47 Record the 2-minute video (the demo app it is filmed from)
- **Did:** Ran the demo app (`python app/server.py`) on my PC on the real crawl. The film's last restyle had never reached my copy, so `app/static/index.html` and `app.css` were re-applied from the video chat's own edits (OKLCH colours, wordmark-only header, no logo in the result panel). Checked the notebook's demo company on the page: Warning, match score 0.95, no console errors. Shared `app/`, `requirements-demo.txt` and the demo's credits through pull request #200 and merged it.
- **Result:** pull request #200, merged as 53f90bb; checks green on the pull request and on `main`; #47 closed. `scripts/check.sh` ok; `pytest -q` 323 passed, 1 skipped; on a fresh clone the app starts on the tiny world and answers every endpoint.
- **AI used for:** Claude (claude.ai, Opus 5.5) built the demo app and the video earlier at my request; in this session it re-applied the film's styling, tested the page, and opened and merged the pull request, at my request.
- **Next:** post #47's "How it works" note; final submission (#52).
- **Blocked by:** nothing
