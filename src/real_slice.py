"""The real slice (card #36): the query companies the crawl finished, labelled and split.

Not a box. Like main.ipynb, it only calls boxes: the adapter turns data/raw into mentions
and claims, and evaluate.py gives the label and the split. No box imports it (ADR-005).

The crawl (#24) writes a company into data/raw/query_companies.csv once all its files are
saved: its profile, insolvency file and officers, and its directors' earlier companies.
Those companies are the slice. Every other company in data/raw was reached through their
directors: it is evidence, never a query.

The second half answers one question on the slice: does an insolvent predecessor raise the
failure rate? It counts each company under the strongest link it has to an insolvent
earlier company, and gives each failure rate with its 95% interval.
"""

import math
from pathlib import Path

import pandas as pd

from src import baseline
from src import decide
from src import evaluate
from src import evidence as ev
from src import ingest_companies_house as adapter

ROOT = Path(__file__).resolve().parents[1]   # the repo folder: this file is in src/
DONE_FILE = "data/raw/query_companies.csv"   # the crawl's list of finished query companies


# --- The slice --------------------------------------------------------------------------

def query_companies(done_file=DONE_FILE):
    """The query companies the crawl finished, as a table with year and company_number (text).

    done_file is counted from the repo folder, like load_raw's folder. A company listed
    twice counts once.
    """
    done = pd.read_csv(ROOT / done_file, dtype=str)
    return done.drop_duplicates("company_number", ignore_index=True)


def build_evidence(raw):
    """The adapter's two tables for every raw file, (mentions, claims), checked against the schema."""
    companies = adapter.companies_to_mentions(raw)
    people, claims = adapter.officers_to_evidence(raw)
    mentions = pd.concat([companies, people], ignore_index=True)
    ev.check_rows(mentions, claims)   # stops here if a row breaks the shared schema
    return mentions, claims


def make_labels(mentions, numbers):
    """The labels table for these company numbers, in this order (ev.LABEL_COLS).

    failed is the team's label (evaluate.label_failures). split is "train", "validation"
    or "test" (evaluate.split), and None for a company formed outside 2021-2022.
    """
    companies = mentions[mentions["kind"] == "company"].set_index("company_number").loc[numbers]
    labels = pd.DataFrame({
        "company_id": numbers,
        "formed_on": companies["incorporated_on"].to_numpy(),
        "failed": evaluate.label_failures(mentions).loc[numbers].to_numpy(),
        "split": None,
    }, columns=ev.LABEL_COLS)
    # split() gives three tables: write each one's name next to its companies
    for name, part in zip(["train", "validation", "test"], evaluate.split(companies)):
        labels.loc[labels["company_id"].isin(part.index), "split"] = name
    return labels


def slice_from_raw(raw, numbers):
    """(mentions, claims, labels, left_out) from the raw files and the query companies' numbers.

    left_out says which query companies get no label, and why:
    - "no profile": no company profile on disk, so there is nothing to label
    - "insolvency file missing": the profile says has_insolvency_history but the file isn't
      there, so an empty insolvency_on would wrongly read as "not failed" (#76)
    """
    mentions, claims = build_evidence(raw)
    have_profile = set(mentions.loc[mentions["kind"] == "company", "company_number"])
    no_insolvency_file = set(adapter.companies_missing_insolvency(raw))
    left_out = {}
    for number in numbers:
        if number not in have_profile:
            left_out[number] = "no profile"
        elif number in no_insolvency_file:
            left_out[number] = "insolvency file missing"
    keep = [number for number in numbers if number not in left_out]
    return mentions, claims, make_labels(mentions, keep), left_out


def load_slice(raw_dir="data/raw", done_file=DONE_FILE):
    """The real slice in one call: (mentions, claims, labels, left_out), see slice_from_raw.

    mentions and claims cover every file in raw_dir, earlier companies included. labels has
    one row per finished query company that can be labelled.
    """
    raw = adapter.load_raw(raw_dir)
    numbers = list(query_companies(done_file)["company_number"])
    return slice_from_raw(raw, numbers)


# --- Which split a pair belongs to ----------------------------------------------------------

def person_split(mentions, claims, labels):
    """The split of each person mention: the split of the query company it is a director of.

    A director of any other company (an earlier company the crawl reached) gets None.
    Returns a Series indexed by mention_id.
    """
    company_number = mentions.set_index("mention_id")["company_number"]
    split_of = labels.set_index("company_id")["split"]
    people = mentions.loc[mentions["kind"] == "person", "mention_id"]
    of_company = claims.drop_duplicates("subject").set_index("subject")["object"].map(company_number)
    return pd.Series(people.map(of_company).map(split_of).to_numpy(), index=people.to_numpy(), name="split")


def pair_split(pairs, splits):
    """The split of each pair, from `splits` (person_split): a pair is held out as soon as
    one of its two people is.

    "test" if either person is in test, else "validation" if either is in validation,
    else "train", the pairs between two people at earlier companies included. So no pair
    of a validation company's director is ever learned from.
    """
    a, b = pairs["a"].map(splits), pairs["b"].map(splits)
    held_out = pd.Series("train", index=pairs.index)
    held_out[(a == "validation") | (b == "validation")] = "validation"
    held_out[(a == "test") | (b == "test")] = "test"
    return held_out


# --- The key table: does an insolvent predecessor raise the failure rate? --------------

# The links to an insolvent earlier company, strongest first.
LINKS = ["same officer id", "same name and birth month and year", "same name only"]


def link_pairs(mentions):
    """The pairs of person mentions behind each link, as {link: pairs table}.

    - same officer id: the register's own link (baseline.officer_link_pairs)
    - same name and birth month and year: the same name (baseline.normalise_name), the same
      birth month and year, and different officer ids
    - same name only: the same name, a different or unknown birth month and year, and
      different officer ids
    """
    people = mentions[mentions["kind"] == "person"].set_index("mention_id")
    by_name = baseline.same_name_pairs(mentions)
    a, b = people.loc[by_name["a"]], people.loc[by_name["b"]]

    def same(column):
        # as numbers, so 1979 and "1979" agree; a missing value never agrees with anything
        return (pd.to_numeric(a[column], errors="coerce").to_numpy()
                == pd.to_numeric(b[column], errors="coerce").to_numpy())

    other_id = a["officer_id"].to_numpy() != b["officer_id"].to_numpy()
    born_same = same("birth_month") & same("birth_year")
    return {
        "same officer id": baseline.officer_link_pairs(mentions),
        "same name and birth month and year": by_name[other_id & born_same].reset_index(drop=True),
        "same name only": by_name[other_id & ~born_same].reset_index(drop=True),
    }


def strongest_link(queries, mentions, claims, pairs_by_link):
    """Each query company's strongest link to an insolvent earlier company.

    One of LINKS, or "no predecessor", or "no director records". The rule is the decision
    layer's own (decide.candidate_matches): a director on record by the formation date,
    paired with someone who was a director of a company insolvent by that date (as-of rule).
    Returns a Series indexed by company number.
    """
    found = {}
    for query in queries:
        found[query] = "no predecessor"
        for link in LINKS:
            matches = decide.candidate_matches(query, mentions, claims, pairs_by_link[link])
            if matches is None:
                found[query] = "no director records"
                break
            if not matches.empty:
                found[query] = link
                break
    return pd.Series(found, name="link")


def wilson(k, n, z=1.96):
    """The 95% Wilson interval for k out of n, as (low, high) shares.

    Better than "rate ± 1.96 standard errors" for small counts: it never goes below 0 or
    above 1, and 0 out of 20 still gets an upper end above 0. n = 0 gives (nan, nan).
    """
    if n == 0:
        return math.nan, math.nan
    rate = k / n
    middle = (rate + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * math.sqrt(rate * (1 - rate) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return max(0.0, middle - half), min(1.0, middle + half)


def rate(k, n):
    """k out of n as text: "12 of 40: 30% (18-45%)", the rate with its 95% Wilson interval."""
    if n == 0:
        return "no companies"
    low, high = wilson(k, n)
    return f"{k} of {n}: {k / n:.0%} ({low * 100:.0f}-{high * 100:.0f}%)"


def rate_table(link, failed, failed_insolvency):
    """The key table: one row per link (no predecessor first), with the failure rates.

    link: strongest_link's Series. failed and failed_insolvency: True or False per company
    (the team's label, and liquidation or administration only), indexed by company number.
    Only companies in all three count.
    """
    both = pd.DataFrame({"link": link, "failed": failed, "failed_insolvency": failed_insolvency}).dropna()
    rows = []
    for name in ["no predecessor"] + LINKS + ["no director records"]:
        group = both[both["link"] == name]
        n = len(group)
        if name == "no director records" and n == 0:
            continue
        rows.append({"strongest link to an insolvent earlier company": name, "companies": n,
                     "failed (team label)": rate(int(group["failed"].sum()), n),
                     "failed through insolvency only": rate(int(group["failed_insolvency"].sum()), n)})
    return pd.DataFrame(rows)
