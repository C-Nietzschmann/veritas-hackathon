"""A harder baseline and a stress test for the matcher (card #191).

Two questions a judge would ask, answered on validation companies only:
1. Does the matcher beat the simple rule "same name and same birth month and year"?
2. Does it still link one person's two records when one of them is written differently:
   a typo, a dropped middle name, a wrong or missing birth date, a new address?
"""

import random

import numpy as np
import pandas as pd

from src import baseline, resolve
from src import evidence as ev

# --- 1. The harder baseline -------------------------------------------------------------


def name_and_birth(links, mentions):
    """For each row of `links` (real_slice.method_links): same name AND same birth month and year?

    A missing birth date never counts as the same.
    """
    people = mentions.set_index("mention_id")
    # year and month as one number, for example 197903. Missing gives NaN, and NaN equals nothing.
    birth = (pd.to_numeric(people["birth_year"], errors="coerce") * 100
             + pd.to_numeric(people["birth_month"], errors="coerce"))
    director = birth.loc[links["director"]].to_numpy(dtype=float)
    record = birth.loc[links["record"]].to_numpy(dtype=float)
    return links["same name"].to_numpy(dtype=bool) & (director == record)


def compare(links, methods):
    """Per method: the links it makes, how many the register confirms (same officer id) and how
    many it doesn't, recall against the register, and the companies that would get a warning."""
    confirmed = (links["register"] == "same officer id").to_numpy()
    rows = {}
    for method in methods:
        made = links[method].to_numpy(dtype=bool)
        found = int((made & confirmed).sum())
        rows[method] = {"links": int(made.sum()), "confirmed": found, "not confirmed": int(made.sum()) - found,
                        "recall vs the register": round(found / confirmed.sum(), 3) if confirmed.any() else None,
                        "companies linked": links.loc[made, "company_id"].nunique()}
    return pd.DataFrame.from_dict(rows, orient="index")


# --- 2. The stress test -----------------------------------------------------------------


def split_name(name):
    """(surname, forenames) of "HARROW, Daniel James" or "Daniel James Harrow"."""
    if "," in name:
        surname, forenames = name.split(",", 1)
        return surname.strip(), forenames.split()
    words = name.split()
    return (words[-1], words[:-1]) if words else ("", [])


def join_name(surname, forenames):
    """Back to the register's way of writing: "HARROW, Daniel James"."""
    return surname + ", " + " ".join(forenames)


def typo(word, rng):
    """Swap two neighbouring letters inside the word: "harrow" -> "hrarow". The first letter stays."""
    if len(word) < 4:
        return word + word[-1:]   # too short to swap inside: double the last letter instead
    i = rng.randrange(1, len(word) - 2)
    return word[:i] + word[i + 1] + word[i] + word[i + 2:]


def change_names(records, change):
    """`records` with `change(surname, forenames)` applied to every name."""
    records["name"] = [join_name(*change(*split_name(name))) for name in records["name"]]
    return records


def changes(rng):
    """Each change as (what happened, a function that does it to a table of person records)."""
    def moved(records):
        records["postcode"] = "ZZ99 9ZZ"   # a postcode that doesn't exist
        return records

    def birth_month_off(records):
        month = pd.to_numeric(records["birth_month"], errors="coerce")
        records["birth_month"] = month % 12 + 1   # the next month; December becomes January
        return records

    def birth_missing(records):
        records["birth_year"] = None
        records["birth_month"] = None
        return records

    return [
        ("nothing changed", lambda records: records),
        ("moved (new postcode)", moved),
        ("typo in the first name", lambda r: change_names(r, lambda s, f: (s, [typo(f[0], rng)] + f[1:] if f else f))),
        ("typo in the surname", lambda r: change_names(r, lambda s, f: (typo(s, rng), f))),
        ("middle names dropped", lambda r: change_names(r, lambda s, f: (s, f[:1]))),
        ("birth month one off", birth_month_off),
        ("birth date missing", birth_missing),
        ("new surname", lambda r: change_names(r, lambda s, f: ("ZZQXVK", f))),
    ]


def stress_test(model, mentions, pairs, seed):
    """Change one record of each pair in `pairs` and ask again: is it still linked?

    `pairs` are pairs the register confirms as one person (columns a and b). For each change,
    the second record is rewritten and the pair goes through the matcher's own steps: blocking
    must still propose it, and the match score must be 0.5 or more. Next to it, the same-name rule.
    Returns one row per change, in percent of the pairs.
    """
    people = mentions.set_index("mention_id")
    has_names = [isinstance(people.at[a, "name"], str) and isinstance(people.at[b, "name"], str)
                 for a, b in zip(pairs["a"], pairs["b"])]
    pairs = pairs[has_names]
    if pairs.empty:
        return pd.DataFrame()
    first = people.loc[pairs["a"]].reset_index()
    second = people.loc[pairs["b"]].reset_index()
    # New ids, so every pair stands alone even when one record is in several pairs
    first["mention_id"] = [f"A{i:06d}" for i in range(len(first))]
    second["mention_id"] = [f"B{i:06d}" for i in range(len(second))]
    asked = pd.DataFrame({"a": first["mention_id"], "b": second["mention_id"], "p": None, "features": None,
                          "method": "candidates", "label": None}, columns=ev.PAIR_COLS)

    rng = random.Random(seed)   # the same typos every run
    rows = {}
    for what, change in changes(rng):
        changed = change(second.copy())
        both = pd.concat([first, changed], ignore_index=True)
        candidates = resolve.candidate_pairs(both)
        proposed = set(zip(candidates["a"], candidates["b"]))
        kept = np.array([pair in proposed for pair in zip(asked["a"], asked["b"])])
        score = np.asarray(resolve.match_probability(model, resolve.pair_features(asked, both)))
        names_a = first["name"].map(baseline.normalise_name)
        names_b = changed["name"].map(baseline.normalise_name)
        same_name = np.array([x == y and x != "" for x, y in zip(names_a, names_b)])
        rows[what] = {"pairs": len(asked),
                      "blocking still proposes it %": round(100 * kept.mean(), 1),
                      "matcher still links it %": round(100 * (kept & (score >= 0.5)).mean(), 1),
                      "same-name rule still links it %": round(100 * same_name.mean(), 1)}
    return pd.DataFrame.from_dict(rows, orient="index")
