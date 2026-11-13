# Evaluation Protocol

"Testing and honesty" is 15 points in Round 1, and "how do you know it works?" is the most likely question in the finals. This is how we make sure we have a real answer. Owner: Data and evaluation lead.

## In order
1. **Choose one main metric** before training anything and write in Idea why it fits the problem. Accuracy is misleading when classes are unbalanced. Ask what a mistake costs the user.
2. **Split the data once.** Train, validation, test, with a fixed seed. Write the split in [[Evaluation]]. The test set is not looked at again until the end.
3. **Build a baseline first.** The dumbest thing that produces an answer: always predict the most common class, predict the mean, or a simple linear model. Its score is the bar.
4. **Log every experiment** as one row in the results table in [[Evaluation]]: what changed, validation score, notebook and commit.
5. **Tune on validation only.** Choosing models or settings by test score makes the test score a lie.
6. **Test once, at the end.** After feature freeze, run the chosen model on the test set. That number goes in the write-up, whatever it is.
7. **Look at the failures.** Take 10 to 20 examples the model got wrong and read them. Group them. This becomes the "where it fails" section.

## Checks that catch the classic mistakes
- **Leakage:** is there a feature that secretly contains the answer, or do near-identical rows sit in both train and test? A score that looks too good usually is.
- **Same preprocessing:** scalers and encoders are fitted on train only, then applied to validation and test.
- **Repeatability:** same seed, same result. If not, find out why before trusting any comparison.
- **Size:** with a small test set, a 1 to 2 point difference is noise. Say so.

## For generative or LLM projects
When there is no single correct label:
- Write 20 to 30 test inputs **before** building, with what a good answer must contain.
- Score each output against a short checklist (correct? complete? safe?) and report how many pass.
- Compare against a baseline: the plain model without our system.
- Keep the test inputs and outputs in the repo so the result can be checked.

## Honesty
What we write is what we measured.
- Report the baseline next to our result, always.
- Report the failures and limits: what data it wasn't tested on, who it might not work for.
- A modest result that is explained well scores higher than an impressive one nobody can verify.
- If something doesn't work by the deadline, say so in the write-up and say what we'd try next.
