"""Masking: how a person's name and postcode may be shown in public (card #49).

The repo is public, so no output may identify a real director:
- names become pseudonyms: the same name always gives the same invented label
- postcodes keep only the district, the part before the space ("SW1A 1AA" -> "SW1A")
- birth dates are never shown, so they need no function here

The adapter calls these once, at ingestion, to fill display_name and display_postcode (#111).
"""

import hashlib
import re

# A UK postcode: the district (1-2 letters, a digit, maybe one more letter or digit),
# then the last part (a digit and two letters). The space between them is optional.
UK_POSTCODE = re.compile(r"^([A-Z]{1,2}[0-9][A-Z0-9]?) ?([0-9][A-Z]{2})$")

# 8 hex characters = about 4 billion labels, so two different names almost never share one.
LABEL_LENGTH = 8


def clean_name(name):
    """Make small writing differences irrelevant: "HARROW,  Daniel " and "harrow, daniel" are the same name."""
    return " ".join(str(name).split()).casefold()


def pseudonym(name):
    """The same name always gets the same label, so the name itself is never shown.

    The label is the start of a SHA-256 hash, which has no "undo". That keeps names off the page,
    but it is not secrecy: the register is public, so someone who already has a list of names can
    hash each one and compare the labels. Missing or empty names give an empty string.
    """
    if name is None or not str(name).strip():
        return ""
    digest = hashlib.sha256(clean_name(name).encode("utf-8")).hexdigest()
    return "Person " + digest[:LABEL_LENGTH].upper()


def mask_postcode(postcode):
    """Keep only the district of a UK postcode. Anything that isn't one gives an empty string."""
    if postcode is None:
        return ""
    match = UK_POSTCODE.match(" ".join(str(postcode).split()).upper())
    if not match:
        return ""
    return match.group(1)
