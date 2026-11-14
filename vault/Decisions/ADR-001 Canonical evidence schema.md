# ADR-001 Canonical evidence schema

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09, revised 07:55 after the review on card #16
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
Every source is turned into the same two tables, **mentions** and **claims**. Both keep the source's own wording and point back to the untouched raw record they came from.

- **Mentions:** one row per entity as one record describes it: `mention_id`, `kind` (person, company …), `name` as written, and the source's own attributes as written (registration number, address, dates).
- **Claims:** one row per relationship a source states between two mentions: `claim_id`, `subject` and `object` (mention ids), `relation`, and `valid_from` and `valid_to` (when the source says the relationship started and ended; either may be empty).
- **Provenance on every row:** `source` (dataset and version), `record_ref` (raw file and row), `origin` (who first published it, if this source copies someone else, see R5) and `adapter` (which code made the row).
- Ids are built from stable keys the source gives (a company number, an appointment link), falling back to the record and the position in it. Never at random, so a rerun gives the same ids (R7).

## Why
With one shape for every source, entity resolution and inference never need to know where the data came from (ADR-005), and provenance travels with every row (R2).

Mentions are not entities. Two records that look like the same company stay two mentions. Deciding whether they are one entity is entity resolution's job (ADR-003, R6).

The alternative was letting each source keep its own table and having later code handle each one. That's quicker for a single source, but every new source then changes the reasoning code, and provenance gets lost in joins.

## What it changes
- Ingestion adapters output exactly these two tables. Nothing downstream opens a raw file.
- Raw downloads land in `data/raw/` and are never edited. Each raw response's hash is stored in the `record_ref` of the rows it produced (R1), with no separate manifest. Datasets stay out of git: the notebook downloads them.
- **As-of rule:** a decision about date t only uses rows dated before t. A crawl made today also shows what happened after t, so this is where leakage would creep in. The train-on-earlier, test-on-later split (Finance must-have) runs on these dates.

## Open, set at scope lock
- The attribute columns of mentions, once the dataset is chosen. Proposed for Companies House:
  - Companies: number, status, incorporation, dissolution and insolvency dates, sector code, postcode.
  - People: birth month and year, nationality, postcode, the register's officer id.
- The full list is in Modules. Adding a column is fine. Renaming or removing one means updating this note.

Next: [[ADR-002 Separate observed and inferred graphs]]
