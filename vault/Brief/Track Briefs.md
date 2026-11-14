# Track Briefs

Summary of the official Project Briefs (PDF from the starter-kit email, 22 pages). Read the PDF itself for the full step-by-step instructions of a project. This note is for choosing.

Up: [[Brief]]

## How to choose
- Pick **one track** and build **one project** for it. The track is chosen on the submission form.
- Each track has suggested projects with a level. Following one gets a working baseline, but **adding something of our own is required** to score well: our own **user or setting**, our own **data**, or our own **question** (when it fails, who it fails for, whether it holds up somewhere new). Judges compare teams that started from the same suggested project and score what each added.
- Or build **our own idea**, as long as it meets the track's challenge. It must stay inside one of the four tracks.
- There is no easier track. Pick the problem we care most about.

| Level | For a team that… | Recommended tools |
|---|---|---|
| Beginner | has never coded or knows only basics | Teachable Machine, or the starter notebooks (we run them in local Jupyter) |
| Intermediate | can write some Python | Jupyter, pandas, scikit-learn, Gradio |
| Advanced | has trained models before | PyTorch or Hugging Face, a GPU if one is available (we have none: keep models small) |

---

## AI + Health
**Challenge:** help one specific person catch a health problem sooner, or manage one better.

**Must have**
- Name the user (doctor, nurse, patient, parent, health worker) and how they use it
- Report **missed cases (false negatives) and false alarms (false positives) separately**, not only accuracy
- The exact line in the write-up: *"This project is a prototype and is not medical advice."*
- Public datasets only. No real patient records, even through family, school or work

| Suggested project | Level | Data | Baseline to beat | Report |
|---|---|---|---|---|
| Pneumonia screening from chest X-rays | Beginner | PneumoniaMNIST or Kaggle Chest X-Ray | "pneumonia" for every image (about 3:1 in training) | Pneumonia recall, number of false alarms |
| Heart disease risk from checkup data | Intermediate | UCI Heart Disease, Cleveland (about 300 patients) | Most common class | Accuracy, recall, most important measurements |
| Country-level health risk | Advanced | WHO GHO, Our World in Data | This year = last year. Split by year, never at random | Error vs baseline, top 10 countries at risk |

**Own ideas they mention:** sign language from webcam, mood journal with an emotion classifier, reading medicine labels aloud.
**Judges look extra at:** a clear user, honest missed cases and false alarms, whether it works equally across age, sex or skin tone.

## AI + Finance
**Challenge:** help a person or small business make a safer or fairer money decision, and show it beats a simple rule.

**Must have**
- At least one simple baseline, both results reported
- A measure that fits: for rare events like fraud, **precision and recall**, not accuracy
- Data with dates: **train on earlier, test on later**
- The exact line: *"This project is a prototype and is not financial advice."*

| Suggested project | Level | Data | Baseline to beat | Report |
|---|---|---|---|---|
| Scam text filter | Beginner | SMS Spam Collection (5,574 messages, 13% spam) | "Not spam" for all (87% accurate, catches nothing) | Spam precision and recall, five messages it gets wrong |
| Card fraud detection | Intermediate | Kaggle Credit Card Fraud (284,807, 492 fraud) | "Not fraud" for all (99.8% accurate, useless) | Precision, recall, PR-AUC |
| Fairness audit of a loan model | Intermediate | Statlog German Credit (1,000 applicants) | Approve everyone | Accuracy, approval rate per group, the gap |
| News headlines and the stock market | Advanced | Daily News for Stock Market Prediction | Always "up", and "same as yesterday". Split by date | Accuracy for the model and both baselines, honestly even if "not really" |

**Own ideas they mention:** budgeting assistant for teens with a first debit card, a city inflation tracker, bank fees explained in plain language.
**Judges look extra at:** the right measure, a fair baseline comparison, whether a real person could trust it, checking for unfair treatment of a group.
**Worked example:** the organisers' sample submission "ScamCheck" (scam filter for grandparents) is this track. It shows the detail they expect: one user, a baseline, 40 modern test messages the team wrote, and honest misses.

## AI + Climate
**Challenge:** help a community, city or energy system measure, predict or reduce its climate impact.

**Must have**
- **One location** or region
- Forecasts: **train on earlier dates, test on later**. Never shuffle days
- Compare with the **persistence baseline**: "tomorrow is the same as today"
- Say what decision the prediction supports, and who makes it

| Suggested project | Level | Data | Baseline to beat | Report |
|---|---|---|---|---|
| Next-day solar energy forecast | Beginner | NASA POWER (no code to download), Open-Meteo | Tomorrow = today (hard to beat) | Mean absolute error, baseline vs model |
| Next-day air quality (PM2.5) forecast | Intermediate | OpenAQ (free key), Open-Meteo weather | Tomorrow = today | MAE on the most recent months |
| Land-use mapping from satellite images | Advanced | EuroSAT (27,000 tiles, 10 classes) | Most common class | Accuracy per class, confusion matrix |

**Own ideas they mention:** biggest emitters with Climate TRACE, a building's energy use, a meal's carbon footprint from a photo, which streets flood after heavy rain.
**Judges look extra at:** a fair comparison with a simple forecast, a clear link to a decision, a test period the model never saw. A small project tied to a real place beats "the whole planet".

## AI + Languages
**Challenge:** help people understand each other, learn a language or be understood, especially in a language technology serves poorly. A teammate who speaks such a language is an advantage.

**Must have**
- Results **for each language or accent** separately, not only an average
- Real examples: the model's output **next to the correct output**
- Public data or our own voice and writing. No one else's voice or messages without permission

| Suggested project | Level | Data | Baseline to beat | Report |
|---|---|---|---|---|
| Language identification | Beginner | Tatoeba, 5 to 10 languages | The `langdetect` library | Accuracy per language, confusion matrix |
| Translation quality test | Intermediate | NLLB-200 and FLORES+ (Hugging Face account) | A widely spoken language vs a less served one | chrF per language, the five worst translations |
| Speech recognition across accents | Advanced | Common Voice or FLEURS, Whisper-small | Per-group comparison | Word error rate per group |

**Own ideas they mention:** rewriting complicated forms in plain language, reading and translating street signs, a conversation partner for learners. On top of an LLM API, judges look at what we add: our data, testing and user.
**Judges look extra at:** side-by-side examples, results per language or accent, a check by a real speaker.
