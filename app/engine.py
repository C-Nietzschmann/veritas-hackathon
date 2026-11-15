"""The demo's engine (card #47): the notebook's pipeline, loaded once, asked one company at a time.

The web page (app/static/) asks app/server.py, and the server asks this file. It only calls src/,
read-only, so the page shows what main.ipynb computes. Company names and numbers never leave this
file: the page gets "This company" and "Earlier company 1" instead, and people their pseudonyms.

The first start loads the crawl and trains the matcher (a few minutes) and keeps the result in
data/engine.pkl, which git ignores. Without the crawl (a fresh clone) it uses the tiny world.
"""

import hashlib
import inspect
import math
import pickle
import sys
from pathlib import Path, PurePosixPath

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]   # the repo folder: this file is in app/
sys.path.insert(0, str(ROOT))                # so that `import src` works however the server is started

from src import baseline, decide, interface, real_slice, resolve   # noqa: E402
from src import evidence as ev                                    # noqa: E402
from src import ingest_companies_house as adapter                 # noqa: E402
from tests.tiny_world import tiny_world                           # noqa: E402

SEED = 42                                    # the notebook's seed
HAS_CRAWL = (ROOT / real_slice.DONE_FILE).exists()
CACHE = ROOT / "data" / "engine.pkl"         # git ignores data/
WARN_AT = 0.5                                # the Evaluation's bar, as in the notebook's Demo cell

# Copied from vault/Project/Evaluation.md, not recomputed: the test set is opened only once.
# "Final result" (main.ipynb @ 74d8a97): links to an earlier insolvent company, 2022 companies.
TEST = {"companies": 6847,
        "same name": {"unconfirmed": 1537, "common": 442, "recall": 0.980},
        "matcher": {"unconfirmed": 534, "common": 112, "recall": 0.918}}
# "A harder baseline and a stress test" (card #191): share of the register's own pairs still linked.
STRESS = [("Typo in the first name", 0.810, 0.026),
          ("Middle names dropped", 0.323, 0.296),
          ("Birth month one off", 0.000, 0.984)]

# The matcher's 8 numbers (resolve.FEATURE_COLS), in words.
WORDS = {"name_similarity": "Names alike", "name_missing": "A name missing",
         "birth_same": "Same birth month and year", "birth_missing": "A birth date missing",
         "postcode_same": "Same postcode district", "postcode_missing": "A postcode missing",
         "nationality_same": "Same nationality", "nationality_missing": "A nationality missing"}

# The code the page shows for each step: real functions from src/, read when the page asks.
CODE = {"crawl": adapter.officers_to_evidence, "register": decide.candidate_matches, "blocking": resolve.candidate_pairs,
        "features": resolve.pair_features, "matcher": resolve.train_matcher}


# --- 1. Load once: the notebook's Data and Model sections --------------------------------

def build():
    """The notebook's steps (main.ipynb cells 5, 11, 13 and 16), with the same seed."""
    if HAS_CRAWL:
        raw = adapter.load_raw()
        done = real_slice.query_companies()
        numbers = list(done.loc[done["year"] == "2021", "company_number"])
        test_numbers = set(done.loc[done["year"] == "2022", "company_number"])
        # Like the notebook: drop the 2022 companies' own files, so the demo never sees the test set
        raw = {path: data for path, data in raw.items()
               if not (PurePosixPath(path).parent.name in ("company", "insolvency", "officers")
                       and PurePosixPath(path).stem in test_numbers)}
        mentions, claims, labels, _ = real_slice.slice_from_raw(raw, numbers)
        crawled = len(done)
    else:
        mentions, claims, truth = tiny_world()
        labels = real_slice.make_labels(mentions, truth["queries"])
        crawled = len(labels)

    # The matcher learns from the pairs the register links itself (same officer id = same person),
    # only from companies formed by the end of the training period, as in the notebook.
    labelled = resolve.labelled_pairs(mentions)
    labelled["split"] = real_slice.pair_split(labelled, real_slice.person_split(mentions, claims, labels))
    in_time = real_slice.train_period_pairs(labelled, mentions, claims)
    train = labelled[(labelled["split"] == "train") & in_time].reset_index(drop=True)
    model = resolve.train_matcher(resolve.pair_features(train, mentions), train["label"], SEED)

    return {"mentions": mentions, "claims": claims, "labels": labels, "model": model, "crawled": crawled,
            "training_pairs": {"same": int((train["label"] == 1).sum()), "different": int((train["label"] == 0).sum())},
            "scored": resolve.scored_pairs(model, resolve.candidate_pairs(mentions), mentions),
            "same_name": baseline.same_name_pairs(mentions),
            "officer_links": baseline.officer_link_pairs(mentions)}


_DATA = None


def load():
    """Everything the engine needs. Built once, then read back from data/engine.pkl."""
    global _DATA
    if _DATA is None:
        if HAS_CRAWL and CACHE.exists():
            _DATA = pickle.loads(CACHE.read_bytes())
        else:
            _DATA = build()
            if HAS_CRAWL:
                CACHE.write_bytes(pickle.dumps(_DATA))
    return _DATA


# --- 2. Small helpers --------------------------------------------------------------------

def features(vias, mentions):
    """The matcher's 8 numbers (resolve.pair_features) for each pair of records in `vias`."""
    pairs = pd.DataFrame({"a": [via[0] for via in vias], "b": [via[1] for via in vias],
                          "p": None, "features": None, "method": None, "label": None})
    return resolve.pair_features(pairs, mentions)


def score(model, row):
    """The matcher's match score for one row of the 8 numbers: the same call the pipeline makes."""
    return float(resolve.match_probability(model, pd.DataFrame([row]))[0])


def compared(row):
    """The four fields of a pair in words, never the values themselves (birth dates are never shown)."""
    def field(name):
        return "missing" if row[f"{name}_missing"] else ("same" if row[f"{name}_same"] else "different")
    return [{"field": "Name", "verdict": f"{row['name_similarity']:.0%} alike"},
            {"field": "Born (month, year)", "verdict": field("birth")},
            {"field": "Postcode district", "verdict": field("postcode")},
            {"field": "Nationality", "verdict": field("nationality")}]


def source(ref, label):
    """Where a register fact came from, with the company's number hidden, and whether the raw
    file on disk still has the hash the fact was built from (R1)."""
    path, row, sha = ev.parse_record_ref(ref)
    file = ROOT / path
    verified = file.exists() and hashlib.sha256(file.read_bytes()).hexdigest() == sha
    return {"file": f"Companies House · {PurePosixPath(path).parent.name} of {label[0].lower() + label[1:]}", "row": row,
            "sha": sha[:12], "verified": verified}


# --- 3. One company, step by step --------------------------------------------------------

def company(number):
    """Everything the page shows for one company: the engine's steps, the evidence graph,
    the inspector behind every line, and the verdicts of the register and two simple rules."""
    data = load()
    mentions, claims, model = data["mentions"], data["claims"], data["model"]
    number = str(number).strip().upper()
    if number not in set(data["labels"]["company_id"]):
        return {"found": False}

    by_matcher, by_name, by_register = [decide.candidate_matches(number, mentions, claims, data[pairs])
                                        for pairs in ("scored", "same_name", "officer_links")]
    if by_matcher is None:    # no director on record by the day it was formed (R8)
        return {"found": True, "enough": False}

    # Step 1: the register as it stood on the day the company was formed (the as-of rule)
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    formed = companies.loc[number, "incorporated_on"]
    edges = ev.observed_graph(claims, as_of=formed)
    here = (edges["relation"] == "director_of") & (edges["object"] == companies.loc[number, "mention_id"])
    directors = list(dict.fromkeys(edges.loc[here, "subject"]))

    # Steps 2 and 3: the pairs blocking proposed for those directors, and the matcher's score for each
    scored = data["scored"]
    proposed = scored[scored["a"].isin(directors) | scored["b"].isin(directors)]
    scores = sorted((float(p) for p in proposed["p"]), reverse=True)

    # Step 4 and the answer: links to an earlier insolvent company, and the strongest one
    strongest = by_matcher.loc[by_matcher["p"].idxmax()] if len(by_matcher) else None
    warning = strongest is not None and strongest["p"] >= WARN_AT

    # The graph: the four strongest guesses. With no warning, the namesakes the same-name rule
    # flags, so the picture shows why the matcher stays quiet.
    shown = by_matcher.sort_values("p", ascending=False, kind="stable")
    namesakes = shown[shown["via"].isin(set(by_name["via"]))]
    shown = (namesakes if not warning and len(namesakes) else shown).head(4).reset_index(drop=True)

    names = {}   # mention id -> what the page may show
    names[companies.loc[number, "mention_id"]] = "This company"
    earlier_ids = companies.set_index("mention_id")
    for i, earlier in enumerate(dict.fromkeys(shown["predecessor"]), start=1):
        names[companies.loc[earlier, "mention_id"]] = f"Earlier company {i}"
    people = mentions[mentions["kind"] == "person"].set_index("mention_id")["display_name"]

    query_id, facts, guesses = interface.evidence(number, mentions, claims, shown)
    nodes, lines, inspect_ = {}, [], {}

    def node(mention_id, role):
        if mention_id not in nodes:
            is_company = role in ("query", "earlier")
            label = names.get(mention_id) or ("Company (hidden)" if is_company else people.get(mention_id)) \
                or "Person (name hidden)"
            entry = {"id": mention_id, "role": role, "label": label, "company": is_company}
            if role == "earlier":
                entry["insolvent"] = str(earlier_ids.loc[mention_id, "insolvency_on"])[:4]
            nodes[mention_id] = entry
        return mention_id

    for d in directors:
        node(d, "director")
    node(query_id, "query")
    for g in guesses:
        node(g["director"], "director")
        node(g["other"], "record")
        node(g["earlier"], "earlier")
    for i, fact in facts.iterrows():
        line_id = f"f{i}"
        lines.append({"id": line_id, "kind": "fact", "from": fact["subject"], "to": fact["object"]})
        inspect_[line_id] = {"kind": "fact", "says": "director of",
                             "source": source(fact["record_ref"], names.get(fact["object"], "a company"))}
    numbers = features([g["via"] for g in guesses], mentions) if guesses else pd.DataFrame()
    weights = resolve.matcher_weights(model)
    for i, g in enumerate(guesses):
        line_id = f"g{i}"
        row = numbers.iloc[i]
        parts = [{"feature": WORDS[f], "value": round(float(row[f]), 3), "weight": round(float(weights[f]), 2),
                  "product": round(float(row[f] * weights[f]), 2)} for f in resolve.FEATURE_COLS if abs(row[f]) > 0]
        off = row.copy()                              # what if the birth month were one off?
        off["birth_same"], off["birth_missing"] = 0.0, 0.0
        lines.append({"id": line_id, "kind": "guess", "from": g["director"], "to": g["other"],
                      "p": round(float(g["p"]), 3), "words": interface.in_words(g["p"])})
        inspect_[line_id] = {"kind": "guess", "p": round(float(g["p"]), 3), "words": interface.in_words(g["p"]),
                             "fields": compared(row), "parts": parts, "start": round(float(weights["intercept"]), 2),
                             "sum": round(float(weights["intercept"] + sum(row[f] * weights[f] for f in resolve.FEATURE_COLS)), 2),
                             "what_if": {"birth_month_off": round(score(model, off[resolve.FEATURE_COLS]), 3)
                                         if row["birth_same"] else None}}

    by_birth = by_name[features(list(by_name["via"]), mentions)["birth_same"].to_numpy() == 1] if len(by_name) else by_name
    return {
        "found": True, "enough": True, "formed": str(formed)[:4], "warning": bool(warning),
        "score": None if strongest is None else round(float(strongest["p"]), 3),
        "steps": [
            {"key": "register", "title": "Register", "value": len(directors),
             "unit": "director" if len(directors) == 1 else "directors", "note": "on record the day it was formed"},
            {"key": "blocking", "title": "Blocking", "value": len(proposed), "unit": "pairs",
             "note": f"proposed out of {int((mentions['kind'] == 'person').sum()):,} director records"},
            {"key": "matcher", "title": "Matcher", "value": round(scores[0], 2) if scores else 0, "unit": "top score",
             "note": f"{len(scores)} pairs scored, {sum(s >= WARN_AT for s in scores)} at {WARN_AT} or more",
             "scores": [round(s, 3) for s in scores[:24]]},
            {"key": "insolvent", "title": "Insolvent", "value": int(by_matcher["predecessor"].nunique()),
             "unit": "earlier company" if by_matcher["predecessor"].nunique() == 1 else "earlier companies",
             "note": "reached through a scored pair"},
            {"key": "answer", "title": "Answer", "value": "Warning" if warning else "No warning",
             "unit": "", "note": f"best match score {strongest['p']:.2f}" if strongest is not None else "no candidate"},
        ],
        "graph": {"nodes": list(nodes.values()), "lines": lines},
        "inspect": inspect_,
        "verdicts": [
            {"name": "The register's own links", "why": "The same officer id at Companies House", "alarm": len(by_register) > 0},
            {"name": "Same name", "why": "The usual check: an identical name", "alarm": len(by_name) > 0},
            {"name": "Same name and birth date", "why": "Identical name, same birth month and year", "alarm": len(by_birth) > 0},
            {"name": "Our matcher", "why": "Match score of 0.5 or more", "alarm": bool(warning), "ours": True},
        ],
    }


# --- 4. The whole pipeline, for the "How it works" view ------------------------------------

def overview():
    """The pipeline's own counts, the matcher's weights, and the test result."""
    data = load()
    mentions = data["mentions"]
    people = int((mentions["kind"] == "person").sum())
    weights = resolve.matcher_weights(data["model"])
    return {
        "crawled": data["crawled"], "companies": int((mentions["kind"] == "company").sum()), "facts": len(data["claims"]),
        "people": people, "possible": people * (people - 1) // 2, "candidates": len(data["scored"]),
        "training_pairs": data["training_pairs"], "labelled": len(data["labels"]),
        "weights": [{"feature": WORDS[f], "weight": round(float(weights[f]), 2)} for f in resolve.FEATURE_COLS],
        "intercept": round(float(weights["intercept"]), 2), "warn_at": WARN_AT, "test": TEST,
        "stress": [{"change": c, "matcher": m, "same_name": s} for c, m, s in STRESS],
    }


def code(name):
    """The real source of one pipeline step, read from src/ when the page asks."""
    function = CODE[name]
    lines, first = inspect.getsourcelines(function)
    return {"file": str(Path(inspect.getsourcefile(function)).relative_to(ROOT).as_posix()),
            "name": function.__name__, "line": first, "source": "".join(lines)}
