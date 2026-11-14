"""The three baselines (card #27): the bars our method has to beat.

Each baseline is a different answer to "is this the same person?", given in the same
shapes our method uses (ADR-005): a pairs table, then one decision per query company.
1. flag_nothing: never flags. The Finance brief's baseline for rare events.
2. same name: two directors with the same name are the same person. What someone does by hand.
3. officer links: only the links Companies House already makes, through the officer id.
   What a careful supplier sees on the register today. This is the only box that pairs
   people by officer id: in our matcher the officer id is the label, never a feature (ADR-003).

A query company is flagged when one of its directors is paired with someone who was a
director of a company that went insolvent in the window before the query company was formed.
- Only directorships count: `director_of` claims, never `controls` (a person with
  significant control is not a director).
- The window: an insolvency counts when it is on or before the formation date and at most
  `window_years` whole years before it, both days included. With 3 years, a company formed
  on 2021-04-20 counts insolvencies from 2018-04-20 to 2021-04-20.
- The as-of rule (ADR-001): only evidence dated on or before the formation date counts.

Baselines don't abstain and give no probabilities: every pair has p = 1, and every decision
is FLAG or CLEAR. A company with no director records is cleared too, but with its own reason,
so those cases can be counted. Reasons name companies by number only, never a person (masking).
Every table a function returns is checked against the shared schema first (ADR-005).
"""

import numbers
import re

import pandas as pd

from src import evidence as ev

# "Recently insolvent", from cards 27.2 and 27.3. The decision layer has no window yet (#34).
WINDOW_YEARS = 3

# Words left out when two names are compared.
TITLES = {"mr", "mrs", "ms", "miss", "mx", "dr", "sir", "dame", "lord", "lady", "prof", "rev"}

# How each baseline's reason says why two directors were taken as one person.
LINKED_BY = {"same_name": "has the same name as", "officer_links": "has the same officer id as"}


# --- 27.1 Flag nothing ------------------------------------------------------------------

def flag_nothing(queries):
    """Every company CLEAR: the rare-event baseline from the Finance brief."""
    rows = [decision(query, "flag_nothing", "CLEAR", "This baseline never flags.") for query in queries]
    return checked(pd.DataFrame(rows, columns=ev.DECISION_COLS), "decisions")


# --- 27.2 Same name means same person --------------------------------------------------

def normalise_name(name):
    """One comparable form of a name: "HARROW, Daniel" and "Mr Daniel Harrow" both give "daniel harrow".

    What is normalised (card #78), and nothing else:
    - Case: ignored.
    - Punctuation: any character that isn't a letter or a digit separates words, so
      "SMITH-JONES" reads as "smith jones" and "O'BRIEN" as "o brien".
    - Titles: the words in TITLES are dropped.
    - Order: the words are sorted, so the register's "SURNAME, Forenames" matches
      "Forenames Surname".
    Everything else counts as part of the name: every forename, middle names included, and
    accents. So "Daniel James Harrow" is not "Daniel Harrow", "Anna Smith-Jones" is not
    "Anna Jones", and "José" is not "Jose".
    """
    if not isinstance(name, str):
        return ""
    words = re.sub(r"[\W_]+", " ", name.lower()).split()
    return " ".join(sorted(word for word in words if word not in TITLES))


def same_name_pairs(mentions):
    """Every two people with the same normalised name, as pairs with p = 1."""
    people = mentions[mentions["kind"] == "person"]
    return pairs_by(people["mention_id"], people["name"].map(normalise_name), "same_name")


def same_name_flags(queries, mentions, claims, window_years=WINDOW_YEARS):
    """FLAG when a director has the same name as a director of a recently insolvent company."""
    return flags(queries, mentions, claims, same_name_pairs(mentions), "same_name", window_years)


# --- 27.3 Companies House officer links only -------------------------------------------

def officer_link_pairs(mentions):
    """Every two person records with the same officer id, as pairs with p = 1."""
    people = mentions[mentions["kind"] == "person"]
    return pairs_by(people["mention_id"], people["officer_id"], "officer_links")


def officer_link_flags(queries, mentions, claims, window_years=WINDOW_YEARS):
    """FLAG when a director's own officer id was also a director of a recently insolvent company."""
    return flags(queries, mentions, claims, officer_link_pairs(mentions), "officer_links", window_years)


def run_all(queries, mentions, claims, window_years=WINDOW_YEARS):
    """All three baselines in one decisions table, ready to score next to our method."""
    table = pd.concat([
        flag_nothing(queries),
        same_name_flags(queries, mentions, claims, window_years),
        officer_link_flags(queries, mentions, claims, window_years),
    ], ignore_index=True)
    return checked(table, "decisions")


# --- Shared by both linking baselines ---------------------------------------------------

def pairs_by(ids, keys, method):
    """Pairs of mention ids that share a key (a name or an officer id). An empty key never pairs."""
    table = pd.DataFrame({"id": ids.to_numpy(), "key": keys.to_numpy()})
    table = table[~ev.is_blank(table["key"])]
    both = table.merge(table, on="key")
    both = both[both["id_x"] < both["id_y"]]   # each pair once, and never a mention with itself
    pairs = pd.DataFrame({"a": both["id_x"], "b": both["id_y"], "p": 1.0,
                          "features": None, "method": method, "label": None}, columns=ev.PAIR_COLS)
    return checked(pairs.reset_index(drop=True), "pairs")


def flags(queries, mentions, claims, pairs, method, window_years):
    """One decision per query company: FLAG if `pairs` link one of its directors to a recently
    insolvent company, else CLEAR."""
    check_window(window_years)
    rows = []
    for query in queries:
        has_records, hit = first_hit(query, mentions, claims, pairs, window_years)
        if not has_records:
            verdict = "CLEAR"
            reason = f"No director records for {query}, so this baseline clears it anyway."
        elif hit is None:
            verdict = "CLEAR"
            reason = (f"No director of {query} {LINKED_BY[method]} a director of a company "
                      f"that went insolvent in the {window_years} years before it was formed.")
        else:
            earlier, insolvent_on = hit
            verdict = "FLAG"
            reason = (f"A director of {query} {LINKED_BY[method]} a director of {earlier}, "
                      f"which went insolvent on {insolvent_on}.")
        rows.append(decision(query, method, verdict, reason))
    return checked(pd.DataFrame(rows, columns=ev.DECISION_COLS), "decisions")


def first_hit(query, mentions, claims, pairs, window_years):
    """Look for an insolvent company that links the query company to a failure.

    Returns (has_records, hit). has_records is False when the company isn't in our data,
    has no formation date, or has no director on record by its formation date. hit is the
    earliest-failed such company as (company number, insolvency date), or None.

    Everything is seen as it stood on the day the query company was formed: directorships
    that started by then (observed_graph) and companies as they were then (mentions_as_of).
    """
    companies = mentions[mentions["kind"] == "company"]
    company = companies[companies["company_number"] == query]
    formed = ev.parse_dates(company["incorporated_on"]).min()
    if pd.isna(formed):
        return False, None
    edges = ev.observed_graph(claims, as_of=formed)
    edges = edges[edges["relation"] == "director_of"]   # directorships only, never "controls"
    view = ev.mentions_as_of(mentions, formed)

    # The query company's directors on the day it was formed.
    directors = set(edges.loc[edges["object"].isin(company["mention_id"]), "subject"])
    if not directors:
        return False, None

    # Companies that went insolvent in the window, both ends included.
    insolvent_on = ev.parse_dates(view["insolvency_on"])
    start = formed - pd.DateOffset(years=int(window_years))
    recent = view[(view["kind"] == "company") & (insolvent_on >= start) & (insolvent_on <= formed)]
    ran_recent = edges[edges["object"].isin(recent["mention_id"])]

    # The other side of every pair that has one of the query company's directors on one side.
    linked = set(pairs.loc[pairs["a"].isin(directors), "b"]) | set(pairs.loc[pairs["b"].isin(directors), "a"])
    hits = ran_recent[ran_recent["subject"].isin(linked)]
    if hits.empty:
        return True, None
    found = recent.set_index("mention_id").loc[hits["object"], ["company_number", "insolvency_on"]]
    first = found.sort_values("insolvency_on").iloc[0]   # ISO dates sort correctly as text
    return True, (first["company_number"], first["insolvency_on"])


def check_window(window_years):
    """The window is a whole number of years: a date can't be moved back by 2.5 years exactly."""
    if isinstance(window_years, bool) or not isinstance(window_years, numbers.Integral) or window_years < 0:
        raise ValueError(f"window_years must be a whole number of years, 0 or more, not {window_years!r}")


def checked(table, name):
    """Check a table against the shared schema before anyone reads it (ADR-005), then return it."""
    ev.check_columns(table, name)
    return table


def decision(query, method, verdict, reason):
    """One row of the decisions table. Baselines give no probabilities and nothing that would flip them."""
    return dict(query=query, method=method, decision=verdict, p_predecessor=None, p_fail=None,
                reason=reason, flip=None)
