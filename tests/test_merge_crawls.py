"""Test for merging crawl zips (card #162). No network, no key, and only made-up files.

It merges into pytest's temporary folder, never into the real data/raw/.
"""

import zipfile

import pytest

from src import crawl_companies_house as crawl
from src import merge_crawls as merge


@pytest.fixture(autouse=True)
def raw_dir(tmp_path, monkeypatch):
    """The test merges into its own temporary folder."""
    monkeypatch.setattr(crawl, "RAW_DIR", tmp_path / "raw")
    return tmp_path / "raw"


def make_zip(path, files):
    with zipfile.ZipFile(path, "w") as z:
        for name, body in files.items():
            z.writestr(name, body)
    return path


def test_merge_keeps_what_is_there_adds_what_is_new_and_leaves_junk_out(tmp_path, raw_dir):
    crawl.save("company/TW000001.json", b'{"from": "mine"}')
    crawl.mark_finished(2021, "TW000001")
    one = make_zip(tmp_path / "one.zip", {                      # like python -m zipfile -c: raw/...
        "raw/company/TW000001.json": '{"from": "theirs"}',      # the same company: mine must stay
        "raw/company/TW000002.json": '{"from": "theirs"}',
        "raw/insolvency/TW000002.json": "{}",
        "raw/search/officers/-x_Y.json": "{}",
        "raw/company/TW000003.json": '{"cut off',               # not JSON
        "raw/company/TW000004.json.tmp": "{}",                  # a half-written file
        "raw/company/../../evil.json": "{}",                    # tries to leave the folder
        "raw/crawl.log": "a log",
        "raw/query_companies.csv": "year,company_number\r\n2021,TW000001\r\n2022,TW000002\r\n",   # Windows line ends
    })
    two = make_zip(tmp_path / "two.zip", {                      # backslashes, and data\raw\...
        "data\\raw\\officers\\TW000005.json": "{}",
        "data\\raw\\query_companies.csv": "year,company_number\n2022,TW000002\n2021,TW000005\n",
    })

    for _ in range(2):                                          # the second round must add nothing
        counts, unreadable = merge.merge_zip(one)
        merge.merge_zip(two)
    merge.main([one, two])                                      # the report runs too, and adds nothing

    files = sorted(path.relative_to(raw_dir).as_posix() for path in raw_dir.rglob("*") if path.is_file())
    assert files == ["company/TW000001.json", "company/TW000002.json", "insolvency/TW000002.json",
                     "officers/TW000005.json", "query_companies.csv", "search/officers/-x_Y.json"]
    assert (raw_dir / "company" / "TW000001.json").read_bytes() == b'{"from": "mine"}'
    assert (raw_dir / "query_companies.csv").read_text(encoding="utf-8").splitlines() == [
        "year,company_number", "2021,TW000001", "2022,TW000002", "2021,TW000005"]
    assert not (tmp_path / "evil.json").exists()
    assert counts["files copied"] == 0 and counts["files already there"] == 4
    assert unreadable == ["company/TW000003.json: JSONDecodeError"]
