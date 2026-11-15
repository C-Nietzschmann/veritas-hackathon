# TENSEGRITY

*This project is a prototype and is not financial advice.*

**Track:** Finance · **Team:** jonas, cristiano, phantodevc (handles: this repo is public for blind judging, so full names are only on the submission form and in the submitted PDF, which has the same text)

## The problem
Before giving a new construction firm trade credit, a builders' merchant checks its directors for past insolvencies, but common names cause false matches and misspellings hide real ones.

## What we built
A merchant enters a company number; TENSEGRITY's machine-learning model matches its directors to those of earlier insolvent companies, with a match score and an evidence graph (solid: on the register; dashed: inferred), showing whom to check before giving credit.

## What we added
Our own idea, with our own Companies House dataset and user (suppliers offering trade credit). Rather than merging director records by name, we score each candidate pair, to test whether this reduces false matches for common surnames while keeping confirmed links.

## How it works
**Data:** 13,761 UK construction companies formed in 2021–22, with directors' histories: training Jan–Sep 2021, validation Oct–Dec 2021, test 2022 (used once). Names were normalised; each company saw only records up to its formation. Failure: insolvent liquidation or administration within 24 months, or a strike-off after filing real accounts. Our first definition counted all strike-offs, but 96% of training companies it marked failed had filed no real accounts.

**Model:** we trained a machine-learning model, a logistic regression, to score candidate pairs on name similarity, birth month and year, postcode district and nationality. It learns from the register's officer ids as labels, never as input, and is fast and interpretable.

## Results
On 6,847 unseen companies from 2022, the baseline (matching by name alone) made 1,537 links to earlier insolvent companies that the register can't confirm (442 for common surnames), precision 0.163, recall 0.980. Our matcher made 534 (112), precision 0.344, recall 0.918, missing 25 of 305 confirmed links against 6 (95% intervals for recall: 88–94% vs 96–99%). Precision is conservative: Companies House sometimes gives one person separate officer records. A blind re-check of 50 validation pairs, picked across groups, agreed with the matcher on all 50, though on evidence similar to its inputs.

**Where it fails, and why we think so:** 3 of 348 linked test companies failed and 62 of 6,499 others, too few to tell either way, and with failure this rare our decision step clears nearly every company. The matcher misses links when birth dates are wrong or missing or surnames change, and often when middle names are dropped (32.3% still linked). On validation, name plus birth month and year does as well (138 vs 130 unconfirmed); the matcher's edge is typos (first-name typo: 81.0% still linked vs 2.6%).

## What we'd do next
We learned that reducing false identity matches doesn't by itself predict failure. Next: make the matcher tolerate wrong or missing birth dates, and add a name-commonness feature.

## Sources
**Data:** [Companies House public data API](https://developer.company-information.service.gov.uk/). **Models:** none pretrained. **AI tools:** [Claude](https://claude.ai/) and [Claude Code](https://claude.com/claude-code) (Anthropic): code, review, first pass on the 50 check pairs, drafting help. Full list: [Credits](https://github.com/C-Nietzschmann/veritas-hackathon/blob/main/vault/Project/Credits.md).

---

## How this page was made (team notes)

About one page, required, in the official template from the Project Briefs. Judges read clarity, honesty and what we added here. Owner: Product and story lead.
Start at feature freeze (Sun 14:00). Draft it ourselves first, then let others and AI tools edit.

Budget: about 450 words, one page. If it doesn't fit, cut words, not font size. No names, no school.

**Fixed by the decision of Sun 15 Nov 11:55** (A strike-off counts only after real accounts). Draft around these points and don't contradict them:
- **"Failed"** means liquidation or administration, or a strike-off after filing real (not dormant) accounts, within 24 months of incorporation. One sentence in How it works.
- **The main result is the matcher:** calibration (#88), the hand-checked pairs (#89), and false matches by name commonness. It leads Results.
- **Where it fails:** on our data an insolvent predecessor did not predict failure, so the decision layer clears nearly every company. Say it plainly. Also say what we tried first (any strike-off counted, which mostly counted companies that never traded) and why we changed it.
- **Numbers** only from [[Evaluation]].



## Before it goes out
- [ ] Every number matches [[Evaluation]]
- [ ] It says what we learned, not only which tools we used
- [ ] Health or finance track: the exact prototype line is under the title
- [ ] It answers the four questions (who, input and output, baseline, failure)
- [ ] Every link opens in a logged-out browser
- [ ] A classmate who doesn't code would understand the first two sections
- [ ] Read aloud once
- [ ] One page when exported to PDF
