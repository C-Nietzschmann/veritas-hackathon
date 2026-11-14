# Hard rules R1-R8

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
TENSEGRITY reconstructs hidden relationships from fragmented evidence without confusing what it infers with what it knows. Every module follows these eight rules, and each rule gets an automated test in `tests/`.

| Rule | In practice | Test |
|---|---|---|
| **R1** Raw evidence is immutable | Raw downloads are hashed into a manifest at download and never edited | Re-hashing the raw files matches the manifest |
| **R2** Every observed claim has traceable provenance | Every mention and claim row names its source and raw record (ADR-001) | No row has an empty `source` or `record_ref` |
| **R3** Inferred relationships are never presented as observed facts | Two separate graphs (ADR-002) | Every observed edge points to a claim row, and no inferred link appears in the observed graph |
| **R4** Uncertainty and unresolved ambiguity survive downstream | Probabilities travel to one decision layer at the end (ADR-004) | Resolution and inference outputs always carry a probability column; only the decision layer outputs actions |
| **R5** Copied or correlated sources are not independent confirmations | Support is counted per `origin`, not per row (ADR-001) | Duplicating a source's rows under a new source name with the same origin changes no probability |
| **R6** Ambiguous identities are never silently merged | Entity resolution outputs pair probabilities, never merged records (ADR-003) | Two hand-made look-alikes stay two mentions joined by a "same entity?" link with its probability |
| **R7** Inferences are reproducible, challengeable and revisable | Fixed seed, and every inferred link lists what it depends on (ADR-004) | Same input and seed give identical output; changing one match changes only the links that list it |
| **R8** Insufficient evidence means abstention, never manufactured certainty | The decision layer has an explicit "not enough evidence" outcome (ADR-004) | A case with no supporting evidence returns "not enough evidence", never yes or no |

## Why
Our central question is how to reconstruct structures nobody observed directly without mixing up what we infer with what we know. The rules make that checkable, and the tests make the check automatic: CI runs `pytest` on every code pull request.

The alternative was keeping them as guidelines. Under deadline pressure, guidelines without tests are the first thing to go.

## What it changes
- A pull request that breaks a rule's test does not merge.
- The tests run on a tiny hand-made example, not the real data, so they are fast and need no download.
- If a rule blocks something important during the weekend, we change it here, on a call. Never quietly in code.

Next: [[ADR-001 Canonical evidence schema]]
