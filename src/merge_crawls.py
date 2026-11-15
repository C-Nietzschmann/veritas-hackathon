"""Merge crawls from several computers into one data/raw/ (card #162).

Each of us crawled a different part on their own computer and zipped their whole data/raw/
(python -m zipfile -c raw_<handle>.zip data/raw). This puts those zips together in the
data/raw/ of the computer it runs on:

- A raw file is copied only when data/raw/ doesn't have it yet, byte for byte (R1), and only
  when it is valid JSON in one of the crawler's six folders. Nothing already there is changed
  or deleted, so of two crawls that fetched the same company the copy that came first stays.
- query_companies.csv gains the query companies it doesn't list yet.
- Running it again adds nothing, so a zip that arrives late is simply merged later.
- It reads straight out of each zip: nothing is unpacked anywhere else, and nothing is run.

From the repo root:  python -m src.merge_crawls <zip> [<zip> ...]
"""

import json
import re
import sys
import zipfile
from collections import Counter

from src import crawl_companies_house as crawl

FOLDERS = ["company", "insolvency", "officers", "appointments", "search/slice", "search/officers"]
RAW_FILE = re.compile(rf"^({'|'.join(FOLDERS)})/[A-Za-z0-9_-]+\.json$")   # no "..", no other folder
ROW = re.compile(r"^(\d{4}),([A-Za-z0-9]+)$")                              # a line of query_companies.csv


def merge_zip(zip_path):
    """Merge one zip into data/raw/. Returns (counts, the files that could not be read)."""
    counts, unreadable = Counter(), []
    with zipfile.ZipFile(zip_path) as z:
        # A zip made by old Windows tools writes its folders with backslashes.
        members = {info.filename.replace("\\", "/"): info for info in z.infolist() if not info.is_dir()}
        lists = sorted((name for name in members if name.split("/")[-1] == crawl.DONE_FILE), key=len)
        if not lists:
            raise ValueError(f"{zip_path} holds no {crawl.DONE_FILE}: is it a zip of data/raw?")
        top = lists[0][:-len(crawl.DONE_FILE)]        # "raw/", "data/raw/" or "": where the list sits
        for name, info in members.items():
            relpath = name[len(top):] if name.startswith(top) else ""
            if not RAW_FILE.match(relpath):
                continue                              # logs, the list, .tmp files, anything unexpected
            if (crawl.RAW_DIR / relpath).exists():
                counts["files already there"] += 1
                continue
            try:
                body = z.read(info)
                json.loads(body)
            except Exception as error:                # one damaged file must not stop the other 100,000
                unreadable.append(f"{relpath}: {type(error).__name__}")
                continue
            crawl.save(relpath, body)
            counts["files copied"] += 1
        rows = z.read(members[lists[0]]).decode("utf-8-sig").splitlines()

    listed = crawl.finished_companies()
    for row in rows:
        match = ROW.match(row.strip())                # the header and broken lines don't match
        if not match:
            continue
        year, number = match.groups()
        if number in listed:
            counts[f"query companies {year}, already listed"] += 1
        else:
            crawl.mark_finished(year, number)
            listed.add(number)
            counts[f"query companies {year}, new"] += 1
    return counts, unreadable


def main(zips):
    for zip_path in zips:
        counts, unreadable = merge_zip(zip_path)
        print(f"\n{zip_path}")
        for what, count in sorted(counts.items()):
            print(f"  {what}: {count:,}")
        print(f"  files that could not be read: {len(unreadable):,}", unreadable[:10])

    done = crawl.RAW_DIR / crawl.DONE_FILE
    rows = done.read_text(encoding="utf-8").splitlines()[1:] if done.exists() else []
    print("\ndata/raw/ now")
    print("  query companies per year:", dict(sorted(Counter(row.split(",")[0] for row in rows).items())))
    for folder in FOLDERS:
        print(f"  {folder}: {len(list((crawl.RAW_DIR / folder).glob('*.json'))):,} files")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
