"""Guard: no real director's name may reach GitHub inside main.ipynb (card #112).

Run it before pushing the notebook (scripts/check.sh does this for you):
    .venv/bin/python scripts/name_guard.py

It reads every real name from the raw data on this computer (data/raw, never in git)
and searches everything saved in the notebook for them: the cells and their outputs.
Exit code 0 = no real name found, 1 = found one (the lines say where).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "main.ipynb"
RAW_DIR = ROOT / "data" / "raw"


def clean(text):
    """Lower case, with every run of spaces and line breaks made one space."""
    return " ".join(str(text).split()).casefold()


def name_forms(name):
    """The ways a name can be written. The register writes "HARROW, Daniel"; a sentence says "Daniel Harrow"."""
    name = clean(name)
    forms = {name}
    if "," in name:
        surname, given = name.split(",", 1)
        forms.add(clean(given + " " + surname))
    return forms


def notebook_texts(notebook_path):
    """Every piece of text saved in the notebook, as (cell number, text). Images are skipped."""
    notebook = json.loads(Path(notebook_path).read_text(encoding="utf-8"))
    texts = []
    for number, cell in enumerate(notebook["cells"], start=1):
        texts.append((number, "".join(cell.get("source", []))))
        for output in cell.get("outputs", []):
            if "text" in output:                                   # printed text
                texts.append((number, "".join(output["text"])))
            for kind, value in output.get("data", {}).items():     # tables, values, html
                if kind.startswith("text/"):
                    texts.append((number, "".join(value)))
    return texts


def find_names(notebook_path, names):
    """Return (cell number, name) for every real name found in the notebook."""
    found = []
    for number, text in notebook_texts(notebook_path):
        text = clean(text)
        for name in names:
            if not re.search(r"[^\W\d_]", name):
                continue   # a "name" with no letter (the register has one written ".") would match punctuation
            for form in name_forms(name):
                # \b = a word edge, so "jo lee" is not found inside "jo leeds"
                if re.search(r"\b" + re.escape(form) + r"\b", text):
                    found.append((number, name))
                    break
    return found


def real_names(mentions):
    """The names of person mentions that are not safe to show.

    The tiny world's names are invented, so there display_name equals name and they are skipped.
    """
    people = mentions[mentions["kind"] == "person"]
    unsafe = people[people["name"] != people["display_name"]]
    return sorted(set(unsafe["name"].dropna()))


def main():
    if not RAW_DIR.is_dir():
        print("name guard: no raw data on this computer, so there are no real names to look for.")
        return 0
    # Imported here, so the guard still runs (and skips) where pandas isn't installed.
    sys.path.insert(0, str(ROOT))
    from src import ingest_companies_house as ingest

    mentions, _ = ingest.officers_to_evidence(ingest.load_raw())
    found = find_names(NOTEBOOK, real_names(mentions))
    for number, name in found:
        print(f"  x real name in notebooks/main.ipynb, cell {number}: {name}. Show display_name instead")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
