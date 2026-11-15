# Modules

Up: [[Project]]

The boxes we build. Modularity is the point: each box is one file with fixed inputs and outputs (ADR-005) and its own tests on the tiny world. Boxes import only `src/evidence.py`, and only `main.ipynb` calls them. Swapping a method or a data source never touches another box. Whoever holds a box's card owns its file until the card is done. The order to pick cards in is in Plan.

| Box | File | Takes → gives | Enforces | Layer | Cards |
|---|---|---|---|---|---|
| Evidence schema and observed graph | `src/evidence.py` | nothing → the six shared tables, the id builder, the checks, and the observed graph as a filter on claims | R1, R2, R3, R7 | L0 | #22 |
| Tiny world | `tests/tiny_world.py` | nothing → about 30 hand-made mentions and claims with invented names, plus the true answers | all rules | L0 | #21 |
| Crawler | `src/crawl_companies_house.py` | API key (`COMPANIES_HOUSE_API_KEY` in `.env`) and the slice → raw API answers in `data/raw/`, byte for byte, in the layout the adapter reads, plus appointment lists and a name search per director. Under 600 requests per 5 minutes, resumes where it stopped | R1 | L1 | #24, #71, #72, #73 |
| Crawl merge | `src/merge_crawls.py` | zips of `data/raw/` from several computers → one `data/raw/`: a file is copied only when it isn't there yet, byte for byte, and `query_companies.csv` gains the companies it doesn't list. Running it again adds nothing | R1 | L1 | #159, #162 |
| Source adapter | `src/ingest_companies_house.py` | API key and slice settings → raw JSON (each hash kept in `record_ref`) → mentions, claims and labels, with masked display columns | R1, R2, masking | L0, L1 | #19, #24, #25, #49 |
| Baselines | `src/baseline.py` | mentions and claims → pairs and decisions for flag nothing, same name means same person, and Companies House officer links | none (they're the bar) | L0 | #27 |
| Entity resolution | `src/resolve.py` | mentions → pairs with `p`. The officer id is the label, never a feature | R6 | L1 | #30, #31 |
| Decision layer | `src/decide.py` | pairs, claims, labels and costs → links and decisions: P(predecessor) by the formula, P(fail) by a straight line, then FLAG, CLEAR or NOT ENOUGH EVIDENCE with the reason and the flip | R4, R8 | L1, L2 | #33, #34, #37 |
| One identity per director | `src/infer.py` | pairs and seed → P(predecessor) with the one-identity rule, closed form plus a possible-worlds check | R4, R7 | L2 | #32 |
| Rule tests | `tests/test_rules.py` | tiny world → R2, R3, R4, R6 and R8 first, then R1 cheaply and R7 with #32. R5 is skipped with one source | R1–R8 | L0 | #23 |
| Evaluation | `src/evaluate.py` | decisions and labels → metrics vs the three baselines, calibration, false flags by name commonness, failures, figures | none | L0–L2 | #28, #39, #40, #42, #45 |
| Interface | `src/interface.py` | the shared tables → a static graph image for GitHub, a local view, what-if toggles, cost sliders. Display columns only | R3, masking | L1, L2 | #35, #38 |
| Main notebook | `notebooks/main.ipynb` | every box → the story top to bottom, outputs saved | none | L0–L2 | #29, #36 |

Other cards: #20 repo skeleton, #46 write-up, #47 video, #50 Credits and README, #48 fresh-run test, #51 first and #52 final submission.

## Build order
- **L0, target Sat 13:00:** the tiny world runs through every box, the rule tests pass, the three baselines give their first numbers.
- **L1, target Sat 19:00:** the real slice runs through every box with the formula. The decision layer, interface v1 and masking work. False flags by name commonness and five failures are measured. That is a complete submission.
- **L2, target Sun 12:00:** the one-identity rule as the one measured improvement, what would flip each decision, what-if toggles, cost sliders, static figures.
- **Cut, listed as next steps in the write-up:** robustness tests, the one detail to ask, a public demo link.

When something slips, cut from the top layer, never the deadline.

## The six shared tables
Defined once in `src/evidence.py`, each with its check. Change one only on a call: bump the schema version and update this note in the same push.

| Table | Written by | Read by | Columns |
|---|---|---|---|
| **mentions** | adapter | every box | `mention_id`, `kind` (company or person), `name` as written, `display_name` (masked), the attributes below, and provenance (`source`, `record_ref` with raw file, row and hash, `origin`, `adapter`) |
| **claims** | adapter | evidence, decision layer, interface | `claim_id`, `subject`, `relation` (`director_of` or `controls`), `object`, `valid_from`, `valid_to`, provenance |
| **labels** | adapter | decision layer, evaluation | `company_id`, `formed_on`, `failed` (liquidation, administration or dissolution within 24 months), `split` (train, validation or test) |
| **pairs** | entity resolution, baselines | decision layer, evaluation, interface | `a`, `b`, `p`, `features`, `method`, `label` (same officer id, for training and checking only) |
| **links** | decision layer | interface, evaluation | `query`, `predecessor`, `via` (the pair it rests on), `p`, `method`, `depends_on` |
| **decisions** | decision layer, baselines | interface, evaluation | `query`, `method`, `decision`, `p_predecessor`, `p_fail`, `reason`, `flip` |

Attributes as written, in this order in `MENTION_COLS`:
- Companies: `company_number`, `status`, `incorporated_on`, `dissolved_on`, `insolvency_on`, `sic_code`.
- People: `birth_month`, `birth_year`, `nationality`, `officer_id` (the register's officer id, used as the matcher's label only).
- Both: `postcode`, then `display_postcode` (the district only).

Outputs show display columns only: names become pseudonyms, birth dates are never shown, and postcodes keep only the district.

Conventions: dates are ISO strings (YYYY-MM-DD). `company_id`, `query` and `predecessor` are company numbers; `a`, `b`, `subject` and `object` are mention ids. Schema version 1 (`SCHEMA_VERSION` in `src/evidence.py`).

`flip` in decisions is empty, or the match to check first: `via` (the pair), `predecessor`, `p`, `if_same_person` (which what-if changes the decision) and `becomes` (the new decision). Built by `flip` in `src/decide.py`.
