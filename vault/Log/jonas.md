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
