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

## 2026-11-14 13:50
- **Task:** #35 interface v1 (#98, #99, #100) and #109 example figure (cards on the board)
- **Did:** Added `evidence_table` (#100) and `show()` (#99) to `src/interface.py`, and three cells to the Demo section of `main.ipynb` that show TW000002's decision, reason, graph and evidence table, plus the polite answer for a company outside our data (#109). Ran the notebook on a copy and kept only the new cells' outputs, so the teammates' cells are unchanged. Shipped as PR #143.
- **Result:** #98, #99, #100 and #109 closed, #35 at 3/3, `main` green with 170 tests. The name guard checked 889 real names from my crawl against the notebook: none found.
- **AI used for:** Claude Code wrote the table, `show()`, the Demo cells and tests, ran the notebook, shipped the PR and drafted the notes and this entry. I read `interface.py`.
- **Next:** crawl part 2 keeps running. Pick the next free card.
- **Blocked by:** nothing
