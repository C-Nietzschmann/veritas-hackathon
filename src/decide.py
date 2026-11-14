"""The decision layer (card #34): FLAG, CLEAR or NOT ENOUGH EVIDENCE, with the reason.

For one query company, step by step (ADR-004):
1. candidate_matches: its directors on the day it was formed, and the pairs that may
   make one of them the same person as someone who ran an insolvent earlier company.
2. p_predecessor: the chance that at least one of those matches is right.
3. p_fail: a straight line turns that into the chance the company fails (#33).
4. thresholds and decide: the three costs say when to flag, when to clear, and when
   to ask instead.

Only this box turns probabilities into actions (R4). Like every box, it imports
nothing from src/ but the shared schema (ADR-005).
"""

import math

import numpy as np
import pandas as pd

from src import evidence as ev

# The decisions' method name: 1 − ∏(1 − p), the MVP formula of ADR-004.
METHOD = "formula"


def candidate_matches(query, mentions, claims, pairs):
    """The query company's candidate matches with an insolvent earlier company, as links rows.

    `query` is a company number; `pairs` is one method's pairs table. Returns None when
    there is nothing to judge: the company isn't in our data, or no director of it is
    on record by its formation date. An empty table is different news: we had directors
    to check and none of them matches anyone who ran an insolvent company (R8).

    As-of rule (ADR-001): only what is dated on or before the formation date t counts.
    An appointment counts if it started by t, and an earlier company only if it was
    insolvent by t. A company with no formation date gets no edges at all, so it ends
    as "nothing to judge" instead of seeing the future.
    """
    companies = mentions[mentions["kind"] == "company"]
    company = companies[companies["company_number"] == query]
    if company.empty:
        return None
    formed = ev.parse_dates(company["incorporated_on"]).iloc[0]
    edges = ev.observed_graph(claims, as_of=formed)

    at_query = edges[edges["object"].isin(company["mention_id"])]
    if at_query.empty:
        return None

    insolvent = companies[ev.parse_dates(companies["insolvency_on"]) <= formed]
    at_insolvent = edges[edges["object"].isin(insolvent["mention_id"])]

    # A pair has no direction: the query's director can be its a or its b. So list every
    # pair both ways round, then keep the rows where `director` runs the query company
    # and `other` ran an insolvent one.
    both_ways = pd.concat([
        pairs.assign(director=pairs["a"], other=pairs["b"]),
        pairs.assign(director=pairs["b"], other=pairs["a"]),
    ])
    directors = at_query.rename(columns={"subject": "director", "claim_id": "claim_at_query"})
    earlier = at_insolvent.rename(columns={"subject": "other", "object": "earlier", "claim_id": "claim_at_earlier"})
    hits = (both_ways.merge(directors[["director", "claim_at_query"]], on="director")
                     .merge(earlier[["other", "earlier", "claim_at_earlier"]], on="other"))

    number = companies.set_index("mention_id")["company_number"]
    links = pd.DataFrame({
        "query": query,
        "predecessor": hits["earlier"].map(number),
        # The pair the link rests on, sorted so that (a, b) and (b, a) are the same pair.
        "via": [tuple(sorted(pair)) for pair in zip(hits["a"], hits["b"])],
        "p": hits["p"],
        "method": hits["method"],                   # whoever made the pair made the link's p
        "depends_on": [[at_q, at_e] for at_q, at_e in zip(hits["claim_at_query"], hits["claim_at_earlier"])],
    }, columns=ev.LINK_COLS)
    # A copied claim states the same appointment again (R5), and a pairs table may list
    # one pair both ways round: either way it is still one link.
    return links.drop_duplicates(["via", "predecessor"], ignore_index=True)


def p_predecessor(ps):
    """The chance that at least one candidate match is right: 1 − (1 − p1)(1 − p2)...

    This assumes the matches are independent: whether one is right tells us nothing
    about another. It isn't quite true, because a director is only one person, and two
    records of one earlier person count twice here. Sunday's one-identity rule (#32,
    ADR-004) fixes that. No matches gives 0.
    """
    return float(1 - math.prod(1 - p for p in ps))


def company_p_predecessor(matches):
    """P(predecessor) for one company, from what candidate_matches gave. None when there
    was nothing to judge.

    One match can lead to several insolvent companies; it is still one chance of being right.
    """
    if matches is None:
        return None
    return p_predecessor(matches.drop_duplicates("via")["p"])


def fit_failure_line(p_predecessors, failed):
    """33.1: the straight line from P(predecessor) to the failure rate, as (rate_without, rate_with).

    p_predecessors: one P(predecessor) per training company. failed: True or False for the
    same companies, in the same order. Training companies only, never validation or test.

    The line is the least-squares fit: the straight line closest to the points. Its left
    end, at P(predecessor) = 0, is the failure rate without an insolvent predecessor; its
    right end, at 1, is the rate with one. A rate can't be below 0 or above 1, so each end
    is cut to that range. A company with no P(predecessor) (no director records) is left out.
    It stays a straight line so that averaging over possible worlds stays exact (#32, ADR-004).
    """
    points = pd.DataFrame({"p": pd.to_numeric(pd.Series(list(p_predecessors)), errors="coerce"),
                           "failed": pd.Series(list(failed)).astype(float)}).dropna()
    if points["p"].nunique() < 2:
        raise ValueError("the failure line needs companies with at least two different values of "
                         "P(predecessor): with one value there is no line to fit")
    slope, rate_without = np.polyfit(points["p"], points["failed"], 1)
    rate_with = rate_without + slope
    return float(np.clip(rate_without, 0, 1)), float(np.clip(rate_with, 0, 1))


def p_fail(p_pred, line):
    """The chance the company fails, read off the straight line of #33 (card #93).

    line = (rate_without, rate_with): the failure rates of training companies without
    and with an insolvent predecessor. P(predecessor) slides us between the two.
    """
    rate_without, rate_with = line
    return rate_without + p_pred * (rate_with - rate_without)


def thresholds(cost_miss, cost_wrong_flag, cost_ask):
    """Chow's rule (1970, ADR-004): clear at or below clear_below, flag at or above flag_above.

    With P(fail) = p, clearing costs p × cost_miss on average, flagging costs
    (1 − p) × cost_wrong_flag, and asking always costs cost_ask. Clearing beats asking
    while p ≤ cost_ask / cost_miss; flagging beats asking once p ≥ 1 − cost_ask / cost_wrong_flag.
    Costs 10, 2, 1 give (0.1, 0.5).
    """
    clear_below = cost_ask / cost_miss
    flag_above = 1 - cost_ask / cost_wrong_flag
    if clear_below > flag_above:
        # Asking costs more than it could ever save, so never ask: clear or flag, whichever
        # is cheaper. They cost the same where p × cost_miss = (1 − p) × cost_wrong_flag.
        clear_below = flag_above = cost_wrong_flag / (cost_miss + cost_wrong_flag)
    return clear_below, flag_above


def decide(query, matches, line, costs):
    """FLAG, CLEAR or NOT ENOUGH EVIDENCE for one company, as one row of the decisions table.

    matches: what candidate_matches gave for this query (None means nothing to judge).
    line: (rate_without, rate_with), see p_fail. costs: (cost_miss, cost_wrong_flag, cost_ask).
    The reason names companies by number only, never a person (masking).
    """
    if matches is None:
        # R8: no records is not good news. Abstain, and give no number we don't have.
        return dict(query=query, method=METHOD, decision="NOT ENOUGH EVIDENCE",
                    p_predecessor=None, p_fail=None,
                    reason=f"We have no director records for {query}, so we can't judge it.", flip=None)

    p_pred = company_p_predecessor(matches)
    chance = p_fail(p_pred, line)
    clear_below, flag_above = thresholds(*costs)
    if chance <= clear_below:
        decision, verdict = "CLEAR", "low enough to clear"
    elif chance >= flag_above:
        decision, verdict = "FLAG", "high enough to flag"
    else:
        decision, verdict = "NOT ENOUGH EVIDENCE", "too close to call, so check it by hand"

    if matches.empty:
        evidence = f"No director of {query} matches anyone who ran a company that went insolvent before it was formed"
    else:
        best = matches.loc[matches["p"].idxmax()]
        evidence = (f"{query} may share a director with {best['predecessor']}, an earlier company that "
                    f"went insolvent ({best['p']:.0%} sure it's the same person)")
    return dict(query=query, method=METHOD, decision=decision, p_predecessor=p_pred, p_fail=chance,
                reason=f"{evidence}: its {chance:.0%} chance of failing within two years is {verdict}.",
                flip=None)   # what would flip it comes with #37
