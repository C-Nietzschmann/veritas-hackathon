# Next 24 hours

Up: [[Project]]

> From Sat 08:00 to Sun 09:00 CET we finish 24 cards in three build groups, each ending at a gate, then close the day. No fixed roles: everyone claims their own cards (see the decision note). On the board each group is a **milestone**, and each card is split into small sub-tasks.

## 1. Scope lock · by Sat 10:00
Gate: the plan is agreed, everyone can run the repo, the data loads, and every person has a P0 card.

| Card | Task | Prio | Done by | Done when |
|---|---|---|---|---|
| #3 | Agree roles and schedule | P0 | Sat 08:45 | No fixed roles confirmed; everyone has claimed a first card |
| #16 | Confirm the architecture and build plan | P0 | Sat 08:45 | ADRs and rules marked confirmed on the call |
| #4, #5, #6 | Setup for each member | P0 | Sat 09:00 | Clone, `git sync`, Obsidian, `.venv`, Companies House API key in `.env` |
| #19 | Check Companies House access and pick the slice | P0 | Sat 10:00 | Slice loads within 30 minutes; counts and licence written in Idea |
| #20 | Create the repo skeleton | P0 | Sat 10:00 | `src/`, `tests/`, `notebooks/main.ipynb`, `requirements.txt` on `main`, CI green |

## 2. L0, the tiny world · by Sat 13:00 (skeleton gate 14:00)
Gate at 14:00: `main.ipynb` on `main` runs end to end on the tiny world, the rule tests pass, and the three baselines print their first numbers into Evaluation. The real crawl (#24) starts in this window and runs in the background.

| Card | Task | Prio | Done by | Done when |
|---|---|---|---|---|
| #21 | Build the tiny world with known answers | P0 | Sat 11:30 | About 30 hand-made mentions and claims with the true answers, in `tests/` |
| #22 | Write the evidence schema, checks and observed graph | P0 | Sat 12:00 | Column lists, id builder and row checks; observed graph built from claims only |
| #28 | Define the label and the time split | P0 | Sat 12:00 | Label and the 2021 train, validation and 2022 test cohorts written in Evaluation |
| #25 | Turn raw Companies House data into mentions and claims (tiny world first) | P0 | Sat 12:30 | The adapter turns sample raw records into the two tables, with their source on every row |
| #23 | Write the rule tests | P0 | Sat 12:30 | One test per kept rule, passing on the tiny world |
| #27 | Build the three baselines | P0 | Sat 13:00 | Each baseline returns the decision format; first numbers on the tiny world |
| #29 | Run `main.ipynb` end to end on the tiny world | P0 | Sat 13:00 | Restart and run all passes; pushed with outputs |

## 3. L1, the real slice · by Sat 19:00 (MVP gate 21:00)
Gate at 21:00: on the call, a real company number goes in and a masked decision with its evidence comes out; ours and the baselines are scored on validation. Check-in at 18:00. If L1 isn't running by 19:00, shrink the work inside the cards (smaller slice, fewer features, plainer interface), never the gate.

| Card | Task | Prio | Done by | Done when |
|---|---|---|---|---|
| #24 | Crawl the Companies House slice | P0 | Sat 14:00 | Raw records for the whole slice in `data/raw/` (not in git) |
| #25 | Mentions and claims for the real slice | P0 | Sat 15:00 | Both tables built from the crawl, checks passing |
| #30 | Build blocking and pair features | P0 | Sat 15:00 | Candidate pairs with features; blocking recall logged |
| #31 | Train and calibrate the matcher | P0 | Sat 16:30 | Every pair has a calibrated `p`; never merges |
| #33 | Fit the failure rate against P(predecessor) | P0 | Sat 17:30 | Fitted on training, checked on validation |
| #34 | Build the cost-based decision layer | P0 | Sat 18:00 | FLAG, CLEAR or NOT ENOUGH EVIDENCE with the reason, from the agreed costs |
| #49 | Mask names, birth dates and postcodes in every output | P0 | Sat 18:00 | Nothing personal in notebook outputs, figures or interface |
| #35 | Build interface v1: solid facts, dashed guesses, evidence on click | P0 | Sat 19:00 | A company number in, the graph and the decision out, masked |
| #39 | Check false flags by name commonness | P0 | Sat 19:00 | False flags per name-commonness band, ours vs baselines, on validation |
| #40 | Build the failure gallery | P0 | Sat 19:00 | Five wrong answers with a one-line reason each, masked |
| #36 | Run `main.ipynb` end to end on real data | P0 | Sat 19:00 | Restart and run all passes on the slice; pushed with outputs |

## 4. Close the day · Sat 21:00 to Sun 09:00
Gate at 23:00: `main` green, nothing left In Progress, everyone has run `git sync`. Then sleep.

| When | Task | Card | Done when |
|---|---|---|---|
| Sat 21:00 | MVP gate: run the demo once on the call | #36 | It runs on a real company number; what failed becomes a card |
| Sat 21:00–23:00 | Finish open L1 cards, fix what the demo showed | Group 3 | `main` green; the board is accurate |
| Sat 21:00–23:00 | Start Credits and `requirements.txt` while it's fresh | #50 | Companies House and every library used so far are listed |
| Sun 09:00 | Check-in: pick the one improvement and how it's measured | #32 | Written in Sync notes |

## After the 24 hours · Sunday
Not due in this window, listed so nothing is forgotten.

| By | Cards |
|---|---|
| Sun 12:00 (L2) | #32 one identity per director, #37 what would flip each decision, #38 what-if toggles and cost sliders, #42 static figures |
| Sun 14:00 | Feature freeze |
| Sun 18:00 | #45 test set once, #46 write-up, #50 Credits and README, #48 fresh-run test, #51 first submission |
| Sun 21:00 | #47 video, #52 final submission |
