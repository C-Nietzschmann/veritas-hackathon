"""One identity per director (card #32): a director is at most one of their candidate earlier people.

The formula in decide.py treats every match as independent: with two 50% candidates it
says "75% that he is at least one of them". But one director is one person. He can't be
both. This box takes the same match probabilities and rules out the impossible cases.

32.1 The closed form, for one director and candidates that don't interact with anyone else.
The possible-worlds sampler for the cases that do interact is card 32.2.
"""


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
