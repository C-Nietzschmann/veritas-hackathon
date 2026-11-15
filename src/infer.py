"""One identity per director (card #32): a director is at most one of their candidate earlier people.

The formula in decide.py treats every match as independent: with two 50% candidates it
says "75% that he is at least one of them". But one director is one person. He can't be
both. This box takes the same match probabilities and rules out the impossible cases.

32.1 The closed form, for one director and candidates that don't interact with anyone else.

32.2 Possible worlds, for the cases that do interact (two directors pointing at the same
earlier person), and as a check on the closed form. A world is one complete guess at who
is who: every match is "yes" or "no". Draw many worlds, throw away the ones that break the
rule, and count in the rest how often each match is "yes".
"""

import hashlib
import warnings

import numpy as np
import pandas as pd

from src import evidence as ev


def one_identity(ps):
    """32.1: the chance that the director is each candidate, given he is at most one of them.

    ps: the match probability of each candidate earlier person, each taken on its own.
    Returns one share per candidate, in the same order. What is left, 1 − their sum, is the
    chance he is "nobody we know".

    How: turn each p into odds = p / (1 − p). Candidate k gets odds_k / (1 + sum of all odds).
    Why: with independent matches, the case "only k is right" has chance odds_k × C, and the
    case "none is right" has chance 1 × C, with the same C for all of them. Every case with
    two or more right is impossible, so it is dropped, and the rest are scaled to add up to 1.

    - One candidate gives back its p unchanged.
    - The shares never add up to more than 1.
    - A candidate with p = 1 is certain, so he gets everything. Two certain candidates
      contradict each other; they share equally.
    """
    ps = [float(p) for p in ps]
    for p in ps:
        if not 0 <= p <= 1:   # written this way round so that a missing value (NaN) is caught too
            raise ValueError(f"a match probability must be between 0 and 1, not {p}")

    certain = [p == 1 for p in ps]
    if any(certain):
        # The odds of p = 1 are infinite, so the formula below can't be used.
        return [1 / sum(certain) if is_certain else 0.0 for is_certain in certain]

    odds = [p / (1 - p) for p in ps]
    total = 1 + sum(odds)   # the 1 stands for "nobody we know"
    return [one / total for one in odds]


# --- 32.2 Possible worlds -------------------------------------------------------------

def person_pairs(pairs, person_of):
    """Turn pairs of records into pairs of people: candidates are people, not records (ADR-004).

    person_of: {mention_id: officer id}, for example mentions.set_index("mention_id")["officer_id"].
    A record with no officer id stands for itself.
    - Two records of one registered person are no candidates for each other: that pair is dropped.
    - Several record pairs between the same two people become one pair with the highest p.
      Otherwise two records of one earlier person would compete with each other, or count twice.
    """
    ev.check_columns(pairs, "pairs")

    def person(mention_id):
        officer = person_of.get(mention_id)
        if officer is None or pd.isna(officer) or not str(officer).strip():
            return mention_id
        return officer

    best = {}
    for a, b, p in zip(pairs["a"], pairs["b"], pairs["p"]):
        key = tuple(sorted((person(a), person(b))))
        if key[0] != key[1]:
            best[key] = max(float(p), best.get(key, 0.0))
    rows = [dict(a=a, b=b, p=p, features=None, method="person_pairs", label=None)
            for (a, b), p in sorted(best.items())]
    return pd.DataFrame(rows, columns=ev.PAIR_COLS)


def pair_draws(key, n, seed):
    """n random numbers between 0 and 1 for one pair.

    They depend only on the seed and the pair's own two ids, never on which other pairs
    exist or in what order. So adding or changing another pair can't change these (R7).
    """
    # repr keeps the three parts apart whatever characters the ids contain
    digest = hashlib.sha256(repr((seed, key[0], key[1])).encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big")).random(n)


def groups(keys):
    """Sort pairs into groups: two pairs are in one group when they share a record, directly
    or through other pairs. Pairs in different groups can't affect each other.
    Returns {group label: [pair keys]}.
    """
    neighbours = {}   # record -> the records it shares a pair with
    for a, b in keys:
        neighbours.setdefault(a, []).append(b)
        neighbours.setdefault(b, []).append(a)

    group_of = {}     # record -> its group's label, which is the record the walk started from
    for start in neighbours:
        if start in group_of:
            continue
        group_of[start] = start
        to_visit = [start]
        while to_visit:   # walk to every record that can be reached from start
            for other in neighbours[to_visit.pop()]:
                if other not in group_of:
                    group_of[other] = start
                    to_visit.append(other)

    members = {}
    for key in keys:
        members.setdefault(group_of[key[0]], []).append(key)
    return members


def sample_worlds(pairs, n=400, seed=0):
    """32.2: each pair's chance of being right when every record is at most one other person.

    1. For every pair, n coin tosses that land "yes" with its p: n worlds. All tosses are
       made up front from the seed (pair_draws).
    2. Group by group, throw away every world in which some record has two "yes" pairs.
    3. A pair's new p is the share of its group's kept worlds in which it is "yes".

    Returns the pairs table with the new p, method "possible_worlds", and two more columns:
    depends_on (the pairs of its group, the matches this number rests on) and worlds_kept
    (how many worlds it rests on). With 400 kept worlds a p is within about ±0.05 of the
    exact value. When no world of a group is kept, its p is empty and a warning says so.

    ponytail: throwing worlds away is wasteful when one record has many likely candidates,
    because almost every world then breaks the rule. If worlds_kept gets too small on the
    real slice, draw each record's identity from one_identity instead.
    """
    ev.check_columns(pairs, "pairs")
    keys = [tuple(sorted(pair)) for pair in zip(pairs["a"], pairs["b"])]
    if len(set(keys)) != len(keys):
        raise ValueError("the same pair is listed twice: sample_worlds needs each pair once")

    ps = [float(p) for p in pairs["p"]]
    for p in ps:
        if not 0 <= p <= 1:   # catches a missing p (NaN) too: an unscored pair is not a "no"
            raise ValueError(f"a match probability must be between 0 and 1, not {p}")

    # 1. Every toss, up front: for each pair, the worlds in which it is "yes".
    yes = {key: pair_draws(key, n, seed) < p for key, p in zip(keys, ps)}

    result = {}
    for group in groups(keys).values():
        # 2. In each world, in how many "yes" pairs is each record? More than one breaks the rule.
        times_matched = {}
        for key in group:
            for record in key:
                times_matched[record] = times_matched.get(record, 0) + yes[key]
        kept = np.ones(n, dtype=bool)
        for count in times_matched.values():
            kept &= count <= 1

        # 3. Count the "yes" among the kept worlds.
        rests_on, worlds_kept = sorted(group), int(kept.sum())
        for key in group:
            new_p = float(yes[key][kept].mean()) if worlds_kept else None
            result[key] = (new_p, rests_on, worlds_kept)

    no_worlds = sum(1 for new_p, _, _ in result.values() if new_p is None)
    if no_worlds:
        warnings.warn(f"{no_worlds} pairs have no world left out of {n}: their matches contradict "
                      "each other too often. Their p is empty.")

    sampled = pairs.copy()
    sampled["p"] = [result[key][0] for key in keys]
    sampled["method"] = "possible_worlds"
    sampled["depends_on"] = [result[key][1] for key in keys]
    sampled["worlds_kept"] = [result[key][2] for key in keys]
    return sampled
