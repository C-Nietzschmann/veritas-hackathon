# Idea

Filled in together on our kickoff call, Sat 08:00–10:00 CET. Locked at 10:00. Changes after that need a note in `Decisions/`.
Owner after lock: the coordinator.

> **Draft by jonas for the 08:00 call, updated after the review on card #16.** Everything here is a proposal until the call confirms it. Points still to settle are marked **open**.

## Track and challenge
- **Track:** Finance
- **The track's challenge** (from [[Track Briefs]]):

> Help a person or small business make a safer or fairer money decision, and show it beats a simple rule.

- **Starting point:** our own idea
- **The track's must-haves:**
  - [ ] At least one simple baseline, both results reported (we report three)
  - [ ] Precision and recall, not accuracy (company failures are rare)
  - [ ] Train on earlier, test on later
  - [ ] The exact line in the write-up: "This project is a prototype and is not financial advice."

## The problem, in one sentence
A small UK supplier asked to give credit to a young company can't easily see whether the people behind it have a trail of companies that went bust owing money. Checking by hand fails both ways: a common name raises false alarms, and a slightly different spelling hides the real trail.

The organisers' test: "Our project helps **the owner of a small UK supplier** by taking **a customer's company number** and giving back **FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the evidence graph and how sure it is**."

## Our user
The owner of a small UK supplier, for example a builders' merchant, deciding whether to open a 30-day credit account for a company that is a few months old. Today they glance at the Companies House website or pay for a credit check.

A wrong "yes" means an unpaid invoice when the customer goes under and the same people carry on in a new company (a "phoenix"). A wrong "no" turns away an honest customer, often one whose director simply has a common name.

## Our approach
A company number goes in. The model gathers the company's directors from Companies House and works out, with a probability, which earlier companies the same people ran, because a matching name is not proof. From those probabilities it computes the chance that the company has an insolvent predecessor, and from that the chance it fails.

What comes out: FLAG, CLEAR or NOT ENOUGH EVIDENCE for this credit decision, the evidence graph (solid lines are stated in the register, dashed lines are inferred), and the one uncertain match that would change the answer.

Step by step: [[Pipeline]]

## What we add (required)
- **Our own user or setting:** small UK suppliers deciding on trade credit
- **Our own data:** Companies House, not one of the suggested datasets
- **Our own question:** does keeping identity uncertainty, instead of merging by name, cut false flags for people with common names without missing more real phoenix cases?

**What we add:** We test whether uncertainty-aware identity matching cuts false phoenix flags for people with common names, without missing more real ones, on real Companies House data.

## Data
| Dataset | Link | Size | Licence | Why this one |
|---|---|---|---|---|
| Companies House free company data | https://www.gov.uk/guidance/companies-house-data-products | About 5 million live companies, monthly CSV | Open Government Licence (confirm) | Status, incorporation date, sector and address of every live company |
| Companies House public data API | https://developer.company-information.service.gov.uk/ | One company at a time, 600 requests per 5 minutes per key | Open Government Licence (confirm) | Directors, their officer ids and their other companies |
| PSC bulk file (fallback) | https://www.gov.uk/guidance/companies-house-data-products | Bulk JSON of people with significant control | Open Government Licence (confirm) | Person–company links with no rate limit, if the API crawl fails |

Checked: it downloads from a public URL inside a notebook ☐ · it has enough examples ☐ · we're allowed to use it ☐

**30-minute rule** (from the workshops): no usable data within 30 minutes means we change the question.

**Slice (chosen 08:00, see Plan):** construction (SIC 41–43), companies formed in 2021 and 2022. Card #19 counts the positives first: if fewer than about 50 young companies fail within 24 months *and* have a director with an earlier insolvent company, we widen the years.

## Model
- **Baselines (three):** flag nothing; same name means same person (the hard merge); and Companies House officer links only, which is what a careful supplier sees on the website today.
- **First real model:** entity resolution that scores pairs of people (name, birth month and year, postcode, nationality) with a calibrated probability, trained on officer ids as labels and never as a feature. Then P(insolvent predecessor) = 1 − ∏(1 − pᵢ) over the candidate matches, a straight line from that to P(fail), and the cost-based decision layer.
- **The one measured improvement (Sunday):** one identity per director. A director is at most one of their candidate earlier people, which is a closed form, with possible worlds as the check. We measure whether it improves the flags against the formula.
- **If there's time:** what would flip each decision, what-if toggles and cost sliders.

## How we measure
- **Main metric and why:** precision and recall of FLAG on 2022 companies, at the thresholds the stated costs give, next to all three baselines. Failures are rare, so accuracy would say nothing. PR-AUC alongside.
- **Label (chosen):** the company goes into liquidation or administration within 24 months of incorporation.
  - Exactly: a company failed if its first liquidation or administration started on or before the day 24 months after its incorporation (a members' voluntary liquidation, which is a solvent wind-down, does not count), and no insolvency or a later one means it did not fail.
- **Split (chosen):** train on companies formed Jan–Sep 2021, validate on Oct–Dec 2021, test on 2022. Directors' histories are only used up to each company's formation date (as-of rule, ADR-001).
- **Limitation we state:** the 2021 companies' 24-month outcomes run into 2023, past the start of the test year.
- **The three costs (chosen):** a missed case 10, a wrong flag 2, asking 1. That means flag above P(fail) 0.5, clear below 0.1, and NOT ENOUGH EVIDENCE in between. The call can still change them.
- **What score would make this useful to our user:** **open.** Proposal: fewer false flags than the name-match rule at the same recall, with calibrated probabilities.
- **Also:** calibration, false flags by name-commonness group (our main claim), at least five failures with a one-line reason each, and a hand-check of about 50 identity pairs.
- Details: [[Evaluation Protocol]]

## Scope
**MVP, must exist by Sat 21:00 (P0)**
- L0, target 13:00: the tiny world runs through every box, the rule tests pass, the three baselines give their first numbers
- L1, target 19:00: the real slice runs through every box with the formula, plus the decision layer, interface v1 and masking. False flags by name commonness and five failures are measured

**Makes it better (P1)**
- One identity per director, as Sunday's measured improvement
- What would flip each decision
- What-if toggles and cost sliders
- Static figures for the notebook

**Not doing** (listed as next steps in the write-up)
- Robustness tests against copied and corrupted evidence
- The one detail to ask (value of information)
- A public demo link. It would put real directors' data online
- Ingesting any file type, documents or other languages. That's the long-term TENSEGRITY vision, not this weekend
- A better pairwise matcher for its own sake. Our claim is about decisions, calibration and fairness

## The demo, in one sentence
We type in the number of a company a few months old. The graph builds with solid register facts and dashed inferred links to its directors' earlier companies that went bust, with names masked. It answers FLAG, CLEAR or NOT ENOUGH EVIDENCE and names the one uncertain match behind the answer. We reject that match and the answer changes live.

## The four questions
- **Who is it for?** The owner of a small UK supplier deciding whether to give credit to a young company.
- **What goes in, what comes out?** A company number goes in. Out comes FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the evidence graph and the match that would change it.
- **Which baseline must it beat?** Three: flag nothing, same name means same person, and Companies House's own officer links.
- **Where do we expect it to fail?** Very common names with no birth date match, a phoenix run through a new front person, failures the register doesn't show yet, and companies outside our slice.

## Risks
| What could go wrong | How we'd notice | Plan B |
|---|---|---|
| Too few positives: young companies that fail *and* have an insolvent predecessor are rare | #19 counts fewer than about 50 | Widen the years or the sector |
| Directors only come one company at a time through the API, at 600 requests per 5 minutes | The crawl isn't running by 10:30 | PSC bulk file: person–company links with no rate limit |
| The free bulk file lists live companies only, so companies that already failed and were dissolved are missing (survivorship bias) | Few dissolved companies in the sample | Draw the sample through the API and check in #19 that dissolved companies come back. If not, rethink the label |
| Leakage: a crawl made today shows what happened after the decision date | Scores look too good | As-of rule: a decision about date t only uses evidence dated before t (ADR-001) |
| Real people's names, birth dates and postcodes in public outputs | Before every push of the notebook | Mask them in every output: notebook, figures, interface, write-up and video. No raw data in git |
| Officer-id labels copy Companies House's own linking | The hand-check of about 50 pairs | Say so, and prove value against the officer-links baseline |
| The dataset is too messy or too small | The data test | A smaller, cleaner slice |
| Training is too slow on our laptops | A run takes over 20 minutes | A smaller slice |
| The model is no better than the baselines | Validation scores | Report it honestly. The fairness and calibration results can still stand |
