# ADR-003 Probabilistic entity resolution

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09, reviewed 07:35
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
Entity resolution never merges records. For each candidate pair of mentions it outputs the probability that both describe the same real-world entity, plus the features behind that probability. Every candidate pair stays in the output, however uncertain it is (R6).

## Why
A wrong merge invents relationships that don't exist, which are the false relationships our research question counts. A missed merge hides real ones. Keeping the probability lets ADR-004 carry the doubt to the end instead of guessing early.

The alternative was a hard merge: same entity whenever name similarity passes one threshold. That's our **baseline**, not our method. The research question is whether keeping the uncertainty produces fewer false relationships than the hard merge while still recovering the links.

## What it changes
- **Output:** one table of candidate pairs with mention a, mention b, `p`, and the features that drove `p`.
- **Blocking**, the cheap filter that proposes candidate pairs, is written down and its recall is measured on validation. A true match it never proposes can never be found.
- The hard-merge baseline is built from the same candidate pairs, so both run on identical input (ADR-005).
- `p` is only called a probability once it has passed the calibration check (ADR-004).
- **Companies House:** the register's own officer id already links some appointments of one person, but not all of them. We use it as a strong feature and as weak labels, never as the truth. Name, birth month and year, and postcode are the other core features.

## Open, decide at scope lock (once we know if the data has labelled pairs)
- **(a) Fellegi–Sunter weights:** the classic record-linkage model. Every field gets an agree or disagree weight, learned from labels or without them. Fully explainable, and it works without labels.
- **(b) A small trained classifier** (logistic regression) on pair features, calibrated on validation. Explainable, and it calibrates well. Needs labelled pairs; officer ids give weak ones.
- **(c) An LLM judging pairs:** strong, but slow, costly and hard to calibrate. Better as a second opinion on the unsure pairs only.
- Default if nobody objects: (b) with labels, (a) without.

Next: [[ADR-004 Uncertainty and dependency propagation]]
