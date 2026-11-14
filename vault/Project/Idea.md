# Idea

Filled in together on our kickoff call, Sat 08:00–10:00 CET. Locked at 10:00. Changes after that need a note in `Decisions/`.
Owner after lock: the coordinator.

> **Draft by jonas for the 08:00 call.** Everything here is a proposal until the call confirms it. Points still to settle are marked **open**.

## Track and challenge
- **Track:** Finance
- **The track's challenge** (from [[Track Briefs]]):

> Help a person or small business make a safer or fairer money decision, and show it beats a simple rule.

- **Starting point:** our own idea
- **The track's must-haves:**
  - [ ] At least one simple baseline, both results reported
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
A company number goes in. The model gathers the company's directors and owners from Companies House and works out, with a probability, which other companies the same people ran, because a matching name is not proof. It reruns that reasoning across 400 possible versions of who is who, so every inferred link carries an honest probability.

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
| Companies House public data API | https://developer.company-information.service.gov.uk/ | One company at a time, 600 requests per 5 minutes per key | Open Government Licence (confirm) | Directors, owners and their other companies |
| PSC bulk file (fallback) | https://www.gov.uk/guidance/companies-house-data-products | Bulk JSON of people with significant control | Open Government Licence (confirm) | Person–company links with no rate limit, if the API crawl fails |

Checked: it downloads from a public URL inside a notebook ☐ · it has enough examples ☐ · we're allowed to use it ☐

**30-minute rule** (from the workshops): no usable data within 30 minutes means we change the question.

**Open:** the slice (one sector, one region, incorporation years) and the sample size, set in the data test.

## Model
- **Baseline:** what a person would do by hand. Treat the same name as the same person, and flag the company if any of its directors matches a director of a company that went insolvent in the last three years.
- **First real model:** entity resolution that scores pairs of people (name, birth month and year, postcode, the register's own officer id) with a calibrated probability, then possible worlds, a calibrated logistic regression for "fails within the label window", and the cost-based decision layer.
- **If there's time:** what would flip each link, what-if toggles and cost sliders, the one detail to ask.

## How we measure
- **Main metric and why:** precision and recall of FLAG on companies formed after the training period, at the thresholds the stated costs give. Failures are rare, so accuracy would say nothing. PR-AUC alongside.
- **What score would make this useful to our user:** **open.** Proposal: fewer false flags than the name-match rule at the same recall, with calibrated probabilities.
- **Also:** false identity links compared with the hard merge, calibration, results by name-commonness group, and at least five failures read and explained.
- **Label:** **open.** Proposal: the company goes into liquidation or administration within 24 months of incorporation.
- **The three costs** for the decision layer (a wrong flag, a missed case, asking): **open**, agreed on the call.
- Details: [[Evaluation Protocol]]

## Scope
**MVP, must exist by Sat 21:00 (P0)**
- L0, target 13:00: the tiny world runs through every box, the rule tests pass, the baseline gives its first number
- L1, target 19:00: the real slice runs through every box, interface v1, a decision for any company number in the slice

**Makes it better (P1)**
- What would flip each inferred link
- What-if toggles and cost sliders
- False flags by name commonness, a failure gallery, robustness to copied and corrupted evidence

**Stretch (P2)**
- The one detail to ask (value of information)
- A public demo link

**Not doing**
- Ingesting any file type, documents or other languages. That's the long-term TENSEGRITY vision, not this weekend
- Other countries' registers
- A better pairwise matcher for its own sake. Our claim is about decisions, calibration and fairness

## The demo, in one sentence
We type in the number of a company a few months old. The graph builds with solid register facts and dashed inferred links to its directors' earlier companies that went bust. It answers FLAG, CLEAR or NOT ENOUGH EVIDENCE and names the one uncertain match behind the answer. We reject that match and the answer changes live.

## The four questions
- **Who is it for?** The owner of a small UK supplier deciding whether to give credit to a young company.
- **What goes in, what comes out?** A company number goes in. Out comes FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the evidence graph and the match that would change it.
- **Which baseline must it beat?** The rule "same name means same person", flagging any match with a director of a recently insolvent company.
- **Where do we expect it to fail?** Very common names with no birth date match, a phoenix run through a new front person, failures the register doesn't show yet, and companies outside our slice.

## Risks
| What could go wrong | How we'd notice | Plan B |
|---|---|---|
| Directors only come one company at a time through the API, at 600 requests per 5 minutes | The crawl isn't running by 10:30 | PSC bulk file: person–company links with no rate limit |
| The free bulk file lists live companies only, so companies that already failed and were dissolved are missing (survivorship bias) | Few dissolved companies in the sample | Draw the sample through the API and check in the data test that dissolved companies come back. If not, rethink the label |
| Leakage: a crawl made today shows what happened after the decision date | Scores look too good | As-of rule: a decision about date t only uses evidence dated before t (ADR-001) |
| Real people's names in a public repo and demo | Before every push | Mask names in the interface, write-up and video. No raw data in git |
| The dataset is too messy or too small | The data test | A smaller, cleaner slice |
| Training is too slow on our laptops | A run takes over 20 minutes | Sample per query, smaller slice |
| The model is no better than the baseline | Validation scores | Report it honestly. The fairness and calibration results can still stand |
