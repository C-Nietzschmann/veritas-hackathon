"""The tiny world: 28 hand-made rows with known answers (card #21).

Every box runs its tests on this before real data arrives. All names, company
numbers, officer ids and postcodes are invented: "TW" company numbers and "ZZ"
postcodes don't exist in the real register.

The stories it holds:
- Phoenix: Harrow Build Ltd goes into liquidation in March 2021. A month later
  the same Daniel Harrow starts Harrow Build Services Ltd, which fails within
  24 months. Companies House gave him a new officer id, so the officer-links
  baseline misses him.
- Look-alike: a different Daniel Harrow (other birth date, other postcode) runs
  Northgate Roofing Ltd. Same-name matching wrongly flags it.
- Common name: a different James Smith runs Elm Street Plumbing Ltd. The James
  Smith whose joinery went insolvent is someone else.
- The future must not leak: Elm Street's James Smith later runs a company that
  goes insolvent in 2024. Judged in 2021, that can't count (as-of rule).
- No evidence: Quiet Fields Landscaping Ltd has no director records at all.
- Clean: Priya Lambert's earlier company closed without any insolvency.
- Copied source: Priya's Brightwater appointment is recorded a second time by
  a source that copies Companies House, so it has the same origin (R5).

Use it like this: mentions, claims, truth = tiny_world()
"""

import json

import pandas as pd

from src import evidence as ev

SOURCE = "tiny_world"
COPY_SOURCE = "tiny_world_copy"   # a second source that copies Companies House
ORIGIN = "companies_house"        # who first published every record here
RAW_PATH = "tests/tiny_world.py"

# Earlier companies (the history) and query companies (the ones a supplier asks about).
COMPANIES = [
    # number      name                            formed        insolvent     dissolved     postcode   sic
    ("TW000001", "Harrow Build Ltd",              "2017-02-01", "2021-03-15", None,         "ZZ1 1AA", "41202"),
    ("TW000002", "Harrow Build Services Ltd",     "2021-04-20", "2022-09-01", None,         "ZZ1 1AB", "41202"),
    ("TW000003", "Northgate Roofing Ltd",         "2021-06-01", None,         None,         "ZZ7 2CD", "43910"),
    ("TW000004", "Smith and Sons Joinery Ltd",    "2015-05-01", "2020-10-01", None,         "ZZ3 3EF", "43320"),
    ("TW000005", "Elm Street Plumbing Ltd",       "2021-02-10", None,         None,         "ZZ4 4GH", "43220"),
    ("TW000006", "Quiet Fields Landscaping Ltd",  "2021-09-01", None,         None,         "ZZ6 6LM", "43999"),
    ("TW000007", "Brightwater Electrical Ltd",    "2021-05-15", None,         None,         "ZZ5 5JK", "43210"),
    ("TW000008", "Lambert Electrical Ltd",        "2016-03-01", None,         "2020-12-01", "ZZ5 5JK", "43210"),
    ("TW000009", "Smith Brothers Builders Ltd",   "2023-01-10", "2024-05-01", None,         "ZZ4 4GH", "41202"),
]

# One row per appointment record. The same real person can appear more than once:
# that is exactly what entity resolution has to work out.
APPOINTMENTS = [
    # key   name             born       officer id       postcode   company     from          to
    ("p1", "Daniel Harrow",  (1979, 4),  "tw-officer-01", "ZZ1 1AA", "TW000001", "2017-02-01", "2021-03-15"),
    ("p2", "Daniel Harrow",  (1979, 4),  "tw-officer-02", "ZZ1 1AB", "TW000002", "2021-04-20", None),
    ("p3", "Daniel Harrow",  (1990, 11), "tw-officer-03", "ZZ7 2CD", "TW000003", "2021-06-01", None),
    ("p4", "James Smith",    (1962, 2),  "tw-officer-04", "ZZ3 3EF", "TW000004", "2015-05-01", "2020-10-01"),
    ("p5", "James Smith",    (1988, 7),  "tw-officer-05", "ZZ4 4GH", "TW000005", "2021-02-10", None),
    ("p6", "Priya Lambert",  (1985, 3),  "tw-officer-06", "ZZ5 5JK", "TW000008", "2016-03-01", "2020-12-01"),
    ("p7", "Priya Lambert",  (1985, 3),  "tw-officer-06", "ZZ5 5JK", "TW000007", "2021-05-15", None),
    ("p8", "Ruth Okafor",    (1983, 6),  "tw-officer-07", "ZZ1 2BC", "TW000002", "2021-04-20", None),
    ("p9", "James Smith",    (1988, 7),  "tw-officer-05", "ZZ4 4GH", "TW000009", "2023-01-10", "2024-05-01"),
]

# The true answers, written with the friendly keys above.
SAME_PERSON = [("p1", "p2"), ("p5", "p9"), ("p6", "p7")]
LOOK_ALIKES = [("p1", "p3"), ("p2", "p3"), ("p4", "p5"), ("p4", "p9")]   # same name, different people
QUERIES = ["TW000002", "TW000003", "TW000005", "TW000006", "TW000007"]   # all formed in 2021
PREDECESSOR = {"TW000002": "TW000001", "TW000003": None, "TW000005": None, "TW000006": None, "TW000007": None}
DECISION = {
    "TW000002": "FLAG",                 # the phoenix
    "TW000003": "CLEAR",                # the innocent look-alike
    "TW000005": "CLEAR",                # the common name; the 2024 insolvency is the future
    "TW000006": "NOT ENOUGH EVIDENCE",  # no director records at all
    "TW000007": "CLEAR",                # clean history
}
FAILED = {"TW000002": True, "TW000003": False, "TW000005": False, "TW000006": False, "TW000007": False}


def provenance(row, record, source=SOURCE):
    """Where a hand-made row "came from": the record itself stands in for the raw response."""
    raw_bytes = json.dumps(record, sort_keys=True).encode("utf-8")
    return dict(source=source, record_ref=ev.record_ref(RAW_PATH, row, raw_bytes), origin=ORIGIN, adapter=SOURCE)


def tiny_world():
    """Return (mentions, claims, truth). Same tables every call: no randomness, stable ids."""
    mentions, claims, company_mention, person_mention = [], [], {}, {}

    for number, name, formed, insolvent, dissolved, postcode, sic in COMPANIES:
        status = "liquidation" if insolvent else ("dissolved" if dissolved else "active")
        row = dict.fromkeys(ev.MENTION_COLS)
        row.update(
            mention_id=ev.make_id(SOURCE, f"company/{number}"), kind="company",
            name=name, display_name=name,            # invented names are safe to show
            company_number=number, status=status, incorporated_on=formed,
            dissolved_on=dissolved, insolvency_on=insolvent, sic_code=sic,
            postcode=postcode, display_postcode=postcode.split()[0],
            **provenance(len(mentions), {"company": number, "name": name}),
        )
        company_mention[number] = row["mention_id"]
        mentions.append(row)

    for key, name, (year, month), officer, postcode, company, start, end in APPOINTMENTS:
        appointment = f"appointment/{officer}/{company}"
        row = dict.fromkeys(ev.MENTION_COLS)
        row.update(
            mention_id=ev.make_id(SOURCE, appointment), kind="person",
            name=name, display_name=name,
            birth_year=year, birth_month=month, nationality="British", officer_id=officer,
            postcode=postcode, display_postcode=postcode.split()[0],
            **provenance(len(mentions), {"appointment": appointment, "name": name}),
        )
        person_mention[key] = row["mention_id"]
        mentions.append(row)
        claims.append(dict(
            claim_id=ev.make_id(SOURCE, appointment), subject=row["mention_id"], relation="director_of",
            object=company_mention[company], valid_from=start, valid_to=end,
            **provenance(len(claims), {"appointment": appointment, "from": start, "to": end}),
        ))

    # The copied record: Priya's Brightwater appointment again, from a source that copies Companies House.
    copied = "appointment/tw-officer-06/TW000007"
    claims.append(dict(
        claim_id=ev.make_id(COPY_SOURCE, copied), subject=person_mention["p7"], relation="director_of",
        object=company_mention["TW000007"], valid_from="2021-05-15", valid_to=None,
        **provenance(len(claims), {"appointment": copied, "copied_from": ORIGIN}, source=COPY_SOURCE),
    ))

    def ids(pairs):
        return [tuple(sorted((person_mention[a], person_mention[b]))) for a, b in pairs]

    truth = {
        "queries": list(QUERIES),
        "same_person": ids(SAME_PERSON),
        "look_alikes": ids(LOOK_ALIKES),
        "predecessor": dict(PREDECESSOR),
        "decision": dict(DECISION),
        "failed": dict(FAILED),
        "mention": dict(person_mention, **company_mention),   # friendly key or company number -> mention_id
    }
    return pd.DataFrame(mentions, columns=ev.MENTION_COLS), pd.DataFrame(claims, columns=ev.CLAIM_COLS), truth
