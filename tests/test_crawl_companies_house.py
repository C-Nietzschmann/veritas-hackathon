"""Tests for the Companies House crawler (card #24). No network and no key.

FakeAPI stands in for crawl.get(): it answers from a dict of made-up records in the API's
shapes, with invented names and "TW" company numbers, like the tiny world. Every test
crawls into pytest's temporary folder, never into the real data/raw/.
"""

import json
from pathlib import Path

import pytest

from src import crawl_companies_house as crawl

# The real data folder, kept before the fixture below swaps it for a temporary one.
REAL_RAW_DIR = crawl.RAW_DIR


# --- A fake API and a small made-up world --------------------------------------------

class FakeAPI:
    """Answers like crawl.get(path, params): (200, bytes) for a record it has, else (404, ...).

    A name search is looked up as "/search/officers?q=<query>". Every request is kept in
    self.asked, so a test can check what was asked and what wasn't. fail_after and
    fail_on make it stop with an error, like a crash or a lost connection.
    """

    def __init__(self, records, fail_after=None, fail_on=None):
        self.records = records
        self.fail_after = fail_after
        self.fail_on = fail_on
        self.asked = []

    def __call__(self, path, params=None):
        key = f"{path}?q={params['q']}" if params and "q" in params else path
        if key == self.fail_on or (self.fail_after is not None and len(self.asked) >= self.fail_after):
            raise RuntimeError("the fake API stops here, like a crash")
        self.asked.append(key)
        if key not in self.records:
            return 404, b'{"error": "Not Found"}'
        return 200, json.dumps(self.records[key]).encode()


def profile(number, insolvent=False):
    return {"company_number": number, "company_name": f"{number} LTD", "has_insolvency_history": insolvent}


def officer(name, role, officer_id, born=None):
    """One entry of a company's officer list."""
    entry = {"name": name, "officer_role": role,
             "links": {"officer": {"appointments": f"/officers/{officer_id}/appointments"}}}
    if born:
        entry["date_of_birth"] = {"month": born[0], "year": born[1]}
    return entry


def appointments(*companies):
    """An officer's appointment list, from (company number, status) pairs."""
    return {"total_results": len(companies),
            "items": [{"appointed_to": {"company_number": number, "company_status": status}}
                      for number, status in companies]}


def search_result(title, officer_id):
    """One result of the officer name search. Like the real one, it has no birth date."""
    return {"title": title, "links": {"self": f"/officers/{officer_id}/appointments"}}


def world():
    """Two query companies formed in 2021, and the people and earlier companies around them.

    TW000010, never insolvent. Officers: Daniel HARROW (a director who is a person), a
      secretary and a corporate director (neither is followed). HARROW's own list holds
      TW000001 (insolvent) and TW000003 (never insolvent, still active). His name search
      finds himself, a second HARROW id with the same name words, a "Daniel James HARROW"
      and a "Danielle HARROWS". The second id was in TW000002 (in liquidation) and
      TW000004 (active).
    TW000011, dissolved after a liquidation. Its director LAMBERT has no other companies
      and no namesakes.
    """
    harrow = officer("HARROW, Daniel", "director", "harrow-1", born=(4, 1979))
    return {
        # The slice search: the same page answers for every month, which is enough here.
        "/advanced-search/companies": {"hits": 2, "items": [{"company_number": "TW000010"},
                                                            {"company_number": "TW000011"}]},
        "/company/TW000010": profile("TW000010"),
        "/company/TW000010/officers": {"total_results": 3, "items": [
            harrow,
            officer("OKAFOR, Ruth", "secretary", "okafor-1"),
            officer("INVENTED HOLDINGS LTD", "corporate-director", "invented-1"),
        ]},
        "/officers/harrow-1/appointments": appointments(
            ("TW000010", "active"), ("TW000001", "dissolved"), ("TW000003", "active")),
        "/company/TW000001": profile("TW000001", insolvent=True),
        "/company/TW000001/insolvency": {"cases": [{"type": "creditors-voluntary-liquidation"}]},
        "/company/TW000001/officers": {"total_results": 1, "items": [harrow]},
        "/company/TW000003": profile("TW000003"),
        "/search/officers?q=Daniel HARROW": {"items": [
            search_result("Daniel HARROW", "harrow-1"),        # the director himself
            search_result("Mr Daniel HARROW", "harrow-2"),     # same name words, another id
            search_result("Daniel James HARROW", "harrow-3"),  # one word more
            search_result("Danielle HARROWS", "harrows-1"),    # another name
        ]},
        "/officers/harrow-2/appointments": appointments(("TW000002", "liquidation"), ("TW000004", "active")),
        "/company/TW000002": profile("TW000002", insolvent=True),
        "/company/TW000002/insolvency": {"cases": [{"type": "compulsory-liquidation"}]},
        "/company/TW000002/officers": {"total_results": 1, "items": [
            officer("HARROW, Daniel", "director", "harrow-2", born=(4, 1979))]},
        "/company/TW000004": profile("TW000004"),
        "/company/TW000011": profile("TW000011", insolvent=True),
        "/company/TW000011/insolvency": {"cases": [{"type": "creditors-voluntary-liquidation"}]},
        "/company/TW000011/officers": {"total_results": 1, "items": [
            officer("LAMBERT, Priya", "director", "lambert-1", born=(3, 1985))]},
        "/officers/lambert-1/appointments": appointments(("TW000011", "dissolved")),
        "/search/officers?q=Priya LAMBERT": {"items": [search_result("Priya LAMBERT", "lambert-1")]},
    }


@pytest.fixture(autouse=True)
def raw_dir(tmp_path, monkeypatch):
    """Every test crawls into its own temporary folder."""
    monkeypatch.setattr(crawl, "RAW_DIR", tmp_path)
    return tmp_path


def run_crawl(monkeypatch, records=None, **fake_options):
    """Crawl the 2021 slice of the world (or other records) with a fake API. Returns the fake."""
    api = FakeAPI(records or world(), **fake_options)
    monkeypatch.setattr(crawl, "get", api)
    crawl.crawl(sample_size=None, years=[2021])
    return api


def saved(raw_dir, folder):
    """The names of the files saved in one folder, for example {"TW000010.json"}."""
    return {path.name for path in (raw_dir / folder).glob("*.json")}


# --- The files: where they land and what is in them ------------------------------------

def test_files_land_where_the_adapter_reads_them(monkeypatch, raw_dir):
    run_crawl(monkeypatch)
    assert saved(raw_dir, "company") == {"TW000010.json", "TW000011.json",
                                         "TW000001.json", "TW000002.json", "TW000003.json"}
    assert saved(raw_dir, "insolvency") == {"TW000011.json", "TW000001.json", "TW000002.json"}
    assert saved(raw_dir, "officers") == {"TW000010.json", "TW000011.json", "TW000001.json", "TW000002.json"}
    assert saved(raw_dir, "appointments") == {"harrow-1.json", "harrow-2.json", "lambert-1.json"}


def test_raw_answers_are_saved_byte_for_byte(monkeypatch, raw_dir):
    run_crawl(monkeypatch)
    sent = json.dumps(world()["/company/TW000010"]).encode()
    assert (raw_dir / "company" / "TW000010.json").read_bytes() == sent   # R1: untouched


def test_insolvency_only_when_flagged_and_officers_only_for_query_or_insolvent_companies(monkeypatch):
    api = run_crawl(monkeypatch)
    assert "/company/TW000010/insolvency" not in api.asked   # a query company, never insolvent
    assert "/company/TW000003/insolvency" not in api.asked   # an earlier company, never insolvent
    assert "/company/TW000003/officers" not in api.asked     # so its officers aren't needed
    assert "/company/TW000010/officers" in api.asked         # a query company's always are


def test_only_directors_who_are_people_are_followed(monkeypatch):
    api = run_crawl(monkeypatch)
    assert "/officers/okafor-1/appointments" not in api.asked     # a secretary
    assert "/officers/invented-1/appointments" not in api.asked   # a corporate director


# --- The name search (step 5) ---------------------------------------------------------

def test_name_words_ignore_order_case_punctuation_and_titles():
    assert crawl.name_words("HARROW, Daniel James") == {"DANIEL", "JAMES", "HARROW"}
    assert crawl.name_words("Mr Daniel James HARROW") == crawl.name_words("HARROW, Daniel James")
    assert crawl.name_words("O'BRIEN, Sean") == crawl.name_words("Sean OBRIEN")
    assert crawl.name_words("SMITH-JONES, Ann") == {"SMITH", "JONES", "ANN"}


def test_name_search_asks_forenames_first_and_keeps_same_name_words_with_another_id(monkeypatch):
    api = run_crawl(monkeypatch)
    assert "/search/officers?q=Daniel HARROW" in api.asked     # not "HARROW, Daniel"
    assert "/officers/harrow-2/appointments" in api.asked       # same words, another id
    assert "/officers/harrow-3/appointments" not in api.asked   # Daniel James HARROW
    assert "/officers/harrows-1/appointments" not in api.asked  # Danielle HARROWS


def test_a_candidates_active_companies_are_skipped(monkeypatch):
    api = run_crawl(monkeypatch)
    assert "/company/TW000002" in api.asked       # in liquidation: could be a predecessor
    assert "/company/TW000004" not in api.asked   # active: can't be
    assert "/company/TW000003" in api.asked       # the director's own list is followed in full


def test_at_most_20_candidates_per_director(monkeypatch):
    records = world()
    records["/search/officers?q=Daniel HARROW"] = {
        "items": [search_result("Daniel HARROW", f"harrow-x{k}") for k in range(25)]}
    api = run_crawl(monkeypatch, records)
    followed = [path for path in api.asked if path.startswith("/officers/harrow-x")]
    assert followed == [f"/officers/harrow-x{k}/appointments" for k in range(20)]   # the first 20


# --- Resuming and crashing --------------------------------------------------------------

def test_a_second_run_asks_nothing(monkeypatch):
    run_crawl(monkeypatch)
    again = run_crawl(monkeypatch)
    assert again.asked == []


def test_a_stopped_crawl_resumes_where_it_stopped(monkeypatch, raw_dir):
    with pytest.raises(RuntimeError):
        run_crawl(monkeypatch, fail_after=20)       # stops in the middle of a company
    done = raw_dir / crawl.DONE_FILE
    assert not done.exists() or len(done.read_text(encoding="utf-8").splitlines()) < 3   # not both listed
    second = run_crawl(monkeypatch)
    assert len(done.read_text(encoding="utf-8").splitlines()) == 3                       # now both are
    assert "/advanced-search/companies" not in second.asked   # saved before the stop, not asked again
    assert saved(raw_dir, "company") == {"TW000010.json", "TW000011.json",
                                         "TW000001.json", "TW000002.json", "TW000003.json"}
    assert saved(raw_dir, "insolvency") == {"TW000011.json", "TW000001.json", "TW000002.json"}


def test_a_profile_is_saved_only_after_its_insolvency_file(monkeypatch, raw_dir):
    # A profile on disk without its insolvency file would look like "never insolvent".
    with pytest.raises(RuntimeError):
        run_crawl(monkeypatch, fail_on="/company/TW000001/insolvency")
    assert not (raw_dir / "company" / "TW000001.json").exists()


def test_a_company_with_more_than_100_officers_is_flagged(monkeypatch):
    records = world()
    records["/company/TW000010/officers"]["total_results"] = 150
    run_crawl(monkeypatch, records)
    assert "TW000010" in crawl.flags["more than 100 officers"]


# --- The slice and the sample (#71) -----------------------------------------------------

def test_the_slice_is_asked_month_by_month_for_the_chosen_years_only(monkeypatch, raw_dir):
    run_crawl(monkeypatch)                     # years=[2021]
    assert len(list((raw_dir / "search" / "slice").glob("2021-*.json"))) == 12
    assert not list((raw_dir / "search" / "slice").glob("2022-*.json"))


def test_a_month_too_big_for_the_search_stops_loudly(monkeypatch):
    # The search can't page past 10,000 results, so such a month would be cut short in silence.
    monkeypatch.setattr(crawl, "get", FakeAPI({"/advanced-search/companies": {"hits": 10_000, "items": []}}))
    with pytest.raises(RuntimeError, match="10,000"):
        crawl.slice_numbers(2021)


def test_the_query_order_is_fixed_and_a_bigger_sample_contains_a_smaller_one(monkeypatch):
    numbers = [f"TW{k:06d}" for k in range(100, 130)]
    monkeypatch.setattr(crawl, "get", FakeAPI({"/advanced-search/companies": {
        "hits": 30, "items": [{"company_number": n} for n in numbers]}}))
    everything = crawl.query_companies(2021)
    assert sorted(everything) == numbers                                  # each company once
    assert everything != numbers                                          # shuffled
    assert crawl.query_companies(2021, sample_size=10) == everything[:10]  # same order, nested


def test_a_company_joining_the_slice_doesnt_move_the_others(monkeypatch, raw_dir):
    def order(numbers, folder):
        monkeypatch.setattr(crawl, "RAW_DIR", raw_dir / folder)
        monkeypatch.setattr(crawl, "get", FakeAPI({"/advanced-search/companies": {
            "hits": len(numbers), "items": [{"company_number": n} for n in numbers]}}))
        return crawl.query_companies(2021)

    numbers = [f"TW{k:06d}" for k in range(100, 130)]
    before = order(numbers, "first clone")
    after = order(numbers + ["TW999999"], "later clone")   # one more company in the register
    assert [n for n in after if n != "TW999999"] == before


def test_parts_split_the_companies_without_overlap():
    numbers = [f"TW{k:06d}" for k in range(10)]
    parts = [crawl.part_of(numbers, k, 3) for k in (1, 2, 3)]
    assert parts[0] == [numbers[0], numbers[3], numbers[6], numbers[9]]   # every 3rd, from the 1st
    assert sorted(sum(parts, [])) == numbers                               # together: each company once
    with pytest.raises(ValueError):
        crawl.part_of(numbers, 4, 3)


def test_a_part_crawls_only_its_companies_and_keeps_the_usual_gap(monkeypatch, raw_dir):
    monkeypatch.setattr(crawl, "spacing", crawl.SECONDS_BETWEEN_REQUESTS)   # put back after the test
    monkeypatch.setattr(crawl, "get", FakeAPI(world()))
    done = raw_dir / crawl.DONE_FILE
    crawl.crawl(sample_size=None, years=[2021], part=1, parts=2)
    assert len(done.read_text(encoding="utf-8").splitlines()) == 2             # 1 of the 2 query companies
    assert crawl.spacing == pytest.approx(crawl.SECONDS_BETWEEN_REQUESTS)      # each part has its own key
    crawl.crawl(sample_size=None, years=[2021], part=2, parts=2)
    assert len(done.read_text(encoding="utf-8").splitlines()) == 3             # now both, no overlap


def test_finished_query_companies_are_listed_and_earlier_companies_are_not(monkeypatch, raw_dir):
    run_crawl(monkeypatch)
    rows = (raw_dir / crawl.DONE_FILE).read_text(encoding="utf-8").splitlines()
    assert rows[0] == "year,company_number"
    assert sorted(rows[1:]) == ["2021,TW000010", "2021,TW000011"]   # not TW000001, TW000002 ...
    run_crawl(monkeypatch)                                           # a rerun adds no second line
    assert len((raw_dir / crawl.DONE_FILE).read_text(encoding="utf-8").splitlines()) == 3


# --- Talking to the API: the rate limit and the key --------------------------------------

class FakeClock:
    """Time that only moves when the code sleeps, so the rate test runs instantly."""

    def __init__(self):
        self.now = 1_000_000.0

    def monotonic(self):
        return self.now

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class FakeResponse:
    def __init__(self, status_code, headers=None, content=b"{}"):
        self.status_code = status_code
        self.headers = headers or {}
        self.content = content


def use_fake_clock(monkeypatch, key="test-key"):
    """Swap the clock for a FakeClock and the key for a test value. Returns the clock."""
    clock = FakeClock()
    for name in ("monotonic", "time", "sleep"):
        monkeypatch.setattr(crawl.time, name, getattr(clock, name))
    monkeypatch.setattr(crawl, "last_request", 0.0)
    monkeypatch.setattr(crawl, "spacing", crawl.SECONDS_BETWEEN_REQUESTS)
    monkeypatch.setattr(crawl, "api_key", lambda: key)
    return clock


def test_requests_are_spaced_and_a_429_is_waited_out(monkeypatch):
    clock = use_fake_clock(monkeypatch)
    window_ends = int(clock.now) + 120
    answers = [FakeResponse(200), FakeResponse(429, {"X-Ratelimit-Reset": str(window_ends)}), FakeResponse(200)]
    sent_at = []

    def fake_requests_get(url, **options):
        sent_at.append(clock.now)
        return answers.pop(0)

    monkeypatch.setattr(crawl.session, "get", fake_requests_get)
    crawl.get("/company/TW000001")
    status, _ = crawl.get("/company/TW000002")   # a 429 first, then 200
    assert status == 200
    assert sent_at[1] - sent_at[0] == pytest.approx(crawl.SECONDS_BETWEEN_REQUESTS)   # spaced
    assert sent_at[2] >= window_ends                                   # waited out the window


def test_a_refused_key_is_tried_again_then_stops_with_an_error_that_hides_the_key(monkeypatch):
    use_fake_clock(monkeypatch, key="secret-test-key")
    sent = []
    monkeypatch.setattr(crawl.session, "get", lambda url, **options: sent.append(url) or FakeResponse(401))
    with pytest.raises(RuntimeError, match="COMPANIES_HOUSE_API_KEY") as error:
        crawl.get("/company/TW000001")
    assert len(sent) == crawl.MAX_TRIES   # a 401 can be a passing glitch, so it is tried again
    assert "secret-test-key" not in str(error.value)


def test_a_403_stops_at_once(monkeypatch):
    # A 403 means too many requests from this computer, or a block: asking again makes it worse.
    use_fake_clock(monkeypatch)
    sent = []
    monkeypatch.setattr(crawl.session, "get", lambda url, **options: sent.append(url) or FakeResponse(403))
    with pytest.raises(RuntimeError, match="403"):
        crawl.get("/company/TW000001")
    assert len(sent) == 1


def test_a_broken_answer_is_never_saved(monkeypatch, raw_dir):
    use_fake_clock(monkeypatch)
    monkeypatch.setattr(crawl.session, "get", lambda url, **options: FakeResponse(200, content=b"<html>"))
    with pytest.raises(ValueError):
        crawl.fetch("company/TW000001.json", "/company/TW000001")
    assert not (raw_dir / "company" / "TW000001.json").exists()


def test_a_missing_key_says_which_name_to_set(monkeypatch, tmp_path):
    monkeypatch.delenv(crawl.KEY_NAME, raising=False)
    monkeypatch.setattr(crawl, "REPO_ROOT", tmp_path)   # a folder without a .env
    with pytest.raises(RuntimeError, match=crawl.KEY_NAME):
        crawl.api_key()


def test_raw_files_go_to_the_repos_data_folder_and_git_ignores_it_everywhere():
    repo = Path(crawl.__file__).resolve().parents[1]
    assert REAL_RAW_DIR == repo / "data" / "raw"
    assert "**/data/raw/" in (repo / ".gitignore").read_text(encoding="utf-8").splitlines()
