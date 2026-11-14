# Hard rules R1-R8

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09, revised 07:55 after the review on card #16
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
TENSEGRITY reconstructs hidden relationships from fragmented evidence without confusing what it infers with what it knows. Every module follows these eight rules. Each rule gets an automated test in `tests/` as soon as the box it guards exists.

| Rule | In practice | Test | From |
|---|---|---|---|
| **R1** Raw evidence is immutable | Each raw response's hash is stored in the `record_ref` of the rows it produced. No separate manifest | Re-hashing a raw response matches its `record_ref` | L0 |
| **R2** Every observed claim has traceable provenance | Every mention and claim row names its source and raw record (ADR-001) | No row has an empty `source` or `record_ref` | L0 |
| **R3** Inferred relationships are never presented as observed facts | Two separate graphs (ADR-002) | Every observed edge points to a claim row, and no inferred link appears in the observed graph | L0 |
| **R4** Uncertainty and unresolved ambiguity survive downstream | Probabilities travel to one decision layer at the end (ADR-004) | Resolution outputs always carry a probability; only the decision layer outputs actions | L0 |
| **R5** Copied or correlated sources are not independent confirmations | Support is counted per `origin`, not per row (ADR-001) | Skipped, with that reason, while we have one source | later |
| **R6** Ambiguous identities are never silently merged | Entity resolution outputs pair probabilities, never merged records (ADR-003) | Two hand-made look-alikes stay two mentions joined by a "same person?" link with its probability | L0 |
| **R7** Inferences are reproducible, challengeable and revisable | Fixed seed, and every inferred link lists what it depends on (ADR-004) | Same input and seed give identical output; changing one match changes only the links that list it | L2, with #32 |
| **R8** Insufficient evidence means abstention, never manufactured certainty | The decision layer has an explicit "not enough evidence" outcome (ADR-004) | A case with no supporting evidence returns NOT ENOUGH EVIDENCE, never yes or no | L0 |

## Why
Our central question is how to reconstruct structures nobody observed directly without mixing up what we infer with what we know. The rules make that checkable, and the tests make the check automatic: CI runs `pytest` on every code pull request.

The alternative was keeping them as guidelines. Under deadline pressure, guidelines without tests are the first thing to go.

## What it changes
- A pull request that breaks a rule's test does not merge.
- The tests run on the tiny world, not the real data, so they are fast and need no download.
- R1 stays in its cheapest form, and R5 waits for a second source. That keeps all eight rules in the pitch without costing build time.
- If a rule blocks something important during the weekend, we change it here, on a call. Never quietly in code.

Next: [[ADR-001 Canonical evidence schema]]
