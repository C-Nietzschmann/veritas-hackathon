Up: [[Log]]

## 2026-11-14 06:45
- **Task:** Setup (card on the board)
- **Did:** Cloned the repo, switched on `git sync`, set my git identity, signed in through GitHub Desktop, started this log.
- **AI used for:** Claude Code followed vault/Setup.md for me and ran this first `git sync`.
- **Next:** install Obsidian, open the vault, claim my Setup card, read Home and the first five Protocols.

## 2026-11-14 07:40
- **Task:** #4 Setup (card on the board)
- **Did:** Logged in to the GitHub CLI (with project access), claimed #4, removed its Colab box after the team dropped Colab, opened the vault in Obsidian, filled in my availability in Team.
- **Result:** notes only. #4 still open: reading the protocols and my role (decided on #3).
- **AI used for:** Claude Code read the whole vault, ran the GitHub login, moved and edited my card, reviewed the teammates' Colab change and wrote this entry.
- **Next:** kickoff call 08:00, agree roles (#3), close #4.
- **Blocked by:** nothing

## 2026-11-14 12:34
- **Task:** #60 API client (handed over) and #110 masking functions (cards on the board)
- **Did:** Built a draft `get()` for #60, then handed #60 to jonas, because his crawl (#24) already talks to the API and the team needs one client. Built `src/mask.py` for #110: `pseudonym()` (SHA-256, same name gives the same label) and `mask_postcode()` (district only), with 7 tests. Shipped as PR #136.
- **Result:** #110 closed, `main` green with 116 tests. Not wired into the adapter yet (#111).
- **AI used for:** Claude Code wrote the API client draft, the masking functions and their tests, shipped the PR and drafted the "How it works" note and this entry. I read the code and can explain it.
- **Next:** raise on the call: who wires masking into the adapter (#111), and whether company names named after their owner get masked. Then pick the next free card.
- **Blocked by:** nothing

## 2026-11-14 12:55
- **Task:** #112 name guard (card on the board)
- **Did:** Built `scripts/name_guard.py`: it searches `main.ipynb`'s cells and saved outputs for every real director's name in the local raw data, written either way round. `scripts/check.sh` now runs it before every share where the raw data is present. Shipped as PR #138.
- **Result:** #112 closed, `main` green. A planted "Daniel Harrow" in a notebook output made `check.sh` refuse to share.
- **AI used for:** Claude Code picked the free card, wrote the guard and its 7 tests, tested it end to end, shipped the PR and drafted the "How it works" note and this entry. I read it and can explain it.
- **Next:** say on the call that `check.sh` gained the name guard. Pick the next free card.
- **Blocked by:** nothing

## 2026-11-14 13:25
- **Task:** #24 crawl part 2, and #98 evidence graph (cards on the board)
- **Did:** Made my own Companies House application and key, and started part 2 of 2 of the 2021 crawl on my computer with jonas's fixed crawler (PR #134). Built `draw_graph` in `src/interface.py` for #98: register facts solid, guessed matches dashed and labelled in words, labels from the display columns only. Opened PR #143 as work in progress. Claimed parent #35.
- **Result:** crawl measured at 450 companies an hour (8.0 s each, 13:03 to 13:13), so my half of 2021 would take about 3.6 days if left to run. #98: 5 tests, all 164 pass. The crawl log slipped into PR #143 and was taken out again; no personal data was in it.
- **AI used for:** Claude Code created the application and key in the browser (I pasted the key into .env myself), set up and measured the crawl, wrote `draw_graph` and its tests, opened the PR and wrote this entry.
- **Next:** add the example picture to `main.ipynb` when Cristiano's notebook changes slow down, then ship #98. Agree with jonas when the crawl stops and how my data/raw reaches the adapter.
- **Blocked by:** nothing

## 2026-11-14 13:35
- **Task:** #35 interface v1 (#98, #99, #100) and #109 example figure (cards on the board)
- **Did:** Added `evidence_table` (#100) and `show()` (#99) to `src/interface.py`, and three cells to the Demo section of `main.ipynb` that show TW000002's decision, reason, graph and evidence table, plus the polite answer for a company outside our data (#109). Ran the notebook on a copy and kept only the new cells' outputs, so the teammates' cells are unchanged. Shipped as PR #143.
- **Result:** #98, #99, #100 and #109 closed, #35 at 3/3, `main` green with 170 tests. The name guard checked 889 real names from my crawl against the notebook: none found.
- **AI used for:** Claude Code wrote the table, `show()`, the Demo cells and tests, ran the notebook, shipped the PR and drafted the notes and this entry. I read `interface.py`.
- **Next:** crawl part 2 keeps running. Pick the next free card.
- **Blocked by:** nothing

## 2026-11-14 13:42
- **Task:** #103 confirm and reject a match (card on the board, parent #38)
- **Did:** Added `interface.what_if`: a person confirms (p = 1) or rejects (p = 0) a match, every other match stays as it was, then the decision layer runs again. Two Demo cells in `main.ipynb` show it. Closed #35 after its three sub-tasks shipped. Shipped #103 as PR #147.
- **Result:** rejecting TW000002's one match turns FLAG into CLEAR. #38 at 1/2, `main` green with 205 tests.
- **AI used for:** Claude Code wrote `what_if`, its tests and the Demo cells, shipped the PR and drafted the note and this entry. I can explain `what_if`.
- **Next:** on the call: may we add ipywidgets for the cost sliders (#104) and buttons? Crawl part 2 keeps running.
- **Blocked by:** #104 waits for the call's yes on ipywidgets

## 2026-11-14 13:48
- **Task:** #104 cost sliders (card on the board, parent #38)
- **Did:** Added `interface.cost_sliders`: three sliders for the costs, the thresholds and decision next to them, and a Reset button to the agreed costs. A Demo cell in `main.ipynb` shows it and prints the agreed line for GitHub. Added ipywidgets to requirements.txt and Credits after the team agreed on the call. Shipped as PR #148.
- **Result:** #104 closed, #38 at 2/2, `main` green with 207 tests.
- **AI used for:** Claude Code wrote the sliders, tests and Demo cell, shipped the PR and drafted the note and this entry. I can explain how the sliders work.
- **Next:** close #38 if the team agrees. Crawl part 2 keeps running.
- **Blocked by:** nothing

## 2026-11-14 14:04
- **Task:** #113 Credits, #115 README, #102 flip in the interface, #114 pinned requirements, #105 name-commonness bands (cards on the board)
- **Did:** Completed Credits (every library, Chow's rule, the AI tools, the Companies House licence checked on its official page) and closed #113. Wrote the README (PR #150, open until the fresh-run test #48); its run steps worked word for word in a fresh clone. Shipped #102 (PR #151): the match to check first is red in the picture, marked in the table, and named in one sentence by `show()`. Shipped #114 (PR #152): every library pinned. Shipped #105 (PR #153): `name_commonness` bands from counts only. Closed #38.
- **Result:** `main` green. #37 at 2/2, #39 at 1/2, #50 at 2/3. Bands on my local crawl (2,223 director records): 737 rare, 1,245 medium, 241 common.
- **AI used for:** Claude Code wrote the code, tests, Credits and README, checked the licence and the run steps, shipped the PRs and drafted the notes and this entry. I can explain each change.
- **Next:** #48 fresh-run test on Sunday, then ship the README. Crawl part 2 keeps running.
- **Blocked by:** nothing

## 2026-11-14 14:28
- **Task:** #62 count the positives (card on the board, parent #19), and #37 closed
- **Did:** Counted failures and positives on my crawl sample (part 2 of 2021, first 482 query companies) with the team's adapter, label and split code; wrote the table in Idea under the slice and the rate limit in Credits. Closed #37 after both sub-tasks shipped.
- **Result:** 173 of 482 failed within 24 months (only 2 by insolvency), and 7 positives (3 by officer id): well under the 50 the plan asks for. Estimate: about 3,400 companies for 50.
- **AI used for:** Claude Code wrote the counting script (kept outside the repo), ran it, and drafted the Idea table, the card note and this entry.
- **Next:** on the call: keep crawling, widen the years, or use the looser predecessor definition (#19 stays open for that). Crawl part 2 keeps running.
- **Blocked by:** nothing

## 2026-11-15 09:23
- **Task:** #24 / #159 stop and upload my crawl, #19 count the positives on the merged data
- **Did:** Stopped crawl part 2 of 2021 at 08:58 (a minute early) with 6,066 companies, uploaded `raw_phantodevc.zip` to the draft release and wrote it on #159. Downloaded cristiano's merged database and checked it (6,914 of 2021, 6,847 of 2022). Counted failures and positives on all of 2021 and posted them on #19 and in Idea.
- **Result:** 2,305 of 6,914 failed (16 by insolvency). Positives: 76 by name and birth date, 22 by officer id. A predecessor goes with a lower failure rate: 10.7% against 33.9% by officer id.
- **AI used for:** Claude Code ran the stop and upload at 09:00 as I asked, ran the counting script (kept outside the repo) and drafted the #19 comment, the Idea table and this entry.
- **Next:** the call decides what the lower failure rate means for the line (#94) and the costs. #48 fresh-run test, then ship the README.
- **Blocked by:** nothing

## 2026-11-15 10:40
- **Task:** #106 false flags per band, #115 README, #48 fresh-run dry run; closed parents #39 and #50
- **Did:** Built `company_bands` and `false_flags_by_band` in `src/evaluate.py` (PR #167), ran ours and the three baselines on the 1,552 merged validation companies and wrote the table in Evaluation under By group. Fixed the name guard: a director written "." matched punctuation. Diagnosed why a predecessor goes with fewer failures and posted the fix options on #19. Dry-ran the fresh-run test, then shipped the README (PR #150).
- **Result:** same name falsely flags 0% / 3.8% / 9.0% from rare to common surnames; ours flags nothing (all NOT ENOUGH EVIDENCE, the line slopes down). main.ipynb runs from a fresh clone in 32 s. #39 and #50 closed.
- **AI used for:** Claude Code wrote the code, tests and scratch scripts, ran them, shipped the PRs and drafted the notes, comments and this entry. I can explain each change.
- **Next:** #48 real run at 17:00 (better by someone who didn't write the notebook); #107 and #108 once main.ipynb runs on real data.
- **Blocked by:** the team's choice on #19 (what we claim), and who moves main.ipynb to real data

## 2026-11-15 11:07
- **Task:** #107 and #108 figures (parent #42); new card #170 for cristiano
- **Did:** Added `pr_figure`, `false_flag_figure` and `reliability_figure` to `src/interface.py` with tests, and drew them under Evaluation in main.ipynb (PR #173, closes both cards). Created #170 "Run main.ipynb on the real slice" and tagged cristiano on it (not assigned, per the claiming rule).
- **Result:** #42 at 3/3. The figures show the tiny world for now and redraw on real data once #170 is done. 310 tests pass.
- **AI used for:** Claude Code wrote the figure functions, tests and cells, checked the pictures, shipped the PR and drafted the notes and this entry. I can explain each change.
- **Next:** #48 real fresh-run at 17:00; close #42 once the figures show real data.
- **Blocked by:** #19 decision and #170

## 2026-11-15 11:25
- **Task:** #166 name guard: names ending in a full stop, and speed
- **Did:** Swapped `\b` for "no letter or digit next to it" edges, added a quick `in` test before the regular expression, and read only the officers folder (PR #181).
- **Result:** `check.sh` with the real crawl: about 9 s instead of several minutes, the same 49,253 names, no real name in main.ipynb. 314 tests pass.
- **AI used for:** Claude Code wrote the change and tests, timed it, shipped the PR and drafted the note and this entry. I can explain it.
- **Next:** #48 real fresh-run at 17:00; close #42 once #170 brings real data.
- **Blocked by:** nothing

## 2026-11-15 11:41
- **Task:** #180 call the matcher's p a score, not a probability
- **Did:** Changed the decision reason to "match score 0.90 out of 1" and the two Idea sentences (PR #184). Asked cristiano on PR #182 to change the two notebook sentences in his rewrite; noted the write-up wording and the 2 unsure pairs on #46. Checked every tracked file against the crawl's real names: none leaked (only invented test names).
- **Result:** #180 closed. 318 tests pass.
- **AI used for:** Claude Code made the change, the test and the comments, shipped the PR and drafted the note and this entry. I can explain it.
- **Next:** #48 real fresh-run at 17:00; close #42 once #182 merges.
- **Blocked by:** nothing

## 2026-11-15 11:59
- **Task:** #92 one identity against the formula; the #106 table on the new label
- **Did:** Worked out #92 from main.ipynb's failure line and wrote it in Evaluation; replaced my band table with the numbers main.ipynb prints on the stricter label (@ f38cebd). #19 and #42 were already closed by the team.
- **Result:** same name falsely flags 0% / 3.6% / 10.1% from rare to common surnames, and every baseline flag is a false flag. Formula and one identity both clear everything: the line (1.4% to 1.8%) is under CLEAR for any P(predecessor).
- **AI used for:** Claude Code read the notebook outputs, wrote the Evaluation sections and the card note, and drafted this entry. I can explain both results.
- **Next:** #48 real fresh-run at 17:00.
- **Blocked by:** nothing

## 2026-11-15 14:20
- **Task:** #48 Run the fresh-run test
- **Did:** Fresh clone of `main` @ 74d8a97, new venv, then the three lines in Notebook Workflow. Ran it twice: as the card asks (no data, tiny world) and once more with only the crawl put in `data/raw`.
- **Result:** both ran top to bottom with no error: 29 s on the tiny world, 5.1 min on the real slice. Every saved output matched `main` cell for cell, except the run time. Nothing broke, so no new cards. Closed #48.
- **AI used for:** Claude Code ran the clone, the install and both runs, compared the outputs, and wrote the card comment and this entry, at my request.
- **Next:** if `main.ipynb` changes after the 2022 run (#45), run the same three lines once more before 18:00.
- **Blocked by:** nothing
