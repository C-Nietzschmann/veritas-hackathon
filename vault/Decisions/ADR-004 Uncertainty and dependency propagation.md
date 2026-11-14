# ADR-004 Uncertainty and dependency propagation

Up: [[Decisions]]

- **Date:** 2026-11-14 07:09
- **Decided by:** proposed by jonas. Confirm or change on the kickoff call (task #16)
- **Status:** proposed

## Decision
Uncertainty travels as probabilities from entity resolution to **one decision layer at the end**. Every inferred link lists the matches and claims it depends on. Only the decision layer turns probabilities into an action, and it abstains when no action is worth its expected cost (R4, R7, R8).

## Why
A link that rests on a 60% identity match can't honestly be more certain than that match. If the match is revised, the link has to be revised with it. Rounding to yes or no at a module boundary is where pipelines silently throw uncertainty away.

The alternative was thresholding at every stage. That's simpler, but it is the hard-merge pipeline we're trying to beat.

## What it changes
- **Calibration first.** A model output is called a probability only after a calibration check on validation data (reliability plot and Brier score). Until then it's labelled "score", in the interface too.
- **Dependencies:** every inferred link stores `depends_on`, the ids of the matches and claims it rests on.
- **One random draw:** all random numbers come from the seed once, up front. Changing one input then changes only what depends on it (R7).
- **The decision layer** uses three costs the user states: a wrong flag, a missed case, and asking or checking. With a calibrated `p`, it flags if `p ≥ 1 − cost_ask / cost_wrong_flag`, clears if `p ≤ cost_ask / cost_miss`, and abstains otherwise (Chow's reject rule, 1970). The costs are never tuned on test data.
- **If time:** when it abstains, name the one missing detail whose answer would lower the expected cost the most (value of information).

## Open, decide on the call: how uncertainty is propagated
- **(a) Possible worlds (proposed):** draw every uncertain match as on or off according to its probability, rebuild the graph, run inference, and repeat N times. A link's probability is its average over the worlds; for a yes-or-no rule, that's the share of worlds where it appears. With N = 400 this lands within about ±0.05 of the exact value (95%). Comparing worlds with and without one match shows which uncertain assumption would overturn a link. Limitation: drawing pairs independently ignores that A=B and B=C imply A=C, so it can over-chain. We report this. Bayesian entity resolution (Steorts et al.) is the principled fix and is out of scope.
- **(b) Multiply probabilities along a path:** fast, but wrong whenever two paths share a match, because it assumes they're independent.
- **(c) A full probabilistic graphical model:** the most principled option, but too heavy to build and explain in 48 hours.

Next: [[ADR-005 Model and adapter independence]]
