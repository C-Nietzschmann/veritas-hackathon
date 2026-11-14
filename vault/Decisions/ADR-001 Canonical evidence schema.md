# ADR-001 Canonical evidence schema

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
Every source is turned into the same two tables, **mentions** and **claims**. Both keep the source's own wording and point back to the untouched raw record they came from.

- **Mentions:** one row per entity as one record describes it: `mention_id`, `kind` (person, company …), `name` as written, and the source's own attributes as written (registration number, address, dates).
- **Claims:** one row per relationship a source states between two mentions: `claim_id`, `subject` and `object` (mention ids), `relation`, and `observed_at` (when the source says it happened; may be empty).
- **Provenance on every row:** `source` (dataset and version), `record_ref` (raw file and row), `origin` (who first published it, if this source copies someone else, see R5) and `adapter` (which code made the row).
- Ids are built from the source, the record and the position in it, never at random, so a rerun gives the same ids (R7).

## Why
With one shape for every source, entity resolution and inference never need to know where the data came from (ADR-005), and provenance travels with every row (R2).

Mentions are not entities. Two records that look like the same company stay two mentions. Deciding whether they are one entity is entity resolution's job (ADR-003, R6).

The alternative was letting each source keep its own table and having later code handle each one. That's quicker for a single source, but every new source then changes the reasoning code, and provenance gets lost in joins.

## What it changes
- Ingestion adapters output exactly these two tables. Nothing downstream opens a raw file.
- Raw downloads land in one folder and are never edited. They are hashed into a manifest at download (R1), and datasets stay out of git: the notebook downloads them.
- `observed_at` is the date the train-on-earlier, test-on-later split runs on (Finance must-have).

## Open, set at scope lock
- The attribute columns of mentions, once the dataset is chosen. Adding a column is fine. Renaming or removing one means updating this note.

Next: [[ADR-002 Separate observed and inferred graphs]]
