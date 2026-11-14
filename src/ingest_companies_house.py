"""The Companies House adapter: raw API responses become mentions and claims (card #25).

The raw layout. The crawler (#72, #73) saves each response once, untouched (R1):
- data/raw/company/{number}.json     the response of GET /company/{number}
- data/raw/insolvency/{number}.json  GET /company/{number}/insolvency, only for companies that have one
- data/raw/officers/{number}.json    GET /company/{number}/officers, with every officer of the
                                     company in one file (the API pages its answer, so the crawler
                                     asks for a page big enough or joins the pages)

The functions below take `raw`: {path: the file's bytes}, for example
{"data/raw/company/TW000001.json": b'{"company_name": ...}'}. load_raw() builds it.
Bytes, not parsed JSON, because every row keeps the file's hash in record_ref (R1).

Names, dates and codes are kept as the register writes them. Nothing is merged (R6).
The masked display columns stay empty here: that is card #111.
"""

import json
from pathlib import Path, PurePosixPath

import pandas as pd

from src import evidence as ev

SOURCE = "companies_house"           # source and origin of every row
ADAPTER = "ingest_companies_house"   # the code that made the row

# insolvency_on: the case types that count as the company failing (liquidation or administration).
# Left out on purpose: members-voluntary-liquidation (a solvent company closing itself down),
# voluntary arrangements, receivership, moratorium and foreign insolvency.
INSOLVENCY_CASE_TYPES = {
    "creditors-voluntary-liquidation",
    "compulsory-liquidation",
    "in-administration",
    "administration-order",          # administration under the rules before 2003
}

# The dates that say when one of those cases started.
CASE_START_DATE_TYPES = {
    "wound-up-on",                   # voluntary liquidation: the winding-up resolution
    "ordered-to-wind-up-on",         # compulsory liquidation: the court order
    "administration-started-on",     # administration
}

# Our slice is construction: SIC codes 41xxx, 42xxx and 43xxx.
SLICE_SIC_PREFIXES = ("41", "42", "43")


def load_raw(raw_dir="data/raw"):
    """Read every raw response under raw_dir into {path: bytes}.

    The path is kept as given (for example "data/raw/company/TW000001.json")
    because it goes into record_ref.
    """
    raw = {}
    for path in sorted(Path(raw_dir).glob("*/*.json")):
        raw[path.as_posix()] = path.read_bytes()
    return raw


def files_in(raw, folder):
    """The raw files of one folder ("company", "insolvency" or "officers"),
    as (path, company number, bytes). The file name is the company number.

    Sorted by path, so every run reads the files in the same order.
    """
    found = []
    for path in sorted(raw):
        if PurePosixPath(path).parent.name == folder:
            found.append((path, PurePosixPath(path).stem, raw[path]))
    return found


def company_mention_id(number):
    """The mention id of a company. Officer claims (#75) point at it, so both use this function."""
    return ev.make_id(SOURCE, f"company/{number}")


def provenance(path, row, raw_bytes):
    """Where a row came from: the raw file, the position in it, and the file's hash (R1, R2)."""
    return dict(source=SOURCE, record_ref=ev.record_ref(path, row, raw_bytes), origin=SOURCE, adapter=ADAPTER)


def insolvency_start(insolvency):
    """The earliest start date of a liquidation or administration case, or None.

    `insolvency` is the parsed insolvency response, or None if the company has none.
    """
    if insolvency is None:
        return None
    starts = []
    for case in insolvency.get("cases", []):
        if case.get("type") not in INSOLVENCY_CASE_TYPES:
            continue
        for date in case.get("dates", []):
            if date.get("type") in CASE_START_DATE_TYPES:
                starts.append(date["date"])
    if not starts:
        return None
    return min(starts)   # ISO dates (YYYY-MM-DD) sort correctly as text


def pick_sic_code(sic_codes):
    """One SIC code: the first construction code if there is one (our slice), else the first code."""
    for code in sic_codes:
        if code.startswith(SLICE_SIC_PREFIXES):
            return code
    if sic_codes:
        return sic_codes[0]
    return None


def companies_to_mentions(raw):
    """One company mention per company profile file (#74)."""
    insolvency = {}
    for path, number, raw_bytes in files_in(raw, "insolvency"):
        insolvency[number] = json.loads(raw_bytes)

    rows = []
    for path, number, raw_bytes in files_in(raw, "company"):
        profile = json.loads(raw_bytes)
        row = dict.fromkeys(ev.MENTION_COLS)   # every column, empty until filled
        row.update(
            mention_id=company_mention_id(number),
            kind="company",
            name=profile["company_name"],
            company_number=profile["company_number"],
            status=profile.get("company_status"),
            incorporated_on=profile.get("date_of_creation"),
            dissolved_on=profile.get("date_of_cessation"),
            insolvency_on=insolvency_start(insolvency.get(number)),
            sic_code=pick_sic_code(profile.get("sic_codes", [])),
            postcode=profile.get("registered_office_address", {}).get("postal_code"),
            **provenance(path, 0, raw_bytes),   # one company per file, so row 0
        )
        rows.append(row)
    return pd.DataFrame(rows, columns=ev.MENTION_COLS)
