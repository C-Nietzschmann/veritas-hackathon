"""The hard rules R1-R8, one named test each, run on the tiny world (card #23).

The rules and the test each one gets are in vault/Decisions/Hard rules R1-R8.md.
Every test here must fail if its rule is broken. A test that waits for a box not
built yet is marked xfail with the card it waits for. R5 is skipped while we have
one source.
"""

import pandas as pd
import pytest

from src import evidence as ev
from tests.tiny_world import tiny_world


# --- Boxes not built yet -----------------------------------------------------------
# A test that needs a box not built yet imports it inside the test and is marked
# xfail(raises=ImportError): it may fail only because the box is missing. Once the box
# exists the test runs for real. It shows as XPASS while its rule holds (then delete its
# xfail line) and red when the rule is broken.
#
# Entity resolution (src/resolve.py, cards #30, #31) doesn't exist yet, so its function
# name below is a guess. When the box lands, change the line marked GUESS to its real call.

def resolve_pairs(mentions):
    """Entity resolution: mentions -> the pairs table (a, b, p, ...)."""
    from src import resolve
    return resolve.candidate_pairs(mentions)   # GUESS: wire to the real call (cards #30, #31)


# --- The rules ---------------------------------------------------------------------

def test_r1_rehashing_a_raw_record_matches_its_record_ref():
    """R1: raw evidence is immutable. The hash kept in record_ref matches the raw
    record it was built from, and stops matching once one byte changes."""
    mentions, _, truth = tiny_world()
    ref = mentions.set_index("mention_id").loc[truth["mention"]["TW000001"], "record_ref"]
    raw = b'{"company": "TW000001", "name": "Harrow Build Ltd"}'   # that row's raw record, typed out by hand
    assert ev.raw_unchanged(ref, raw)
    assert not ev.raw_unchanged(ref, raw.replace(b"Harrow", b"Harrov"))


def test_r2_every_row_names_its_source_and_record():
    """R2: every observed claim has traceable provenance. No tiny-world row has an empty
    source or record_ref, and check_rows refuses a row that loses one."""
    mentions, claims, _ = tiny_world()
    for table in (mentions, claims):
        for col in ("source", "record_ref"):
            assert not ev.is_blank(table[col]).any()

    mentions.loc[0, "source"] = None
    claims.loc[0, "record_ref"] = " "
    with pytest.raises(ev.SchemaError) as error:
        ev.check_rows(mentions, claims)
    assert f"mentions row {mentions.loc[0, 'mention_id']}: empty source" in str(error.value)
    assert f"claims row {claims.loc[0, 'claim_id']}: empty record_ref" in str(error.value)


def test_r3_every_observed_edge_is_a_stated_claim():
    """R3: inferred relationships are never shown as observed facts. Every edge of the
    observed graph is one claim row, source and record included, and a guess with no
    raw record behind it never becomes an edge."""
    _, claims, truth = tiny_world()
    cols = ["claim_id", "subject", "relation", "object", "source", "record_ref"]

    edges = ev.observed_graph(claims)
    assert len(edges) > 0
    claim_rows = set(claims[cols].itertuples(index=False))
    for edge in edges[cols].itertuples(index=False):
        assert edge in claim_rows

    # A guess nobody stated: the look-alike Daniel Harrow (p3) ran Harrow Build Ltd.
    guess = dict.fromkeys(ev.CLAIM_COLS)   # no source, no record_ref
    guess.update(claim_id="guess", subject=truth["mention"]["p3"], relation="director_of",
                 object=truth["mention"]["TW000001"])
    edges = ev.observed_graph(pd.concat([claims, pd.DataFrame([guess])], ignore_index=True))
    assert "guess" not in set(edges["claim_id"])


@pytest.mark.xfail(raises=ImportError, reason="needs entity resolution, cards #30, #31")
def test_r4_every_pair_carries_a_p():
    """R4: uncertainty survives downstream. Every pair from entity resolution carries a
    probability p between 0 and 1. A missing p becomes NaN, which fails."""
    mentions, _, _ = tiny_world()
    pairs = resolve_pairs(mentions)
    ev.check_columns(pairs, "pairs")
    assert len(pairs) > 0
    p = pd.to_numeric(pairs["p"], errors="coerce")
    assert p.between(0, 1).all()


def test_r4_every_inferred_link_keeps_its_pairs_p():
    """R4: uncertainty survives downstream. Each inferred link carries the p of the pair
    it rests on, unrounded: 0.9 stays 0.9 and never becomes a yes."""
    from src import decide
    mentions, claims, truth = tiny_world()
    person = truth["mention"]
    # Two pairs made by hand, standing in for entity resolution: the phoenix and a look-alike.
    pairs = pd.DataFrame([
        (person["p1"], person["p2"], 0.9, None, "by hand", None),
        (person["p1"], person["p3"], 0.05, None, "by hand", None),
    ], columns=ev.PAIR_COLS)
    for query, p in [("TW000002", 0.9), ("TW000003", 0.05)]:
        links = decide.candidate_matches(query, mentions, claims, pairs)
        ev.check_columns(links, "links")
        assert list(links["p"]) == [p]


@pytest.mark.skip(reason="one source")
def test_r5_copied_sources_are_not_independent_confirmations():
    """R5: support is counted per origin, not per row. Skipped while we have one source."""


def test_r6_look_alikes_stay_two_mentions():
    """R6: ambiguous identities are never silently merged. Each look-alike pair shares a
    name, yet stays two mentions and two people in the observed graph."""
    mentions, claims, truth = tiny_world()
    name = mentions.set_index("mention_id")["name"]
    people = set(ev.observed_graph(claims)["subject"])
    for a, b in truth["look_alikes"]:
        assert a != b
        assert a in people and b in people
        assert name[a] == name[b]   # same name: exactly what a careless merge would join


@pytest.mark.xfail(raises=ImportError, reason="needs entity resolution, cards #30, #31")
def test_r6_look_alikes_get_a_same_person_link_not_a_merge():
    """R6: entity resolution joins each look-alike pair with a "same person?" link and
    its probability, never a hard yes or no."""
    mentions, _, truth = tiny_world()
    pairs = resolve_pairs(mentions)
    p_of = {tuple(sorted((a, b))): p for a, b, p in zip(pairs["a"], pairs["b"], pairs["p"])}
    for pair in truth["look_alikes"]:
        assert pair in p_of
        assert 0 < p_of[pair] < 1


@pytest.mark.xfail(raises=ImportError, reason="placeholder until the one-identity task, card #32")
def test_r7_same_input_and_seed_give_the_same_output():
    """R7: inferences are reproducible and revisable. A placeholder: it checks nothing yet.
    The day src/infer.py exists it turns red, until the real test is written here: same
    input and seed give identical output, and changing one match changes only the links
    that list it in depends_on."""
    from src import infer  # noqa: F401
    pytest.fail("src/infer.py exists now: write the R7 test (card #32)")


def test_r8_no_evidence_gives_not_enough_evidence():
    """R8: no evidence means abstention. Quiet Fields Landscaping Ltd (TW000006) has no
    director records, so the decision layer says NOT ENOUGH EVIDENCE, never FLAG or CLEAR."""
    from src import decide
    mentions, claims, _ = tiny_world()
    no_pairs = ev.empty_table("pairs")   # no directors, so no pairs
    # With this line and these costs a company with directors and no match is CLEAR
    # (5% is under the 10% clear threshold). So only missing records give the abstention.
    line = (0.05, 0.6)   # made up: 5% of companies fail without an insolvent predecessor, 60% with one
    costs = (10, 2, 1)   # a missed case, a wrong flag, asking (ADR-004)
    matches = decide.candidate_matches("TW000006", mentions, claims, no_pairs)
    decision = decide.decide("TW000006", matches, line, costs)
    assert decision["decision"] == "NOT ENOUGH EVIDENCE"
