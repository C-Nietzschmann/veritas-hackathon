"""The real slice (card #36): the query companies the crawl finished, labelled and split.

Not a box. Like main.ipynb, it only calls boxes: the adapter turns data/raw into mentions
and claims, and evaluate.py gives the label and the split. No box imports it (ADR-005).

The crawl (#24) writes a company into data/raw/query_companies.csv once all its files are
saved: its profile, insolvency file and officers, and its directors' earlier companies.
Those companies are the slice. Every other company in data/raw was reached through their
directors: it is evidence, never a query.

The second half answers one question on the slice: does an insolvent predecessor raise the
failure rate? It counts each company under the strongest link it has to an insolvent
earlier company, and gives each failure rate with its 95% interval. The second key table
asks the same with another predecessor: an earlier company that failed the way our own
label defines failure.

The third part measures the headline on the validation companies: which earlier records
each method (the same-name rule, officer links, the matcher) calls the same person, how many
of those links the register doesn't confirm, per name-commonness band, and a sample of them
for a hand check whose sheet stays off git.
"""

import html
import json
import math
import re
from pathlib import Path

import numpy as np
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
        rows.append({"strongest link": name, "companies": n,
                     "failed (team label)": rate(int(group["failed"].sum()), n),
                     "failed through insolvency only": rate(int(group["failed_insolvency"].sum()), n)})
    return pd.DataFrame(rows)


# --- The second key table: earlier companies that failed the way our label defines it ----

def failure_dates(mentions, window_months=24):
    """Each company's failure date under the team's label, or NaT ("not a time") if it didn't fail.

    The label (evaluate.label_failures) calls a company failed when it went into liquidation
    or administration (insolvency_on), or was dissolved (dissolved_on), within window_months of
    its own incorporation. The failure date is the earlier of those two dates inside the window.
    Returns a Series indexed by company number.
    """
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    deadline = evaluate.read_dates(companies["incorporated_on"]) + pd.DateOffset(months=window_months)
    insolvent = evaluate.read_dates(companies["insolvency_on"])
    dissolved = evaluate.read_dates(companies["dissolved_on"])
    in_window = pd.DataFrame({"insolvent": insolvent.where(insolvent <= deadline),
                              "dissolved": dissolved.where(dissolved <= deadline)})
    return in_window.min(axis=1).rename("failed_on")   # the earlier date; NaT when there is neither


APPOINTMENT_COLS = ["officer_id", "name", "birth_month", "birth_year", "company_number", "appointed_on"]


def appointment_rows(raw):
    """One row per directorship in the saved appointment lists, with the columns APPOINTMENT_COLS.

    The crawl saved one page of up to 50 appointments, newest first, for each query company's
    directors and their same-name officers: data/raw/appointments/{officer id}.json. The name
    is as written on that appointment; birth month and year come from the top of the list. The
    start date is appointed_on, or appointed_before for an appointment from before 1992, as in
    the adapter. Only directors who are people count (adapter.DIRECTOR_ROLES), as in the adapter.
    """
    rows = []
    for path, officer, raw_bytes in adapter.files_in(raw, "appointments"):
        listing = json.loads(raw_bytes)
        born = listing.get("date_of_birth") or {}
        for item in listing.get("items", []):
            if item.get("officer_role") not in adapter.DIRECTOR_ROLES:
                continue
            rows.append(dict(officer_id=officer, name=item.get("name") or listing.get("name"),
                             birth_month=born.get("month"), birth_year=born.get("year"),
                             company_number=item.get("appointed_to", {}).get("company_number"),
                             appointed_on=item.get("appointed_on") or item.get("appointed_before")))
    return pd.DataFrame(rows, columns=APPOINTMENT_COLS)


def birth(table):
    """Birth month and year as one text, like "1979-4". Missing when either part is missing."""
    year = pd.to_numeric(table["birth_year"], errors="coerce").astype("Int64").astype("string")
    month = pd.to_numeric(table["birth_month"], errors="coerce").astype("Int64").astype("string")
    return year + "-" + month


def strongest_failed_link(queries, mentions, claims, appointments, failed_on):
    """Each query company's strongest link to an earlier company that failed, through the
    saved appointment lists. With failure_dates, this is the second key table.

    failed_on: a failure date per company number (NaT: it never failed). An earlier company
    counts when that date is on or before the query company's formation date: the as-of rule
    of the first table, which counts the formation day itself. The links, strongest first (LINKS):
    - same officer id: the earlier company is in one of the directors' own appointment lists
    - same name and birth month and year: another officer with the director's name
      (baseline.normalise_name) and the same birth month and year was its director
    - same name only: the same, with a different or unknown birth month and year
    The directors are the ones on record by the formation date, as in strongest_link. An
    appointment at the earlier company counts if it started by that date too.
    Returns a Series indexed by company number: one of LINKS, "no predecessor" or "no director records".
    """
    people = mentions.set_index("mention_id")
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    people_born = birth(people)
    rows = appointments.assign(
        key=appointments["name"].map(baseline.normalise_name),
        born=birth(appointments),
        started=evaluate.read_dates(appointments["appointed_on"]),
        failed_on=appointments["company_number"].map(failed_on))
    found = {}
    for query in queries:
        formed = pd.Timestamp(companies.loc[query, "incorporated_on"])
        edges = ev.observed_graph(claims, as_of=formed)   # the register as it stood that day
        directors = edges.loc[edges["object"] == companies.loc[query, "mention_id"], "subject"]
        if directors.empty:
            found[query] = "no director records"
            continue
        earlier = rows[(rows["company_number"] != query) & (rows["started"] <= formed) & (rows["failed_on"] <= formed)]
        links = set()
        for director in directors:
            own_id, name = people.loc[director, "officer_id"], baseline.normalise_name(people.loc[director, "name"])
            if (earlier["officer_id"] == own_id).any():
                links.add("same officer id")
            others = earlier[(earlier["officer_id"] != own_id) & (earlier["key"] == name) & (earlier["key"] != "")]
            if not others.empty:
                born = people_born[director]
                same_birth = pd.notna(born) and (others["born"] == born).fillna(False).any()
                links.add("same name and birth month and year" if same_birth else "same name only")
        found[query] = next((link for link in LINKS if link in links), "no predecessor")
    return pd.Series(found, name="link")


# --- The headline: which earlier records each method calls the same person -------------------

GROUPS = ["same name, not the matcher", "both", "the matcher only"]   # the hand check's groups
BANDS = ["rare", "medium", "common"]                                 # evaluate.name_commonness (#105)


def earlier_records(queries, mentions, claims):
    """Each query company's directors on record by its formation date, each paired with every
    record of a directorship at another company that started by that date, resigned ones
    included: the as-of rule of decide.candidate_matches (ADR-001).

    Returns one row per (company_id, director, record); director and record are mention ids.
    A company with no director on record by then has no rows.
    """
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    directorships = claims[claims["relation"] == "director_of"]
    rows = []
    for query in queries:
        edges = ev.observed_graph(directorships, as_of=pd.Timestamp(companies.loc[query, "incorporated_on"]))
        here = edges["object"] == companies.loc[query, "mention_id"]
        records = edges.loc[~here, "subject"].unique()
        for director in edges.loc[here, "subject"].unique():
            rows += [(query, director, record) for record in records]
    return pd.DataFrame(rows, columns=["company_id", "director", "record"])


def method_links(pairs, mentions, scored, threshold=0.5):
    """What each method says about each (director, record) pair of earlier_records, and whether
    the register confirms it. Keeps the pairs that at least one method links.

    - same name: the same name after baseline.normalise_name; an empty name never matches
    - officer links: the same officer id; an empty id never matches
    - matcher: blocking proposed the pair (it is in `scored`) and the matcher's p >= threshold
    register: "same officer id" (confirmed) when the officer ids match, else "different ids".
    p is the matcher's, empty for a pair blocking never proposed.
    """
    people = mentions[mentions["kind"] == "person"].set_index("mention_id")
    name = people["name"].map(baseline.normalise_name)
    officer = people["officer_id"].where(~ev.is_blank(people["officer_id"]))
    p_of = dict(zip(zip(scored["a"], scored["b"]), scored["p"]))   # blocking lists each pair once, a < b
    links = pairs.copy()
    d_name, r_name = name.loc[links["director"]].to_numpy(), name.loc[links["record"]].to_numpy()
    d_id, r_id = officer.loc[links["director"]].to_numpy(), officer.loc[links["record"]].to_numpy()
    links["same name"] = (d_name == r_name) & (d_name != "")
    links["officer links"] = pd.notna(d_id) & (d_id == r_id)
    links["p"] = [float(p_of.get(tuple(sorted(pair)), math.nan)) for pair in zip(links["director"], links["record"])]
    links["matcher"] = links["p"] >= threshold                    # an empty p is never >= threshold
    links["register"] = np.where(links["officer links"], "same officer id", "different ids")
    return links[links["same name"] | links["officer links"] | links["matcher"]].reset_index(drop=True)


def links_by_band(links, bands):
    """The headline counts, per name-commonness band of the director (bands: evaluate.name_commonness).

    For each method, the "different ids" links it makes. Then the "same officer id" links,
    every one of which is an officer link, and how many of them the matcher misses.
    """
    band = links["director"].map(bands)
    rows = {}
    for name in BANDS + ["all"]:
        part = links if name == "all" else links[band == name]
        unconfirmed = part[part["register"] == "different ids"]
        confirmed = part[part["register"] == "same officer id"]
        rows[name] = {
            "different ids: same name": int(unconfirmed["same name"].sum()),
            "different ids: officer links": int(unconfirmed["officer links"].sum()),
            "different ids: matcher": int(unconfirmed["matcher"].sum()),
            "same officer id": len(confirmed),
            "same officer id, missed by the matcher": int((~confirmed["matcher"]).sum()),
        }
    return pd.DataFrame(rows).T.rename_axis("band")


def pair_id(a, b):
    """The hand check's id for two records: the same in either order, and no name in it
    (a hash of the two mention ids, which are hashes themselves)."""
    return ev.make_id("handcheck", "|".join(sorted((a, b))))


def handcheck_sample(links, bands, n=50, seed=42):
    """n "different ids" pairs for the hand check, spread over GROUPS x BANDS.

    Groups: the same-name rule says yes and the matcher no; both say yes; only the matcher says
    yes. The pairs of each group x band cell are shuffled (seed); then the cells give one pair
    each in turn (group by group, bands rare to common), skipping empty cells, until n are
    taken. A pair met from both sides (two validation directors) is taken once.
    """
    unconfirmed = links[links["register"] == "different ids"].copy()
    unconfirmed["pair_id"] = [pair_id(a, b) for a, b in zip(unconfirmed["director"], unconfirmed["record"])]
    unconfirmed = unconfirmed.sort_values(["pair_id", "company_id", "director"]).drop_duplicates("pair_id")
    unconfirmed["band"] = unconfirmed["director"].map(bands)
    same, matcher = unconfirmed["same name"], unconfirmed["matcher"]
    unconfirmed["group"] = np.select([same & ~matcher, same & matcher, ~same & matcher], GROUPS, default="")
    rng = np.random.default_rng(seed)
    cells = []
    for group in GROUPS:
        for band in BANDS:
            cell = unconfirmed.index[(unconfirmed["group"] == group) & (unconfirmed["band"] == band)]
            cells.append(list(cell[rng.permutation(len(cell))]))
    picked = []
    while len(picked) < n and any(cells):
        for cell in cells:
            if cell and len(picked) < n:
                picked.append(cell.pop(0))
    columns = ["pair_id", "group", "band", "company_id", "director", "record", "p"]
    return unconfirmed.loc[picked, columns].reset_index(drop=True)


def postcode_area(district):
    """The postcode area: the letters a district starts with ("SW1A" gives "SW"). Empty if none."""
    if not isinstance(district, str):
        return ""
    found = re.match(r"[A-Za-z]+", district.strip())
    return found.group(0).upper() if found else ""


def birth_text(person):
    """Birth month and year as "04/1979", or "unknown"."""
    month = pd.to_numeric(person["birth_month"], errors="coerce")
    year = pd.to_numeric(person["birth_year"], errors="coerce")
    return "unknown" if pd.isna(month) or pd.isna(year) else f"{int(month):02d}/{int(year)}"


def handcheck_sheet(sample, mentions, claims):
    """What the hand check shows of each sampled pair, for both records: display name, birth
    month and year, nationality, postcode area, company name and formation date, appointment
    dates and the co-directors' display names.

    Display names only, never a director's name. Company names are real and can hold a
    person's name, so this table stays on the PC and never goes into git.
    """
    people = mentions[mentions["kind"] == "person"].set_index("mention_id")
    companies = mentions[mentions["kind"] == "company"].set_index("mention_id")
    directorships = claims[claims["relation"] == "director_of"]
    held = directorships.drop_duplicates("subject").set_index("subject")   # each record's company and dates
    rows = []
    for pair in sample.itertuples(index=False):
        for side, mention in [("validation director", pair.director), ("earlier record", pair.record)]:
            person, claim = people.loc[mention], held.loc[mention]
            company = companies.loc[claim["object"]]
            others = directorships.loc[(directorships["object"] == claim["object"])
                                       & (directorships["subject"] != mention), "subject"].unique()
            rows.append({
                "pair_id": pair.pair_id, "group": pair.group, "band": pair.band, "p": pair.p, "side": side,
                "display name": person["display_name"],
                "born": birth_text(person),
                "nationality": person["nationality"],
                "postcode area": postcode_area(person["display_postcode"]),
                "company": company["name"],
                "company formed": company["incorporated_on"],
                "appointed": claim["valid_from"],
                "resigned": claim["valid_to"],
                "co-directors": ", ".join(sorted(people.loc[others, "display_name"].fillna(""))),
            })
    return pd.DataFrame(rows)


def handcheck_html(sheet):
    """handcheck_sheet as one HTML page: a table per pair, the two records side by side."""
    fields = ["display name", "born", "nationality", "postcode area", "company", "company formed",
              "appointed", "resigned", "co-directors"]

    def text(value):
        return "" if value is None or (isinstance(value, float) and math.isnan(value)) else html.escape(str(value))

    parts = ["<!doctype html><meta charset='utf-8'><title>Hand check (#36)</title>",
             "<style>body{font-family:system-ui,sans-serif;margin:2em;max-width:70em}table{border-collapse:collapse;"
             "margin:0 0 2em;width:100%}td,th{border:1px solid #ccc;padding:.3em .6em;text-align:left;"
             "vertical-align:top}th{background:#f3f3f3;width:12em}</style>",
             "<h1>Hand check (#36): same person?</h1><p>Write yes, no or unsure next to each pair id in "
             "notebooks/jonas_handcheck.csv. This page holds real company names: it stays on this PC.</p>"]
    for number, (pair, rows) in enumerate(sheet.groupby("pair_id", sort=False), start=1):
        first = rows.iloc[0]
        p = "never proposed by blocking" if pd.isna(first["p"]) else f"{first['p']:.2f}"
        parts.append(f"<h2>{number}. {text(pair)}</h2><p>{text(first['group'])} | {text(first['band'])} name"
                     f" | matcher p: {p}</p><table><tr><th></th>"
                     + "".join(f"<th>{text(side)}</th>" for side in rows["side"]) + "</tr>")
        for field in fields:
            parts.append(f"<tr><th>{field}</th>" + "".join(f"<td>{text(value)}</td>" for value in rows[field]) + "</tr>")
        parts.append("</table>")
    return "\n".join(parts)
