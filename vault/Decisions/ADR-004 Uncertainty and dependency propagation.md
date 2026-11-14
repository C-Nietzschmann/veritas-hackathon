# ADR-004 Uncertainty and dependency propagation

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09, revised 07:55 after the review on card #16
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
Uncertainty travels as probabilities from entity resolution to **one decision layer at the end** (R4). For the MVP, the company's chance of an insolvent predecessor is 1 − ∏(1 − pᵢ) over every candidate match. A straight line turns that into the chance the company fails. Only the decision layer turns the chance of failure into an action, and it abstains when no action is worth its expected cost (R8). The one-identity rule is Sunday's one measured improvement.

## Why
A link that rests on a 60% identity match can't honestly be more certain than that match. Rounding to yes or no at a module boundary is where pipelines silently throw uncertainty away.

The formula is exact when the matches are independent, and it fits on one slide, so it's easy to defend live. Its known flaw is that it ignores that one director is only one person, and that flaw is exactly what Sunday fixes.

The alternative was thresholding at every stage. That's the hard-merge pipeline we're trying to beat.

## What it changes
- **Calibration first.** A model output is called a probability only after a calibration check on validation data (reliability plot and Brier score). Until then it's labelled "score", in the interface too.
- **From predecessor to failure.** Fit a straight line of failure rate against P(predecessor) on the 2021 training companies. Its two ends are the failure rates without and with a predecessor. The costs are about failure (the unpaid invoice), so the decision runs on P(fail), never on P(predecessor). The fit is linear, so it stays exact when we later average over possible worlds.
- **The decision layer** uses three costs the user states: a missed case, a wrong flag, and asking or checking. With a calibrated P(fail), it flags if `p ≥ 1 − cost_ask / cost_wrong_flag`, clears if `p ≤ cost_ask / cost_miss`, and abstains otherwise (Chow's reject rule, 1970). Proposal: missed case 10, wrong flag 2, asking 1, which gives flag above 0.5, clear below 0.1, and NOT ENOUGH EVIDENCE in between. The costs are never tuned on test data.
- **What would flip it (P1):** drop or confirm each match in turn and recompute. The match that flips the decision is shown with it.
- **Dependencies:** every inferred link stores `depends_on`, the ids of the matches and claims it rests on.

## Sunday's improvement: one identity per director
- A director is at most one of their candidate earlier people. Take the independent matches and condition them on "at most one is true". Candidate k then gets qₖ = oddsₖ / (1 + Σ odds), and "nobody we know" gets 1 / (1 + Σ odds), where oddsₖ = pₖ / (1 − pₖ). That's closed form.
- Candidates are earlier people (officer ids), not single records, so two records of one person don't count twice.
- **Possible worlds** samples identities from these probabilities, with a fixed seed and all random draws made once up front (R7). Use it where the rules interact (two directors pointing at the same earlier person, or chains like A=B=C), and as a check: where nothing interacts, the samples must reproduce the closed form. With 400 worlds an estimated probability lands within about ±0.05 of the exact value (95%).
- Measured against the MVP formula on validation: do the flags change, and do they get better?
- Sampling pairs independently would return exactly the MVP formula. The one-identity rule is the whole point.
- **Out of scope:** a full probabilistic graphical model or Bayesian entity resolution (Steorts et al.).

Next: [[ADR-005 Model and adapter independence]]
