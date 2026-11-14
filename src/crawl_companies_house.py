"""The Companies House crawler (card #24): raw API answers into data/raw/, untouched.

It only downloads. The adapter (src/ingest_companies_house.py, #25) turns the files into
mentions and claims, and the two meet only through this layout (ADR-005). Every path is
relative to RAW_DIR, the repo's data/raw/ folder, which git ignores:

    company/{number}.json             GET /company/{number}, the profile
    insolvency/{number}.json          GET /company/{number}/insolvency, only when the profile
                                      says has_insolvency_history
    officers/{number}.json            GET /company/{number}/officers, 100 per page, one page
    appointments/{officer_id}.json    GET /officers/{officer_id}/appointments, 50 per page, one page
    search/slice/{month}_{start}.json the advanced search that lists the slice (#71)
    search/officers/{officer_id}.json the name search for one query director

The two search folders sit one level deeper on purpose: the adapter's load_raw reads every
data/raw/*/*.json, and these pages are big and not evidence.

For each query company the crawl fetches:
1. the company's own files: profile, insolvency file if flagged, officers (#72);
2. for each director who is a person, their appointment list and every company in it:
   profile, insolvency file if flagged, officers if insolvent (#73);
3. a name search for that director, and for up to 20 officers with exactly the same name
   words but another officer id, their appointment list and every company in it that isn't
   active. Without this, a phoenix under a new officer id can't be reached (comment on #24).

A file already on disk is never asked for again, so a stopped crawl resumes where it stopped.
query_companies.csv lists the query companies crawled in full: downstream takes its companies
from there, never from all the company files (they hold the earlier companies too).

Run one crawl at a time, with one key: two crawls on one key would pass the limit, and
Companies House doesn't allow several keys for one application.
From the repo root:  python -m src.crawl_companies_house [sample size | all] [years ...]
"""

import calendar
import hashlib
import json
import os
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"     # the same folder wherever the code runs from

API = "https://api.company-information.service.gov.uk"
KEY_NAME = "COMPANIES_HOUSE_API_KEY"     # read from .env, never printed

# The limit is 600 requests per 5 minutes. 300 s / 0.55 s = 545 requests, safely under it.
SECONDS_BETWEEN_REQUESTS = 0.55
MAX_TRIES = 6                # a request that keeps failing stops the crawl; run it again to resume
SECONDS_AFTER_ERROR = 30     # the first pause after an error; it doubles with every try

# The run settings: which years to crawl, in this order, and how many query companies per year.
YEARS = (2021, 2022)         # 2021 (train and validation) first, then 2022 (test); (2021,) crawls one year
SAMPLE_SIZE = 25             # query companies per year for the fresh-run test; None means all

# The slice (#71): construction, SIC 2007 divisions 41-43, companies formed in the YEARS above.
SIC_CODES = [
    "41100", "41201", "41202",                                               # 41 buildings
    "42110", "42120", "42130", "42210", "42220", "42910", "42990",           # 42 civil engineering
    "43110", "43120", "43130", "43210", "43220", "43290", "43310", "43320",  # 43 specialised work
    "43330", "43341", "43342", "43390", "43910", "43991", "43999",
]
SEARCH_PAGE = 5000           # the most the advanced search returns per page
SEARCH_LIMIT = 10_000        # it can't page past this many results (start_index 10,000 is a server error)

SEED = 42                    # the order of the query companies
DONE_FILE = "query_companies.csv"   # in RAW_DIR: the query companies crawled in full, with their year

DIRECTOR_ROLES = {"director", "nominee-director"}   # directors who are people, as the adapter keeps them (#75)
MAX_CANDIDATES = 20          # same-name officers followed per director (decided on #24)
TITLES = {"MR", "MRS", "MS", "MISS", "DR", "SIR", "PROF", "REV", "LADY", "LORD", "DAME"}

stats = Counter()            # requests made, for card #24
flags = defaultdict(set)     # what to report: companies and officers the crawl couldn't take in full
last_request = 0.0           # when the last request started (time.monotonic), for the spacing


# --- Talking to the API -----------------------------------------------------------------

def api_key():
    """The key from .env at the repo root. Never printed."""
    load_dotenv(REPO_ROOT / ".env")
    key = os.environ.get(KEY_NAME, "").strip()
    if not key:
        raise RuntimeError(f"{KEY_NAME} is not set: put it in .env at the repo root (the name is in .env.example)")
    return key


def seconds_until_reset(answer):
    """How long to wait after a 429: until the time in the X-Ratelimit-Reset header
    (seconds since 1970) plus one second, or a whole 5-minute window if it's missing."""
    reset = answer.headers.get("X-Ratelimit-Reset", "")
    if reset.isdigit():
        return max(1, int(reset) - time.time() + 1)
    return 300


def get(path, params=None):
    """Ask the API for one path. Returns (status, body bytes) for a 200 or a 404.

    Starts at most one request every SECONDS_BETWEEN_REQUESTS, retries included, so the crawl
    stays under the rate limit. A 429 (too many requests) is waited out, then asked again.
    No answer, a server error or a 401 is tried again, waiting longer each time. A 403 or
    any other answer stops the crawl.
    """
    global last_request
    for attempt in range(1, MAX_TRIES + 1):
        wait = last_request + SECONDS_BETWEEN_REQUESTS - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        last_request = time.monotonic()
        stats["requests"] += 1
        try:
            answer = requests.get(API + path, params=params, auth=(api_key(), ""), timeout=60)
            status = answer.status_code
        except requests.RequestException:             # no answer at all: network down, timeout
            status = None
        if status in (200, 404):
            return status, answer.content
        if status == 429:                             # over the limit: wait for the window to reset
            print("  rate limit reached, waiting for the window to reset")
            time.sleep(seconds_until_reset(answer))
            continue
        if status == 403:                             # retrying would make a ban worse
            raise RuntimeError("The API answered 403: too many requests from this computer, or access "
                               "is blocked. Wait at least an hour before running again.")
        if status is not None and status != 401 and status < 500:
            raise RuntimeError(f"{path}: the API answered {status}")
        # No answer, a server error, or a 401 (the API has refused good keys for a moment):
        # try again after 30 s, then 1, 2, 4 and 8 minutes.
        if attempt == MAX_TRIES:
            break
        pause = SECONDS_AFTER_ERROR * 2 ** (attempt - 1)
        print(f"  {path}: {'no answer' if status is None else f'error {status}'}, "
              f"try {attempt} of {MAX_TRIES}, next in {pause} s")
        time.sleep(pause)
    raise RuntimeError(f"{path}: no usable answer after {MAX_TRIES} tries. "
                       f"If they were 401s, the API refused the key in {KEY_NAME}: check .env")


# --- Raw files ----------------------------------------------------------------------------

def save(relpath, body):
    """Write a raw answer byte for byte (R1), through a .tmp file: a run killed in the
    middle of writing leaves no half file that the next run would take as done."""
    path = RAW_DIR / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(body)
    for _ in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:      # Windows: a virus scanner can hold a new file for a moment
            time.sleep(0.5)
    os.replace(tmp, path)            # a last try, which stops with the error if the file is still held


def fetch(relpath, api_path, params=None):
    """One raw file, parsed: read from disk if it is there, else asked for and saved.
    None if the API has no such record (404); nothing is saved then."""
    path = RAW_DIR / relpath
    if path.exists():
        return json.loads(path.read_bytes())
    status, body = get(api_path, params)
    if status == 404:
        return None
    parsed = json.loads(body)        # before saving: a broken answer stops here, not on disk
    save(relpath, body)
    return parsed


# --- Companies and officers (#72, #73) -----------------------------------------------------

def fetch_company(number, with_officers):
    """A company's files: the profile, the insolvency file if the profile says
    has_insolvency_history, and the officer list if with_officers or the company is insolvent.

    The profile is saved after its insolvency file. So a profile on disk always has its
    insolvency file next to it, and the adapter can't take a missing download for "never insolvent".
    """
    profile_path = RAW_DIR / "company" / f"{number}.json"
    if profile_path.exists():
        body = profile_path.read_bytes()
    else:
        status, body = get(f"/company/{number}")
        if status == 404:
            flags["company not found"].add(number)
            return
    insolvent = json.loads(body).get("has_insolvency_history", False)
    if insolvent and fetch(f"insolvency/{number}.json", f"/company/{number}/insolvency") is None:
        flags["flagged insolvent, no insolvency record"].add(number)
    if not profile_path.exists():
        save(f"company/{number}.json", body)
    if with_officers or insolvent:
        officers = fetch(f"officers/{number}.json", f"/company/{number}/officers", {"items_per_page": 100})
        if officers and officers.get("total_results", 0) > 100:
            flags["more than 100 officers"].add(number)


def officer_id(link):
    """The officer id in a link like "/officers/{id}/appointments"."""
    return link.split("/")[2]


def directors(number):
    """The directors who are people in a company's saved officer list, as the adapter keeps
    them (#75). Secretaries and corporate directors are skipped."""
    path = RAW_DIR / "officers" / f"{number}.json"
    if not path.exists():
        return []
    items = json.loads(path.read_bytes()).get("items", [])
    return [officer for officer in items if officer.get("officer_role") in DIRECTOR_ROLES]


def follow_officer(officer, skip_active=False):
    """An officer's appointment list, and the companies in it (#73).

    skip_active is for the name-search candidates: a company their list shows as "active"
    can't be an insolvent predecessor, so it isn't fetched (decided on #24).
    """
    appointments = fetch(f"appointments/{officer}.json", f"/officers/{officer}/appointments",
                         {"items_per_page": 50})
    if appointments is None:
        return
    if appointments.get("total_results", 0) > 50:
        flags["more than 50 appointments"].add(officer)
    for item in appointments.get("items", []):
        company = item.get("appointed_to", {})
        number = company.get("company_number")
        if not number:
            continue
        if skip_active and company.get("company_status") == "active":
            flags["active, skipped (name search)"].add(number)
            continue
        fetch_company(number, with_officers=False)


# --- The name search ------------------------------------------------------------------------

def name_words(name):
    """The words of a name in capitals, ignoring order, punctuation and titles:
    "SMITH, John Paul" and "Mr John Paul SMITH" both give {"JOHN", "PAUL", "SMITH"}."""
    words = re.findall(r"[^\W\d_]+", name.upper().replace("'", "").replace("’", ""))
    return {word for word in words if word not in TITLES}


def candidates(director):
    """Up to MAX_CANDIDATES other officer ids with exactly the director's name words.

    The search is asked "Forenames Surname": asked the way the register writes names,
    "SURNAME, Forenames", it doesn't even find the director. Its results carry no birth
    dates, so the name is all they can be filtered on (decided on #24).
    """
    own = officer_id(director["links"]["officer"]["appointments"])
    surname, _, forenames = director["name"].partition(",")
    query = f"{forenames.strip()} {surname.strip()}".strip()
    results = fetch(f"search/officers/{own}.json", "/search/officers", {"q": query, "items_per_page": 100})
    wanted = name_words(director["name"])
    found = []
    for item in (results or {}).get("items", []):
        other = officer_id(item["links"]["self"])
        if other != own and other not in found and name_words(item.get("title", "")) == wanted:
            found.append(other)
    if len(found) > MAX_CANDIDATES:
        flags["more than 20 same-name officers"].add(own)
    return found[:MAX_CANDIDATES]


# --- The slice and the query companies (#71) ---------------------------------------------

def slice_numbers(year):
    """The company numbers of the slice formed in `year`: SIC 41-43, any status, dissolved included.

    Asked one month at a time, because the advanced search can't page past 10,000 results.
    Every answer page is saved raw, so a rerun reads the same list back.
    """
    numbers = set()
    for month in range(1, 13):
        first = f"{year}-{month:02d}-01"
        last = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        start = 0
        while True:
            page = fetch(f"search/slice/{first[:7]}_{start}.json", "/advanced-search/companies", {
                "sic_codes": ",".join(SIC_CODES), "incorporated_from": first, "incorporated_to": last,
                "size": SEARCH_PAGE, "start_index": start}) or {}
            hits = page.get("hits", 0)
            if hits >= SEARCH_LIMIT:
                raise RuntimeError(f"{first[:7]} has {hits:,} companies, but the search can't page "
                                   f"past 10,000: split the month")
            numbers.update(item["company_number"] for item in page.get("items", []))
            start += SEARCH_PAGE
            if start >= hits:
                break
    return sorted(numbers)


def query_companies(year, sample_size=None):
    """The slice's companies formed in `year`, in a fixed order that looks random.

    Each company's place comes from a hash of SEED and its own number, as in evidence.make_id.
    So a crawl stopped early still holds a fair sample of the year; the sample is the first
    sample_size of them, and a bigger sample contains every smaller one. A company keeps its
    place when another joins or leaves the list, as can happen on a fresh clone months later.
    """
    numbers = slice_numbers(year)
    numbers.sort(key=lambda number: hashlib.sha256(f"{SEED}|{number}".encode("utf-8")).hexdigest())
    return numbers if sample_size is None else numbers[:sample_size]


def finished_companies():
    """The query companies crawled in full so far, read from DONE_FILE."""
    path = RAW_DIR / DONE_FILE
    if not path.exists():
        return set()
    rows = path.read_text(encoding="utf-8").splitlines()[1:]   # skip the header
    return {row.split(",")[1] for row in rows}


def mark_finished(year, number):
    """Add one query company to DONE_FILE, once its crawl is complete."""
    path = RAW_DIR / DONE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("year,company_number\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as done:
        done.write(f"{year},{number}\n")


# --- The crawl --------------------------------------------------------------------------

def crawl_company(number):
    """Everything for one query company: its files, then for each director who is a person
    their own appointments and their same-name officers."""
    fetch_company(number, with_officers=True)
    for director in directors(number):
        follow_officer(officer_id(director["links"]["officer"]["appointments"]))
        for other in candidates(director):
            follow_officer(other, skip_active=True)


def crawl(sample_size=SAMPLE_SIZE, years=YEARS):
    """Crawl sample_size query companies per year (None: all of them), the years in order.

    Prints a progress line every 100 companies, and returns the counts for card #24.
    """
    stats.clear()
    flags.clear()
    started = time.monotonic()
    finished = finished_companies()
    per_company = []                     # the requests each query company took
    for year in years:
        numbers = query_companies(year, sample_size)
        year_started = time.monotonic()
        print(f"{year}: {len(numbers):,} query companies")
        for done, number in enumerate(numbers, start=1):
            before = stats["requests"]
            crawl_company(number)
            per_company.append(stats["requests"] - before)
            if number not in finished:
                mark_finished(year, number)
                finished.add(number)
            if done % 100 == 0 or done == len(numbers):
                minutes = (time.monotonic() - year_started) / 60
                left = minutes / done * (len(numbers) - done)
                print(f"{year}: {done:,} of {len(numbers):,} companies, {stats['requests']:,} requests, "
                      f"{minutes:.0f} min so far, about {left:.0f} min to go")
    return summary(per_company, started)


def summary(per_company, started):
    """The counts for card #24: requests, time, files on disk, and what was flagged."""
    skipped = [number for number in flags["active, skipped (name search)"]
               if not (RAW_DIR / "company" / f"{number}.json").exists()]
    return {
        "query companies": len(per_company),
        "requests": stats["requests"],
        "minutes": round((time.monotonic() - started) / 60, 1),
        "requests per query company": {
            "mean": round(statistics.mean(per_company), 1) if per_company else 0,
            "median": statistics.median(per_company) if per_company else 0,
            "max": max(per_company, default=0),
        },
        "requests saved by skipping active companies (at least)": len(skipped),
        "files": {folder: len(list((RAW_DIR / folder).glob("*.json")))
                  for folder in ("company", "insolvency", "officers", "appointments")},
        "flags": {name: len(found) for name, found in flags.items()},
    }


if __name__ == "__main__":
    # python -m src.crawl_companies_house             SAMPLE_SIZE per year, 2021 then 2022
    # python -m src.crawl_companies_house all         the whole slice, 2021 then 2022
    # python -m src.crawl_companies_house 500 2021    500 companies of 2021
    size = sys.argv[1] if len(sys.argv) > 1 else str(SAMPLE_SIZE)
    years = [int(year) for year in sys.argv[2:]] or list(YEARS)
    print(json.dumps(crawl(None if size == "all" else int(size), years), indent=2))
