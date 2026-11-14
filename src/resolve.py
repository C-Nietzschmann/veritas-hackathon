"""Entity resolution (cards #30, #31): which person records describe the same person?

This box never merges records (R6, ADR-003). It proposes candidate pairs, and later
gives each pair a probability. The officer id is the label, never a feature.

30.1 Blocking. Comparing every person record with every other is too many pairs, so a
cheap rule proposes the ones worth comparing. The rule, in one sentence:

    Two person records are a candidate pair when they have the same surname and first
    initial, or the same birth month and year and a similar surname.

Blocking decides nothing. A look-alike with the same name is proposed too: telling the
two apart is the matcher's job (#31). But a true match that blocking never proposes can
never be found, so its recall is measured (30.3).

30.2 Pair features. Each candidate pair gets the numbers the matcher learns from: how
similar the names are, and whether birth month and year, postcode district and
nationality agree. A missing value is marked as missing, not counted as a difference.

30.3 Blocking recall. The share of the register's own links that blocking proposed.

31.1 Labelled pairs. The register's officer id gives the examples to learn from: the same
id means the same person. It is wrong where the register split one person across two ids.

31.2 The matcher. A logistic regression turns a pair's features into p, a number from 0 to
1. It is only called a probability once the calibration check passes (31.3, ADR-004).
"""

import re
from difflib import SequenceMatcher

import pandas as pd
from sklearn.linear_model import LogisticRegression

from src import evidence as ev

# Two surnames are "similar" from this SequenceMatcher ratio up. "harrow" and "harow"
# give 0.91, "smith" and "smyth" 0.8, "smith" and "jones" 0.2.
# ponytail: a guess, not tuned. Loosen it if the recall in 30.3 is under about 90%.
SIMILAR_SURNAME = 0.8

# Words that are not part of a name written "Mr Daniel Harrow".
TITLES = {"mr", "mrs", "ms", "miss", "mx", "dr", "sir", "dame", "lord", "lady", "prof", "rev"}


def clean(text):
    """Lower case, and anything that isn't a letter or digit becomes a space."""
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def name_parts(name):
    """(surname, first initial) of a name, for example ("harrow", "d").

    Reads both ways a name is written:
    - the register's "HARROW, Daniel James": the surname is before the first comma,
      the forenames after it. Anything after a second comma (a title) is ignored.
    - "Mr Daniel Harrow": titles are dropped, the last word is the surname.
    A name with no forename gives an empty initial. No name gives ("", "").
    """
    if not isinstance(name, str):
        return "", ""
    if "," in name:
        pieces = name.split(",")
        surname, forenames = pieces[0], pieces[1].split()
    else:
        words = [word for word in name.split() if clean(word) not in TITLES]
        surname, forenames = (words[-1], words[:-1]) if words else ("", [])
    forenames = [word for word in forenames if clean(word) not in TITLES]   # "SMITH, Mr John"
    initial = clean(forenames[0])[:1] if forenames else ""
    return clean(surname), initial


def candidate_pairs(mentions):
    """30.1: the pairs of person mentions worth comparing, as a pairs table with p empty.

    Each pair appears once, with a < b. A person with no surname is in no pair.
    """
    ev.check_columns(mentions, "mentions")
    people = mentions[mentions["kind"] == "person"]
    parts = people["name"].map(name_parts)
    table = pd.DataFrame({
        "id": people["mention_id"].to_numpy(),
        "surname": [surname for surname, _ in parts],
        "initial": [initial for _, initial in parts],
        # as numbers, so a year written 1979 and one written "1979" still meet
        "birth_year": pd.to_numeric(people["birth_year"], errors="coerce").to_numpy(),
        "birth_month": pd.to_numeric(people["birth_month"], errors="coerce").to_numpy(),
    })
    table = table[table["surname"] != ""]

    by_name = sharing(table, ["surname", "initial"])
    by_birth = sharing(table, ["birth_year", "birth_month"])
    similar = [SequenceMatcher(None, x, y).ratio() >= SIMILAR_SURNAME
               for x, y in zip(by_birth["surname_x"], by_birth["surname_y"])]

    both = pd.concat([by_name, by_birth[similar]])[["id_x", "id_y"]].drop_duplicates()
    both = both.sort_values(["id_x", "id_y"])   # the same order every run (R7)
    pairs = pd.DataFrame({"a": both["id_x"].to_numpy(), "b": both["id_y"].to_numpy(), "p": None,
                          "features": None, "method": "candidates", "label": None},
                         columns=ev.PAIR_COLS)
    ev.check_columns(pairs, "pairs")
    return pairs


def sharing(table, keys):
    """Every two rows of `table` with the same values in `keys`. An empty key never pairs."""
    filled = table
    for key in keys:
        filled = filled[~ev.is_blank(filled[key])]
    both = filled.merge(filled, on=keys)
    return both[both["id_x"] < both["id_y"]]   # each pair once, and never a row with itself


# --- 30.2 Pair features ---------------------------------------------------------------

# What the matcher (#31) learns from. The officer id is not here and never will be:
# it is the label, and as a feature it would give away the answer (ADR-003).
FEATURE_COLS = [
    "name_similarity", "name_missing",
    "birth_same", "birth_missing",
    "postcode_same", "postcode_missing",
    "nationality_same", "nationality_missing",
]


def comparable_name(name):
    """A name with its words cleaned and sorted, titles dropped, so that
    "HARROW, Daniel" and "Mr Daniel Harrow" both give "daniel harrow". No name gives ""."""
    if not isinstance(name, str):
        return ""
    return " ".join(sorted(word for word in clean(name).split() if word not in TITLES))


def district(postcode):
    """The district of a postcode: "ZZ1 1AA" and "ZZ11AA" both give "ZZ1". No postcode gives ""."""
    if not isinstance(postcode, str) or not postcode.strip():
        return ""
    postcode = postcode.strip().upper()
    if " " in postcode:
        return postcode.split()[0]
    if len(postcode) <= 4:
        return postcode    # only the district was written
    return postcode[:-3]   # written without the space: the last part is always three characters


def pair_features(pairs, mentions):
    """30.2: one row of numbers per pair, in the same order as `pairs`, with the columns FEATURE_COLS.

    For each field, two columns:
    - name_similarity is 0 to 1 (1 = the same words); the other three "_same" columns are 1 or 0.
    - "_missing" is 1 when either record has no value. Then the first column is 0, and the
      matcher can tell "we don't know" from "they differ".
    Birth is the month and year together. Postcode is the district only.
    """
    ev.check_columns(pairs, "pairs")
    ev.check_columns(mentions, "mentions")
    people = mentions.set_index("mention_id")

    # Each field as text, with "" for a missing value.
    year = pd.to_numeric(people["birth_year"], errors="coerce").astype("Int64").astype("string")
    month = pd.to_numeric(people["birth_month"], errors="coerce").astype("Int64").astype("string")
    values = pd.DataFrame({
        "name": people["name"].map(comparable_name),
        "birth": (year + "-" + month).fillna(""),   # a missing year or month makes the whole text missing
        "postcode": people["postcode"].map(district),
        "nationality": people["nationality"].map(lambda value: clean(value) if isinstance(value, str) else ""),
    })
    left = values.loc[pairs["a"]].reset_index(drop=True)
    right = values.loc[pairs["b"]].reset_index(drop=True)

    features = pd.DataFrame(index=pairs.index)
    for field in values.columns:
        missing = ((left[field] == "") | (right[field] == "")).to_numpy()
        if field == "name":
            column = "name_similarity"
            same = [SequenceMatcher(None, x, y).ratio() for x, y in zip(left[field], right[field])]
        else:
            column = f"{field}_same"
            same = (left[field] == right[field]).to_numpy()
        features[column] = pd.Series(same, dtype=float).where(~missing, 0.0).to_numpy()
        features[f"{field}_missing"] = missing.astype(float)
    return features[FEATURE_COLS]


# --- 30.3 Blocking recall -------------------------------------------------------------

def blocking_recall(pairs, mentions):
    """30.3: of the pairs the register itself links (same officer id), how many did blocking propose?

    Returns a dict: true_pairs, kept, and recall = kept / true_pairs (None when there are no
    true pairs). A true pair that blocking never proposes can never be matched (ADR-003).
    It can't see the people the register split across two officer ids: those have no label.
    """
    true_pairs = officer_pairs(mentions)
    proposed = {tuple(sorted(pair)) for pair in zip(pairs["a"], pairs["b"])}   # (a, b) or (b, a): one pair
    kept = len(true_pairs & proposed)
    return dict(true_pairs=len(true_pairs), kept=kept,
                recall=kept / len(true_pairs) if true_pairs else None)


def officer_pairs(mentions):
    """Every two person mentions with the same officer id, as a set of (a, b) with a < b."""
    people = mentions[mentions["kind"] == "person"]
    linked = sharing(pd.DataFrame({"id": people["mention_id"].to_numpy(),
                                   "officer_id": people["officer_id"].to_numpy()}), ["officer_id"])
    return set(zip(linked["id_x"], linked["id_y"]))


# --- 31.1 Labelled pairs --------------------------------------------------------------

def labelled_pairs(mentions):
    """31.1: the pairs the matcher learns from, as a pairs table with `label` filled.

    - label 1: two mentions with the same officer id, whether blocking proposed them or not.
    - label 0: a candidate pair from blocking whose officer ids differ.
    - A pair where either officer id is missing has no label and is left out.

    The labels copy the register's own linking. Where the register gave one person two
    officer ids, label 0 is wrong: the tiny world's phoenix is exactly that case. So the
    matcher is also checked by hand (31.4) and at the decision level against the baselines.
    Give it the mentions of one split at a time: training mentions to train, validation
    mentions to validate.
    """
    officer = mentions.set_index("mention_id")["officer_id"]
    same_id = officer_pairs(mentions)
    candidates = candidate_pairs(mentions)
    proposed = set(zip(candidates["a"], candidates["b"]))
    rows = []
    for a, b in sorted(same_id | proposed):   # sorted: the same order every run (R7)
        if pd.isna(officer[a]) or pd.isna(officer[b]) or not str(officer[a]).strip() or not str(officer[b]).strip():
            continue
        rows.append(dict(a=a, b=b, p=None, features=None, method="labels", label=int((a, b) in same_id)))
    pairs = pd.DataFrame(rows, columns=ev.PAIR_COLS)
    ev.check_columns(pairs, "pairs")
    return pairs


# --- 31.2 The matcher -----------------------------------------------------------------

def train_matcher(X, y, seed):
    """31.2: fit a logistic regression on the feature rows X and their labels y (1 or 0).

    A logistic regression learns one weight per feature. A positive weight means "when
    this is 1, the two records are more likely the same person". The same X, y and seed
    always give the same model (R7).
    """
    model = LogisticRegression(random_state=seed)
    model.fit(X[FEATURE_COLS], list(y))
    return model


def match_probability(model, features):
    """31.2: the matcher's p for each feature row, between 0 and 1: how likely "same person" is."""
    return model.predict_proba(features[FEATURE_COLS])[:, 1]


def matcher_weights(model):
    """The learned weight of each feature, plus the starting point ("intercept"), for printing."""
    weights = pd.Series(model.coef_[0], index=FEATURE_COLS)
    weights["intercept"] = model.intercept_[0]
    return weights


def scored_pairs(model, pairs, mentions):
    """31.2: `pairs` with p from the matcher and the features behind it, as a pairs table.

    Every pair stays in the table, however low its p: nothing is merged or dropped (R6).
    """
    features = pair_features(pairs, mentions)
    scored = pairs.copy()
    scored["p"] = match_probability(model, features)
    scored["features"] = features.to_dict("records")
    scored["method"] = "matcher"
    ev.check_columns(scored, "pairs")
    return scored
