"""The Companies House adapter: raw API responses become mentions and claims (card #25).

The raw layout. The crawler (#72, #73) saves each response once, untouched (R1),
in the repo folder:
- data/raw/company/{number}.json     the response of GET /company/{number}
- data/raw/insolvency/{number}.json  GET /company/{number}/insolvency, fetched only when the
                                     company profile says has_insolvency_history
- data/raw/officers/{number}.json    GET /company/{number}/officers, one page of up to 100
                                     officers (the crawl flags any company that has more)

The functions below take `raw`: {path: the file's bytes}, for example
{"data/raw/company/TW000001.json": b'{"company_name": ...}'}. load_raw() builds it.
Bytes, not parsed JSON, because every row keeps the file's hash in record_ref (R1).

Names, dates and codes are kept as the register writes them. Nothing is merged (R6).

Masking happens here, once, so no later box has to remember it (card #111). Outputs show
the display columns only:
- a person's display_name is a pseudonym, the same for the same name
- a company's display_name is its name: a company is not a person, and it is public by number anyway
- display_postcode keeps only the district
- birth dates have no display column: they are never shown
"""

import json
import warnings
from pathlib import Path, PurePosixPath

import pandas as pd

from src import evidence as ev
from src import mask

ROOT = Path(__file__).resolve().parents[1]   # the repo folder: this file is in src/, one level below it

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

# The officer roles that are directors who are people. Every other role is skipped:
# secretaries, and corporate-director and the other corporate-* roles (a company, not a person).
DIRECTOR_ROLES = {"director", "nominee-director"}


def load_raw(raw_dir="data/raw"):
    """Read every raw response under raw_dir into {path: bytes}.

    raw_dir is a folder inside the repo, counted from the repo folder and not from where
    Python was started, so a notebook running in notebooks/ reads the same files.
    The paths are counted from the repo folder too (for example
    "data/raw/company/TW000001.json"). They go into record_ref, so they are the same
    on every machine and never carry a local folder name.
    """
    raw = {}
    for path in sorted((ROOT / raw_dir).glob("*/*.json")):
        raw[path.relative_to(ROOT).as_posix()] = path.read_bytes()
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
            # A start entry with its date left empty tells us nothing, so it is skipped.
            if date.get("type") in CASE_START_DATE_TYPES and date.get("date"):
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


def companies_missing_insolvency(raw):
    """The numbers of the companies whose insolvency data is missing.

    The crawl fetches the insolvency file only when the profile says has_insolvency_history.
    So a profile with that flag and no insolvency file means we don't know whether the
    company failed. Without the flag, no file simply means no insolvency.

    These companies still get a mention, with insolvency_on empty, because officer claims
    point at them. Whoever builds the labels (card #76 and the notebook) must leave them
    out: an empty insolvency_on would otherwise read as "not failed".
    """
    have_file = {number for path, number, raw_bytes in files_in(raw, "insolvency")}
    missing = []
    for path, number, raw_bytes in files_in(raw, "company"):
        if json.loads(raw_bytes).get("has_insolvency_history") and number not in have_file:
            missing.append(number)
    return missing


def companies_to_mentions(raw):
    """One company mention per company profile file (#74).

    An insolvency file that exists is always used, whatever has_insolvency_history says.
    Companies with the flag and no file are reported in a warning: see companies_missing_insolvency.
    """
    missing = companies_missing_insolvency(raw)
    if missing:
        warnings.warn(
            f"{len(missing)} companies have has_insolvency_history but no insolvency file: {missing}. "
            "Their insolvency_on is empty because the data is missing. Leave them out of the labels."
        )

    insolvency = {}
    for path, number, raw_bytes in files_in(raw, "insolvency"):
        insolvency[number] = json.loads(raw_bytes)

    rows = []
    for path, number, raw_bytes in files_in(raw, "company"):
        profile = json.loads(raw_bytes)
        postcode = profile.get("registered_office_address", {}).get("postal_code")
        row = dict.fromkeys(ev.MENTION_COLS)   # every column, empty until filled
        row.update(
            mention_id=company_mention_id(number),
            kind="company",
            name=profile["company_name"],
            display_name=profile["company_name"],   # a company's name may be shown
            company_number=profile["company_number"],
            status=profile.get("company_status"),
            incorporated_on=profile.get("date_of_creation"),
            dissolved_on=profile.get("date_of_cessation"),
            insolvency_on=insolvency_start(insolvency.get(number)),
            sic_code=pick_sic_code(profile.get("sic_codes", [])),
            postcode=postcode,
            display_postcode=mask.mask_postcode(postcode),
            **provenance(path, 0, raw_bytes),   # one company per file, so row 0
        )
        rows.append(row)
    return pd.DataFrame(rows, columns=ev.MENTION_COLS)


def officer_id(officer):
    """The register's officer id, from the link "/officers/{id}/appointments".

    Stored as the matcher's label only, never used as a feature (ADR-003).
    """
    return officer["links"]["officer"]["appointments"].split("/")[2]


def officers_to_evidence(raw):
    """One person mention and one director_of claim per director appointment (#75).

    Only directors who are people count (DIRECTOR_ROLES): secretaries and corporate
    directors are skipped. Every appointment gets its own mention, even when the same
    person appears at two companies under the same officer id: deciding who is who
    is entity resolution's job (R6).

    A director record that ends before it starts is skipped too, with no mention and
    no claim, and a warning says how many there were. So:
    director records in = claims out + records skipped.
    """
    mentions, claims = [], []
    skipped = 0
    for path, number, raw_bytes in files_in(raw, "officers"):
        items = json.loads(raw_bytes).get("items", [])
        for position, officer in enumerate(items):
            if officer.get("officer_role") not in DIRECTOR_ROLES:
                continue

            # Appointments from before 1992 have no appointed_on, only appointed_before.
            # The appointment certainly existed by that date, so the as-of rule keeps it.
            # (A claim with no start date is dropped by the as-of rule.)
            valid_from = officer.get("appointed_on") or officer.get("appointed_before")
            valid_to = officer.get("resigned_on")   # None while the director still serves

            # A resignation dated before the appointment can't be right, and check_rows
            # refuses such a claim, so the record is skipped and counted here. The same goes
            # for a pre-1992 appointment that ended before its appointed_before date: it has
            # no start date we can use. ISO dates (YYYY-MM-DD) compare correctly as text.
            if valid_from and valid_to and valid_to < valid_from:
                skipped += 1
                continue

            # The appointment's own link, "/company/{number}/appointments/{id}", is unique
            # and stays the same on every crawl, so the ids do too (R7).
            appointment = officer["links"]["self"]
            born = officer.get("date_of_birth", {})
            postcode = officer.get("address", {}).get("postal_code")

            person = dict.fromkeys(ev.MENTION_COLS)   # every column, empty until filled
            person.update(
                mention_id=ev.make_id(SOURCE, f"person{appointment}"),
                kind="person",
                name=officer["name"],
                display_name=mask.pseudonym(officer["name"]),   # the only name an output may show
                birth_month=born.get("month"),
                birth_year=born.get("year"),
                nationality=officer.get("nationality"),
                officer_id=officer_id(officer),
                postcode=postcode,
                display_postcode=mask.mask_postcode(postcode),
                **provenance(path, position, raw_bytes),
            )
            mentions.append(person)

            claims.append(dict(
                claim_id=ev.make_id(SOURCE, f"director_of{appointment}"),
                subject=person["mention_id"],
                relation="director_of",
                object=company_mention_id(number),   # the company mention from companies_to_mentions
                valid_from=valid_from,
                valid_to=valid_to,
                **provenance(path, position, raw_bytes),
            ))
    if skipped:
        warnings.warn(f"{skipped} director records skipped: the resignation is dated before the appointment.")
    return pd.DataFrame(mentions, columns=ev.MENTION_COLS), pd.DataFrame(claims, columns=ev.CLAIM_COLS)
