"""Tests for the name guard (card #112). All names are invented."""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import name_guard  # noqa: E402  (scripts/ is not a package, so it is put on the path first)


def write_notebook(path, output_text, source="print(table)"):
    """A one-cell notebook whose saved output is output_text."""
    notebook = {"cells": [{"cell_type": "code", "source": [source],
                           "outputs": [{"output_type": "stream", "text": [output_text]}]}]}
    path.write_text(json.dumps(notebook))
    return path


def test_catches_a_real_name_planted_in_an_output(tmp_path):
    nb = write_notebook(tmp_path / "nb.ipynb", "director: HARROW, Daniel\n")
    assert name_guard.find_names(nb, ["HARROW, Daniel"]) == [(1, "HARROW, Daniel")]


def test_catches_the_name_written_the_other_way_round(tmp_path):
    nb = write_notebook(tmp_path / "nb.ipynb", "Run by Daniel   Harrow since 2019")
    assert name_guard.find_names(nb, ["HARROW, Daniel"]) == [(1, "HARROW, Daniel")]


def test_catches_a_name_in_the_cell_itself(tmp_path):
    nb = write_notebook(tmp_path / "nb.ipynb", "ok", source='lookup("HARROW, Daniel")')
    assert name_guard.find_names(nb, ["HARROW, Daniel"]) == [(1, "HARROW, Daniel")]


def test_a_clean_notebook_passes(tmp_path):
    nb = write_notebook(tmp_path / "nb.ipynb", "director: Person F5F6763A, district ZZ1")
    assert name_guard.find_names(nb, ["HARROW, Daniel"]) == []


def test_a_name_inside_a_longer_word_is_not_a_match(tmp_path):
    nb = write_notebook(tmp_path / "nb.ipynb", "Jo Leeds Ltd")
    assert name_guard.find_names(nb, ["LEE, Jo"]) == []


def test_only_unmasked_people_count_as_real_names():
    mentions = pd.DataFrame({
        "kind": ["person", "person", "company"],
        "name": ["HARROW, Daniel", "OKAFOR, Ruth", "NORTHGATE ROOFING LTD"],
        "display_name": ["Person F5F6763A", "OKAFOR, Ruth", "NORTHGATE ROOFING LTD"],
    })
    # Ruth's display_name equals her name: that is the tiny world's invented-name case.
    assert name_guard.real_names(mentions) == ["HARROW, Daniel"]


def test_reads_the_real_notebook():
    # The guard can read main.ipynb's cells and saved outputs.
    assert len(name_guard.notebook_texts(name_guard.NOTEBOOK)) > 0
