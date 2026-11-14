# Modules

Up: [[Project]]

The boxes we build. Modularity is the point: each box is one file with fixed inputs and outputs (ADR-005), its own tests on the tiny world, and one owner. Swapping a method or a data source never touches another box. Claim a box's card on the board before you start it.

| Box | File | Takes → gives | Enforces | Layer | Lead | Cards |
|---|---|---|---|---|---|---|
| Tiny world | `tests/tiny_world.py` | nothing → about 30 hand-made mentions and claims, plus the true answers | all rules | L0 | integration | #21 |
| Evidence schema | `src/evidence.py` | nothing → column lists, id builder, raw-file manifest, row checks | R1, R2, R7 | L0 | integration | #22 |
| Source adapter | `src/ingest_companies_house.py` | API key and slice settings → raw JSON (hashed) → mentions and claims | R1, R2 | L0, L1 | data | #19, #24, #25 |
| Baseline | `src/baseline.py` | mentions → "same name, same person" pairs and the name-match flag rule | none (it's the bar) | L0 | data | #27 |
| Observed graph | `src/graph.py` | claims → observed graph | R3 | L0 | integration | #26 |
| Entity resolution | `src/resolve.py` | mentions → candidate pairs with `p` and the features behind it | R6 | L1 | model | #30, #31 |
| Possible worlds | `src/infer.py` | observed graph, pairs and seed → inferred graph (`p`, `method`, `depends_on`) | R4, R7 | L1, L2 | model | #32, #33, #37 |
| Decision layer | `src/decide.py` | `p` for the query and three costs → FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the reason | R8 | L1 | model | #34, #43 |
| Interface | `src/interface.py` | both graphs and the decision → interactive graph, evidence panel, what-if toggles, cost sliders | R3 | L1, L2 | integration | #35, #38, #44 |
| Evaluation | `src/evaluate.py` | predictions, labels and groups → metrics vs baseline, calibration, results by group, failures | none | L0–L2 | data | #28, #39, #40, #41, #42, #45 |
| Rule tests | `tests/test_rules.py` | tiny world → one test per rule | R1–R8 | L0 | integration | #23 |
| Main notebook | `notebooks/main.ipynb` | every box → the story top to bottom, outputs saved | none | L0–L2 | integration | #20, #29, #36, #48 |

Submission cards: #46 write-up, #47 video. Leads are roles until card #3 settles who is who: **data** is the data and evaluation lead, **model** the model lead, **integration** the product and story lead.

## Build order
- **L0, target Sat 13:00:** the tiny world runs through every box, the rule tests pass, the baseline gives its first number.
- **L1, target Sat 19:00:** the real slice runs through every box, plus interface v1. That is a complete submission.
- **L2, target Sun 12:00:** what would flip each link, what-if toggles, cost sliders, false flags by name commonness, failure gallery.
- **L3, stretch:** the one detail to ask, a public demo link.

When something slips, cut from the top layer, never the deadline.

## The contracts
What passes between boxes. Change one only on a call, and update this note in the same push.

- **mentions:** `mention_id`, `kind` (company or person), `name` as written, attributes as written, and provenance: `source`, `record_ref`, `origin`, `adapter`.
  - Companies: company number, status, incorporation, dissolution and insolvency dates, sector code, postcode.
  - People: birth month and year, nationality, postcode, the register's officer id.
- **claims:** `claim_id`, `subject`, `relation` (`director_of` or `controls`), `object`, `valid_from`, `valid_to`, and the same provenance.
- **pairs:** `a`, `b`, `p`, `features`, `method` (ours or baseline).
- **inferred links:** `link_id`, `a`, `b`, `kind` (`same_entity` or `predecessor`), `p`, `method`, `depends_on`.
- **decision:** `query`, `decision`, `p`, `costs`, `reason`, and from L2 on `flip`, the uncertain match that would change it.
