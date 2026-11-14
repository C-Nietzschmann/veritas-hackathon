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
"""

import re
from difflib import SequenceMatcher

import pandas as pd

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
