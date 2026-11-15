# Write-up

About one page, required, in the official template from the Project Briefs. Judges read clarity, honesty and what we added here. Owner: Product and story lead.
Start at feature freeze (Sun 14:00). Draft it ourselves first, then let others and AI tools edit.

Budget: about 450 words, one page. If it doesn't fit, cut words, not font size. No names, no school.

**Fixed by the decision of Sun 15 Nov 11:55** (A strike-off counts only after real accounts). Draft around these points and don't contradict them:
- **"Failed"** means liquidation or administration, or a strike-off after filing real (not dormant) accounts, within 24 months of incorporation. One sentence in How it works.
- **The main result is the matcher:** calibration (#88), the hand-checked pairs (#89), and false matches by name commonness. It leads Results.
- **Where it fails:** on our data an insolvent predecessor did not predict failure, so the decision layer clears nearly every company. Say it plainly. Also say what we tried first (any strike-off counted, which mostly counted companies that never traded) and why we changed it.
- **Numbers** only from [[Evaluation]].

---

**Project name** · **Track** · **Team** (the official template asks for names. Round 1 is blind and the repo goes public, so the README carries only the team name; names go on the form and in the uploaded PDF if we upload one)

Health or finance: the line *"This project is a prototype and is not medical advice."* / *"…not financial advice."* goes right under the title.

## The problem (2–3 sentences)
Who has this problem, and why does it matter? One concrete situation.

## What we built (about 70 words)
The input, the output, and how someone uses it.

## What we added (about 60 words)
The suggested project we started from and what we added or changed (our own user, data or question). Or: "Our own idea".

## How it works (about 120 words)
**Data:** which dataset, its size, how we cleaned it. **Model:** what we chose and why. Mention what we tried that didn't work if it explains a choice.

## Results (about 130 words)
Baseline X vs our model Y on the held-out test set, on the main metric. One sentence on what that means for the user. Where it fails and why, with a concrete case. Results by group, and whether they are uneven. One small table or chart if it fits.

## What we'd do next (about 50 words)
The first thing we'd do with more time, and what we learned building it.

## Sources (about 40 words)
Datasets, models, tutorials and AI tools, each with a link. From Credits.

---

## Before it goes out
- [ ] Every number matches [[Evaluation]]
- [ ] It says what we learned, not only which tools we used
- [ ] Health or finance track: the exact prototype line is under the title
- [ ] It answers the four questions (who, input and output, baseline, failure)
- [ ] Every link opens in a logged-out browser
- [ ] A classmate who doesn't code would understand the first two sections
- [ ] Read aloud once
- [ ] One page when exported to PDF
