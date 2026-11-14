"""Tests for the masking functions (card #110). Names here are invented."""
from src.mask import mask_postcode, pseudonym


def test_same_name_gives_same_pseudonym():
    assert pseudonym("HARROW, Daniel") == pseudonym("HARROW, Daniel")


def test_small_writing_differences_give_the_same_pseudonym():
    assert pseudonym("HARROW,  Daniel ") == pseudonym("harrow, daniel")


def test_different_names_give_different_pseudonyms():
    assert pseudonym("HARROW, Daniel") != pseudonym("HARROW, Danielle")


def test_the_real_name_cannot_be_read_from_the_pseudonym():
    label = pseudonym("HARROW, Daniel")
    assert label.startswith("Person ")
    assert "harrow" not in label.lower() and "daniel" not in label.lower()


def test_missing_name_gives_empty_string():
    assert pseudonym(None) == ""
    assert pseudonym("   ") == ""


def test_postcode_keeps_only_the_district():
    assert mask_postcode("SW1A 1AA") == "SW1A"
    assert mask_postcode("m1 1ae") == "M1"
    assert mask_postcode("ZZ11AA") == "ZZ1"


def test_anything_that_is_not_a_uk_postcode_gives_empty_string():
    assert mask_postcode(None) == ""
    assert mask_postcode("") == ""
    assert mask_postcode("75008") == ""          # a French postcode
    assert mask_postcode("1 Invented Road") == ""
