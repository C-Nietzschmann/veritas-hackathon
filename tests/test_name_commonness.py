"""Tests for the name-commonness bands (card #105), on the tiny world and small hand-made tables."""
import pandas as pd

from src import evaluate
from tests.tiny_world import tiny_world


def people(names):
    return pd.DataFrame({"mention_id": [f"m{i}" for i in range(len(names))], "kind": "person", "name": names})


def test_surname_from_both_ways_of_writing_a_name():
    assert evaluate.surname("HARROW, Daniel") == evaluate.surname("Daniel  Harrow") == "harrow"


def test_the_tiny_world_bands():
    mentions, _, _ = tiny_world()
    bands = evaluate.name_commonness(mentions)
    names = mentions.set_index("mention_id").loc[bands.index, "name"]
    by_name = dict(zip(names, bands))
    assert by_name["Ruth Okafor"] == "rare"            # once
    assert by_name["Priya Lambert"] == "medium"        # twice
    assert by_name["James Smith"] == by_name["Daniel Harrow"] == "common"   # three times each
    assert len(bands) == (mentions["kind"] == "person").sum()   # every person gets a band, no company does


def test_a_surname_seen_once_is_never_common():
    bands = evaluate.name_commonness(people(["A, X", "B, Y", "C, Z"]))
    assert set(bands) == {"rare"}


def test_band_sizes_count_every_person():
    bands = evaluate.name_commonness(people(["SMITH, A", "SMITH, B", "SMITH, C", "JONES, D", "JONES, E", "OKAFOR, F"]))
    assert bands.value_counts().to_dict() == {"common": 3, "medium": 2, "rare": 1}
