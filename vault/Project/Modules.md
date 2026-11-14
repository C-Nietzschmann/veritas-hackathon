# Modules

Up: [[Project]]

The boxes we build. Modularity is the point: each box is one file with fixed inputs and outputs (ADR-005), its own tests on the tiny world, and one owner. Swapping a method or a data source never touches another box. Claim a box's card on the board before you start it.

Updated after the review on card #16: the lighter MVP uses the formula, and possible worlds becomes Sunday's measured improvement.

| Box | File | Takes → gives | Enforces | Layer | Lead | Cards |
|---|---|---|---|---|---|---|
| Tiny world | `tests/tiny_world.py` | nothing → about 30 hand-made mentions and claims, plus the true answers | all rules | L0 | integration | #21 |
| Evidence and observed graph | `src/evidence.py` | nothing → column lists, id builder, row checks, and the observed graph as a filter on claims | R1, R2, R3, R7 | L0 | integration | #22 |
| Source adapter | `src/ingest_companies_house.py` | API key and slice settings → raw JSON (each hash kept in `record_ref`) → mentions and claims | R1, R2 | L0, L1 | data | #19, #24, #25 |
| Baselines | `src/baseline.py` | mentions → three baselines: flag nothing, same name means same person, Companies House officer links | none (they're the bar) | L0 | data | #27 |
| Entity resolution | `src/resolve.py` | mentions → candidate pairs with `p`. The officer id is the label, never a feature | R6 | L1 | model | #30, #31 |
| Decision layer | `src/decide.py` | pairs and costs → P(predecessor) by the formula, P(fail) by a straight line, then FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the reason and the match that would flip it | R4, R8 | L1, L2 | model | #33, #34, #37 |
| One identity per director | `src/infer.py` | pairs and seed → P(predecessor) with the one-identity rule, closed form plus a possible-worlds check | R4, R7 | L2 | model | #32 |
| Masking | `src/mask.py` | any table or figure label → names, birth dates and postcodes masked | public-data rule | L1 | integration | #49 |
| Interface | `src/interface.py` | graphs and the decision → a static graph image for GitHub, a local view, what-if toggles, cost sliders | R3 | L1, L2 | integration | #35, #38 |
| Evaluation | `src/evaluate.py` | predictions, labels and groups → metrics vs the three baselines, calibration, false flags by name commonness, failures, figures | none | L0–L2 | data | #28, #39, #40, #42, #45 |
| Rule tests | `tests/test_rules.py` | tiny world → tests for R2, R3, R4, R6 and R8 first, then R1 cheaply and R7 with #32. R5 is skipped with one source | R1–R8 | L0 | integration | #23 |
| Main notebook | `notebooks/main.ipynb` | every box → the story top to bottom, outputs saved | none | L0–L2 | integration | #20, #29, #36, #48 |

Submission cards: #46 write-up, #47 video, #50 Credits and README, #51 first submission, #52 final submission. Leads are roles until card #3 settles who is who: **data** is the data and evaluation lead, **model** the model lead, **integration** the product and story lead.

## Build order
- **L0, target Sat 13:00:** the tiny world runs through every box, the rule tests pass, the three baselines give their first numbers.
- **L1, target Sat 19:00:** the real slice runs through every box with the formula. The decision layer, interface v1 and masking work. False flags by name commonness and five failures are measured. That is a complete submission.
- **L2, target Sun 12:00:** the one-identity rule as the one measured improvement, what would flip each decision, what-if toggles, cost sliders, static figures.
- **Cut, listed as next steps in the write-up:** robustness tests, the one detail to ask, a public demo link.

When something slips, cut from the top layer, never the deadline.

## The contracts
What passes between boxes. Change one only on a call, and update this note in the same push.

- **mentions:** `mention_id`, `kind` (company or person), `name` as written, attributes as written, and provenance: `source`, `record_ref` (raw file, row and hash), `origin`, `adapter`.
  - Companies: company number, status, incorporation, dissolution and insolvency dates, sector code, postcode.
  - People: birth month and year, nationality, postcode, the register's officer id (used as the label only).
- **claims:** `claim_id`, `subject`, `relation` (`director_of` or `controls`), `object`, `valid_from`, `valid_to`, and the same provenance.
- **pairs:** `a`, `b`, `p`, `features`, `method` (ours or a baseline), and `label` (same officer id, for training and checking only).
- **inferred links:** `link_id`, `a`, `b`, `kind` (`same_entity` or `predecessor`), `p`, `method`, `depends_on`.
- **decision:** `query`, `decision`, `p_predecessor`, `p_fail`, `costs`, `reason`, `flip` (the uncertain match that would change it).
