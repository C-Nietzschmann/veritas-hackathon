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
- **Did:** C-Nietzschmann reviewed #117. I applied his patch unchanged: stricter row checks (empty ids, swapped claims, dates not in `YYYY-MM-DD`, a `record_ref` in the wrong shape) and end dates after the as-of date now hidden in the graph. I added the same date check for the three company dates, then merged both into #118. ADR-001 now says "on or before t". I replied on #117 to his five open points.
- **Result:** 23 tests pass on #117 and 33 on #118. Both still wait for me to read them before they merge.
- **AI used for:** Claude (claude.ai) checked his patch, applied it, wrote the company-date check and drafted the reply, all at my request.
- **Next:** read and ship #117, then #118. For the call: where the as-of view for company dates lives, which insolvency types count (members' voluntary liquidation doesn't), and which SIC code we keep. Then the baselines (#27).
- **Blocked by:** nothing
