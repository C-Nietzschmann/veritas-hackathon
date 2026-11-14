"""The shared evidence schema: the six tables every box reads and writes.

Every box imports this file and nothing else from src/ (ADR-005), so the boxes
never depend on each other. The tables and their columns are listed in
vault/Project/Modules.md. Change a table only on a call: bump SCHEMA_VERSION
and update Modules in the same push.

Conventions:
- Dates are ISO strings, YYYY-MM-DD.
- Ids are short hashes of the source's own keys, so a rerun gives the same ids (R7).
- company_id, query and predecessor are company numbers.
- a, b, subject and object are mention ids.
"""

import hashlib

import pandas as pd

SCHEMA_VERSION = 1


# --- 22.1 The columns ----------------------------------------------------------

# Where every mention and claim row came from (ADR-001, R2).
PROVENANCE_COLS = ["source", "record_ref", "origin", "adapter"]

# One row per entity as one record describes it. Mentions are not entities:
# two records of the same person stay two rows (ADR-001, R6).
MENTION_COLS = [
    "mention_id", "kind",
    "name", "display_name",          # display_name: masked; the only name an output may show
    # companies, as the register writes them
    "company_number", "status", "incorporated_on", "dissolved_on", "insolvency_on", "sic_code",
    # people, as the register writes them
    "birth_month", "birth_year",     # never displayed, so they get no display column
    "nationality",
    "officer_id",                    # the matcher's label only, never a feature (ADR-003)
    # both
    "postcode", "display_postcode",  # display_postcode: the district only
] + PROVENANCE_COLS

# One row per relationship a source states between two mentions.
CLAIM_COLS = [
    "claim_id", "subject", "relation", "object",
    "valid_from", "valid_to",        # when the source says it started and ended; either may be empty
] + PROVENANCE_COLS

# The other four shared tables. Their own boxes decide what goes in them;
# this file only fixes the column names, so every box speaks the same language.
LABEL_COLS = ["company_id", "formed_on", "failed", "split"]
PAIR_COLS = ["a", "b", "p", "features", "method", "label"]
LINK_COLS = ["query", "predecessor", "via", "p", "method", "depends_on"]
DECISION_COLS = ["query", "method", "decision", "p_predecessor", "p_fail", "reason", "flip"]

TABLES = {
    "mentions": MENTION_COLS,
    "claims": CLAIM_COLS,
    "labels": LABEL_COLS,
    "pairs": PAIR_COLS,
    "links": LINK_COLS,
    "decisions": DECISION_COLS,
}

# Allowed values.
KINDS = {"company", "person"}
RELATIONS = {"director_of", "controls"}
SPLITS = {"train", "validation", "test"}
DECISIONS = {"FLAG", "CLEAR", "NOT ENOUGH EVIDENCE"}


class SchemaError(ValueError):
    """A table broke the shared schema. The message names the row and the rule."""


def empty_table(name):
    """An empty table with the right columns, for example empty_table("pairs")."""
    return pd.DataFrame(columns=TABLES[name])


def empty_mentions():
    return empty_table("mentions")


def empty_claims():
    return empty_table("claims")


def check_columns(table, name):
    """Raise if a table is missing any of its schema columns. Extra columns are fine."""
    missing = [col for col in TABLES[name] if col not in table.columns]
    if missing:
        raise SchemaError(f"{name}: missing columns {missing} (schema v{SCHEMA_VERSION})")


# --- 22.2 Stable ids and record_ref --------------------------------------------

def make_id(source, key):
    """A short, stable id: the same source and key always give the same id (R7).

    `key` is the source's own key for the record, such as a company number or an
    appointment link. Never a counter: a counter changes when the input order does.
    """
    return hashlib.sha256(f"{source}|{key}".encode("utf-8")).hexdigest()[:16]


def record_ref(raw_path, row, raw_bytes):
    """Where a row came from: the raw file, the row in it, and the sha256 of the
    raw response, for example "data/raw/abc.json#0@9f2c...".

    Keeping the hash in every row replaces a separate manifest (R1).
    """
    sha = hashlib.sha256(raw_bytes).hexdigest()
    return f"{raw_path}#{row}@{sha}"


def parse_record_ref(ref):
    """Split a record_ref back into (raw_path, row, sha256)."""
    path_and_row, sha = ref.rsplit("@", 1)
    path, row = path_and_row.rsplit("#", 1)
    return path, int(row), sha


def raw_unchanged(ref, raw_bytes):
    """R1: True if the raw response still has the hash its rows were built from."""
    return parse_record_ref(ref)[2] == hashlib.sha256(raw_bytes).hexdigest()


# --- 22.3 Row checks -------------------------------------------------------------

def is_blank(column):
    """True where a cell is missing or holds only spaces."""
    return column.isna() | column.astype("string").str.strip().eq("").fillna(False)


def parse_dates(column):
    """Read a column of ISO dates (YYYY-MM-DD). Anything else, empty cells included,
    becomes NaT, pandas' "not a time"."""
    return pd.to_datetime(column.astype("string"), format="%Y-%m-%d", errors="coerce")


# What record_ref() builds: file, row number, sha256.
RECORD_REF_SHAPE = r".+#\d+@[0-9a-f]{64}"


def check_rows(mentions, claims):
    """Stop bad rows at the door.

    Raises SchemaError listing every problem, each with the row's id and the rule
    it breaks. Returns None when all rows are fine.
    """
    check_columns(mentions, "mentions")
    check_columns(claims, "claims")
    problems = []
    tables = [("mentions", mentions, "mention_id"), ("claims", claims, "claim_id")]

    # R2: every row says where it came from, in the shape the R1 check can read back.
    for name, table, id_col in tables:
        for col in ("source", "record_ref"):
            for row_id in table.loc[is_blank(table[col]), id_col]:
                problems.append(f"{name} row {row_id}: empty {col} (R2: every row needs its provenance)")
        well_formed = table["record_ref"].astype("string").str.fullmatch(RECORD_REF_SHAPE).fillna(False)
        for row_id in table.loc[~well_formed & ~is_blank(table["record_ref"]), id_col]:
            problems.append(f"{name} row {row_id}: record_ref is not file#row@sha256 (R1: build it with record_ref())")

    # Every row has an id, and ids are unique, so a claim points at exactly one mention.
    for name, table, id_col in tables:
        blank = int(is_blank(table[id_col]).sum())
        if blank:
            problems.append(f"{name}: {blank} row(s) with an empty {id_col} (every row needs an id)")
        for row_id in table.loc[table[id_col].duplicated(), id_col].unique():
            problems.append(f"{name} row {row_id}: duplicate {id_col} (ids must be unique)")

    # Only the kinds and relations the schema knows.
    unknown = mentions.loc[~mentions["kind"].isin(KINDS)]
    for row_id, kind in zip(unknown["mention_id"], unknown["kind"]):
        problems.append(f"mentions row {row_id}: unknown kind {kind!r} (allowed: {sorted(KINDS)})")
    unknown = claims.loc[~claims["relation"].isin(RELATIONS)]
    for row_id, relation in zip(unknown["claim_id"], unknown["relation"]):
        problems.append(f"claims row {row_id}: unknown relation {relation!r} (allowed: {sorted(RELATIONS)})")

    # Every claim connects two mentions that exist.
    for end in ("subject", "object"):
        dangling = claims.loc[~claims[end].isin(mentions["mention_id"])]
        for row_id, value in zip(dangling["claim_id"], dangling[end]):
            problems.append(f"claims row {row_id}: {end} {value!r} is not a mention (claims connect mentions)")

    # Both relations end at a company: someone is a director of, or controls, a company.
    # This catches a claim written the wrong way round.
    company_ids = mentions.loc[mentions["kind"] == "company", "mention_id"]
    is_mention = claims["object"].isin(mentions["mention_id"])
    wrong_end = claims.loc[is_mention & ~claims["object"].isin(company_ids)]
    for row_id, relation in zip(wrong_end["claim_id"], wrong_end["relation"]):
        problems.append(f"claims row {row_id}: the object of {relation} must be a company (subject and object swapped?)")

    # A date is ISO or empty. One we can't read would silently drop out of every as-of filter.
    start = parse_dates(claims["valid_from"])
    stop = parse_dates(claims["valid_to"])
    for col, parsed in (("valid_from", start), ("valid_to", stop)):
        unreadable = claims.loc[parsed.isna() & ~is_blank(claims[col])]
        for row_id, value in zip(unreadable["claim_id"], unreadable[col]):
            problems.append(f"claims row {row_id}: {col} {value!r} is not a date like 2021-05-01 (dates)")

    # The same for the company dates: the label and the as-of rule run on them.
    for col in ("incorporated_on", "dissolved_on", "insolvency_on"):
        unreadable = mentions.loc[parse_dates(mentions[col]).isna() & ~is_blank(mentions[col])]
        for row_id, value in zip(unreadable["mention_id"], unreadable[col]):
            problems.append(f"mentions row {row_id}: {col} {value!r} is not a date like 2021-05-01 (dates)")

    # A relationship can't end before it starts.
    for row_id in claims.loc[stop < start, "claim_id"]:
        problems.append(f"claims row {row_id}: valid_to is before valid_from (dates)")

    if problems:
        more = f"\n... and {len(problems) - 20} more" if len(problems) > 20 else ""
        raise SchemaError(f"{len(problems)} bad row(s):\n" + "\n".join(problems[:20]) + more)


# --- 22.4 The observed graph -------------------------------------------------------

EDGE_COLS = ["claim_id", "subject", "relation", "object", "valid_from", "valid_to", "source", "record_ref"]


def observed_graph(claims, as_of=None):
    """The observed graph: one edge per stated claim, each carrying its claim_id,
    so every edge is one click from its source (R3, ADR-002). Nothing else writes
    to it; inferred links live in the links table.

    as_of keeps only claims that started on or before that date (the as-of rule,
    ADR-001). A claim with no start date is dropped then, because we can't show
    it existed by that date. An end date after as_of is emptied: on that date the
    relationship was still running, and its end was still the future.
    """
    check_columns(claims, "claims")
    stated = ~is_blank(claims["source"]) & ~is_blank(claims["record_ref"])
    edges = claims.loc[stated, EDGE_COLS]
    if as_of is not None:
        as_of = pd.Timestamp(as_of)
        start = parse_dates(edges["valid_from"])
        edges = edges.loc[start.notna() & (start <= as_of)].copy()
        edges.loc[parse_dates(edges["valid_to"]) > as_of, "valid_to"] = None
    return edges.reset_index(drop=True)


# --- #121 The companies as of a date ------------------------------------------------

def mentions_as_of(mentions, as_of):
    """The mentions as they stood on as_of: the as-of rule for companies (ADR-001).

    A crawl made today also shows what happened to a company after as_of. So this
    drops the companies formed after that date and hides dissolution and insolvency
    dates after it. It empties status, which is as of the crawl day: code reads
    the dates instead. People's mentions all stay, because their claims carry the
    dates and observed_graph(claims, as_of) filters those.
    """
    check_columns(mentions, "mentions")
    as_of = pd.Timestamp(as_of)
    is_company = mentions["kind"] == "company"
    formed_later = is_company & (parse_dates(mentions["incorporated_on"]) > as_of)
    view = mentions.loc[~formed_later].copy()
    for col in ("dissolved_on", "insolvency_on"):
        view.loc[parse_dates(view[col]) > as_of, col] = None
    view.loc[view["kind"] == "company", "status"] = None
    return view.reset_index(drop=True)
